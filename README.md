# Automated File Submission, Validation and Failure Recovery Pipeline Using AWS

## Abstract

The Automated File Submission, Validation and Failure Recovery Pipeline Using AWS is a serverless cloud computing project designed to automate the submission and validation of digital assignment files.

The system uses Amazon S3 to store uploaded files and trigger AWS Lambda functions for automatic processing. The Lambda function validates the submission path, file extension, and file size according to predefined rules.

The results of processed submissions are stored in Amazon DynamoDB for tracking and record keeping. Amazon Simple Email Service (SES) sends rejection notifications when files fail validation. Amazon CloudWatch monitors Lambda execution errors and evaluates configured alarms, while Amazon Simple Notification Service (SNS) delivers email alerts to the administrator. Amazon Simple Queue Service (SQS) is configured as a dead-letter queue to retain failed asynchronous Lambda events for investigation.

AWS Identity and Access Management (IAM) provides permissions for communication between the services.

Testing demonstrated successful processing of a valid PDF upload, storage of its submission record, and delivery of an administrator notification following an intentional Lambda failure.

The project demonstrates event-driven serverless architecture, automated validation, centralized submission records, monitoring, and failure handling using managed AWS services. It provides a foundation for a more comprehensive cloud-based assignment management system.

## Objectives

- Automate assignment file submission and processing.
- Validate file paths, extensions, and sizes.
- Store submission records in a database.
- Notify users when files fail validation.
- Monitor processing errors and send administrator alerts.
- Retain failed asynchronous events for investigation.

## AWS Services Used

| AWS Service | Purpose |
|---|---|
| Amazon S3 | Stores uploaded assignment files and triggers processing events. |
| AWS Lambda | Validates and processes uploaded files. |
| Amazon DynamoDB | Stores submission records and processing status. |
| Amazon SES | Sends rejection emails. |
| Amazon SQS | Retains failed events through a dead-letter queue. |
| Amazon CloudWatch | Monitors execution logs, errors, and alarms. |
| Amazon SNS | Sends administrator alerts through subscriptions. |
| AWS IAM | Manages permissions between AWS services. |

## System Workflow

1. A user uploads an assignment file to Amazon S3.
2. The S3 event triggers an AWS Lambda function.
3. Lambda checks the file path, extension, and size against predefined validation rules.
4. Submission details and processing results are recorded in DynamoDB.
5. If validation fails, Amazon SES sends a rejection notification.
6. CloudWatch monitors Lambda execution and evaluates configured alarms.
7. When an administrator alert condition is met, SNS sends a notification to its subscribers.
8. Failed asynchronous Lambda events can be retained in an SQS dead-letter queue for investigation.

## Testing and Results

- Successfully processed a valid PDF upload.
- Verified storage of the submission record in DynamoDB.
- Tested Lambda failure handling using an intentional execution failure.
- Verified administrator email notification through SNS.
- Configured monitoring and a dead-letter queue for failure investigation.

## Key Concepts Demonstrated

- Serverless computing
- Event-driven architecture
- Automated file validation
- Database integration
- Email notifications and alerting
- Cloud monitoring
- Failure handling and recovery

## Keywords

AWS, Serverless Computing, AWS Lambda, Amazon S3, Amazon DynamoDB, Amazon SES, Amazon SQS, Amazon CloudWatch, Amazon SNS, AWS IAM, Failure Monitoring.
