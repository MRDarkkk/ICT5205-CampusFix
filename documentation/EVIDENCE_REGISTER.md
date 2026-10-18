# CampusFix — AWS Implementation and Testing Evidence Register

**ICT5205 Assignment 3 — CampusFix Smart Campus Maintenance System**

**Project status:** AWS deployment completed and core application functionality verified.

**Deployment region:** Asia Pacific (Sydney), `ap-southeast-2`

**Live application:** https://dy5mpxcnbr23i.cloudfront.net

**GitHub repository:** https://github.com/MRDarkkk/ICT5205-CampusFix

## 1. Evidence Register

| ID | Evidence requirement | Verification outcome | Status |
|---|---|---|---|
| E01 | CloudFormation deployment | CampusFix stack reached CREATE_COMPLETE | Verified |
| E02 | HTTPS frontend and S3 website hosting | CampusFix website accessible through CloudFront over HTTPS; private S3 origin configured | Verified |
| E03 | API Gateway and Lambda integration | Six HTTP API routes configured and integrated with Lambda | Verified |
| E04 | Lambda and IAM configuration | API and notification-worker functions deployed; IAM role configuration reviewed | Verified |
| E05 | DynamoDB persistence | Two active tables observed and maintenance issue record checked | Verified |
| E06 | Issue submission and tracking | Maintenance issue created successfully and unique tracking ID returned | Verified |
| E07 | Private photo handling | Presigned upload and authorised photograph retrieval successfully exercised | Verified |
| E08 | Cognito and protected API | Staff authentication and protected administrative endpoint checks completed | Verified |
| E09 | Issue status lifecycle | Open, In Progress and Resolved workflow tested using the staff dashboard | Verified |
| E10 | SQS notification architecture | Main queue, worker integration and dead-letter queue configured | Configuration verified; failure recovery not tested |
| E11 | SNS email notifications | Actual maintenance notification email received from SNS | Verified |
| E12 | CloudWatch monitoring | Notification-worker execution and successful publishing observed in logs | Logs verified; load/performance benchmarking not completed |
| E13 | API validation and error handling | Invalid request and nonexistent issue checks returned expected 400 and 404 responses | Verified |
| E14 | AWS budget monitoring | AWS budget and cost-alert configuration captured | Configuration verified; actual spending not assessed |

## 2. Screenshot Evidence

The following screenshots are stored in the repository's `images/` directory.

| Filename | Evidence |
|---|---|
| `Figure_1.png` | Automated testing — 18 tests passed |
| `Figure_3.png` | CloudFormation deployment completed |
| `Figure_6.png` | Maintenance reporting interface and submission |
| `Figure_7.png` | Public issue tracking |
| `Figure_14.png` | Staff dashboard with resolved maintenance issue |
| `Figure_21.png` | AWS Lambda functions |
| `Figure_AWS_API_Gateway_Lambda_Integration.png` | API Gateway integration with Lambda |
| `Figure_AWS_DynamoDB_Tables.png` | DynamoDB tables |
| `Figure_AWS_S3_Photo_Bucket_Privacy.png` | S3 Block Public Access settings |
| `Figure_AWS_SQS_Queues.png` | Notification queue and dead-letter queue |
| `Figure_AWS_CloudWatch_Notification_Worker.png` | CloudWatch notification-worker logs |
| `email sc.jpeg` | Maintenance notification email received through SNS |

Additional functional and security test evidence was collected during development. Not every verification step has a separate screenshot in the public repository.

## 3. Automated Testing

The recorded pytest execution demonstrated:

**18 tests passed.**

The automated tests covered request handling, validation, maintenance issue creation and tracking, access control, upload handling, staff updates and notification processing using mocked AWS services.

These offline tests complement the live AWS functional checks; they are not substitutes for cloud integration testing.

## 4. Verified Application Workflow

The following workflows were exercised during development and verification:

1. Submitting a maintenance issue from the public CampusFix website.
2. Receiving a unique issue tracking ID.
3. Checking the issue's current status.
4. Accessing the staff dashboard using authorised credentials.
5. Updating an issue from Open to In Progress and Resolved.
6. Uploading an optional private photograph and retrieving it through authorised temporary access.
7. Processing notification messages through the SQS-based worker.
8. Receiving an actual SNS maintenance notification email.
9. Observing successful background processing in CloudWatch logs.

## 5. Security Verification

The implementation includes Cognito-based staff authentication, backend authorisation checks, private photograph storage and temporary presigned URLs.

Recorded security checks included unauthorised administrative requests and blocked direct access to private photo objects.

The prototype has not undergone an independent penetration test or formal security certification.

## 6. Limitations and Outstanding Verification

The following items are not claimed as fully tested:

- Dead-letter queue redrive behaviour under actual worker failure.
- High-concurrency and load testing.
- Comprehensive API latency and performance benchmarking.
- Production-scale reliability and disaster recovery.
- Final AWS spending and cost analysis.

These limitations do not invalidate the completed functional tests, but they are important when describing the scope of the prototype.

## 7. Evidence Integrity

All screenshots and results should reflect actual implementation and testing.

Sensitive information must be redacted before evidence is placed in a public repository, including personal email addresses, passwords, authentication tokens, AWS credentials and signed access URLs.

Where possible, evidence should identify the relevant AWS service, application feature or test outcome.

**This register documents verified prototype functionality rather than claiming full production readiness.**
