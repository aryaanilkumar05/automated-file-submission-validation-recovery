
import json
import urllib.parse
import logging
import boto3
import hashlib
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Allowed file formats and maximum size
ALLOWED_EXTENSIONS = (".pdf", ".doc", ".docx", ".txt")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MiB

EXPECTED_BUCKET = "cloudsubmit-assignment"
SENDER_EMAIL = "your-verified-sender@example.com"
TABLE_NAME = "CloudSubmitSubmissions"

# AWS service clients in Mumbai
ses = boto3.client("ses", region_name="ap-south-1")
dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table(TABLE_NAME)


def save_submission(
    bucket, key, filename, recipient, size,
    status, reason, processed_at, record
):
    # Create a repeatable ID so retries update the same record
    event_time = record.get("eventTime", "")
    sequencer = record.get("s3", {}).get("object", {}).get(
        "sequencer", ""
    )
    unique_source = f"{bucket}|{key}|{event_time}|{sequencer}"
    submission_id = hashlib.sha256(
        unique_source.encode("utf-8")
    ).hexdigest()

    item = {
        "submissionId": submission_id,
        "bucket": bucket,
        "s3Key": key,
        "fileName": filename,
        "recipient": recipient or "UNKNOWN",
        "sizeBytes": int(size),
        "status": status,
        "reason": reason,
        "processedAt": processed_at
    }

    table.put_item(Item=item)
    logger.info("Saved submission to DynamoDB: %s", submission_id)


def send_rejection_email(recipient, filename, reason):
    ses.send_email(
        Source=SENDER_EMAIL,
        Destination={"ToAddresses": [recipient]},
        Message={
            "Subject": {
                "Data": "CloudSubmit: Assignment Rejected"
            },
            "Body": {
                "Text": {
                    "Data": (
                        f"Hello,\n\n"
                        f"Your uploaded file '{filename}' "
                        f"could not be accepted.\n\n"
                        f"Reason: {reason}\n\n"
                        f"Allowed formats: PDF, DOC, DOCX, TXT.\n"
                        f"Maximum file size: 10 MiB.\n\n"
                        f"Please upload a corrected file.\n\n"
                        f"Regards,\nCloudSubmit"
                    )
                }
            }
        }
    )


def lambda_handler(event, context):
    logger.info("CloudSubmit processing started")
    results = []

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )
        size = record["s3"]["object"].get("size", 0)

        if bucket != EXPECTED_BUCKET:
            raise ValueError("Unexpected S3 bucket")

        processed_at = datetime.now(timezone.utc).isoformat()

        # Expected S3 path: email-address/filename
        parts = key.split("/", 1)

        if len(parts) != 2 or not parts[0] or not parts[1]:
            status = "REJECTED"
            reason = "Use an email-address folder."
            filename = key
            recipient = ""

            save_submission(
                bucket, key, filename, recipient, size,
                status, reason, processed_at, record
            )

            result = {
                "file": filename,
                "status": status,
                "reason": reason
            }
            logger.info("Processing result: %s", json.dumps(result))
            results.append(result)
            continue

        recipient = parts[0]
        filename = parts[1]

        # Basic email format check
        if (
            "@" not in recipient
            or "." not in recipient.split("@")[-1]
            or any(char.isspace() for char in recipient)
        ):
            status = "REJECTED"
            reason = "Invalid email address in folder name."

            save_submission(
                bucket, key, filename, recipient, size,
                status, reason, processed_at, record
            )

            result = {
                "file": filename,
                "status": status,
                "reason": reason
            }
            logger.info("Processing result: %s", json.dumps(result))
            results.append(result)
            continue

        reasons = []

        if not filename.lower().endswith(ALLOWED_EXTENSIONS):
            reasons.append(
                "Unsupported file format. "
                "Allowed formats are PDF, DOC, DOCX and TXT."
            )

        if not (0 < size <= MAX_FILE_SIZE):
            reasons.append(
                "File must be larger than 0 bytes and no bigger than 10 MiB."
            )

        status = "ACCEPTED" if not reasons else "REJECTED"
        reason = "; ".join(reasons) if reasons else "Validation passed."

        result = {
            "file": filename,
            "recipient": recipient,
            "size_bytes": size,
            "processed_at": processed_at,
            "status": status,
            "reason": reason
        }

        logger.info("Processing result: %s", json.dumps(result))

        # Save both accepted and rejected results
        save_submission(
            bucket, key, filename, recipient, size,
            status, reason, processed_at, record
        )

        # Send email only for rejected files with a valid email folder
        if reasons:
            try:
                send_rejection_email(recipient, filename, reason)
                logger.info("Rejection email sent to %s", recipient)
            except Exception:
                logger.exception("Failed to send rejection email")
                raise

        results.append(result)

    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }
