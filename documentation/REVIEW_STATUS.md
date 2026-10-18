# CampusFix — Implementation and Verification Status

**ICT5205 Assignment 3 — Smart Campus Maintenance System**

**Current status:** AWS deployment completed, core functionality verified, and GitHub source repository established.

**Last project documentation review:** 18 October 2026

## 1. Overview

CampusFix was developed as a distributed, serverless campus maintenance reporting prototype using AWS services.

The project progressed through offline development, automated testing, AWS deployment, functional verification, and preparation of assessment evidence.

This document distinguishes completed verification from prototype limitations and remaining academic submission tasks.

## 2. Offline Development and Verification

Before deploying to AWS, the following checks were completed:

- Reviewed the official Assignment 3 brief, marking rubric and CampusFix proposal presentation.
- Implemented the proposed REST API routes and added a staff-only photograph retrieval endpoint.
- Successfully compiled the Python backend using `compileall`.
- Completed offline tests covering request validation, issue creation, tracking, protected staff operations, presigned uploads, notification processing and error handling.
- Checked JavaScript syntax using `node --check`.
- Checked Bash deployment script syntax using `bash -n`.
- Parsed the CloudFormation/SAM YAML template and reviewed its resource definitions and security configurations.
- Reviewed API CORS and CloudFront Origin Access Control configurations.

These checks were conducted before live AWS deployment and do not independently establish cloud integration success.

## 3. AWS Deployment — 15–16 October 2026

The application was deployed successfully in AWS Asia Pacific (Sydney), `ap-southeast-2`.

### Deployment verification

- AWS SAM template validation completed.
- Both Lambda functions built using Python 3.13.
- CloudFormation stack `campusfix-dev` reached `CREATE_COMPLETE`.
- Frontend application published through Amazon S3 and CloudFront.
- API Gateway connected to the backend Lambda function.
- DynamoDB tables provisioned for maintenance issues and notification events.
- Amazon Cognito configured for staff authentication.
- Amazon SQS, SNS and a notification-worker Lambda deployed for asynchronous email notifications.
- CloudWatch logging enabled.
- IAM permissions configured for application components.

**Live application:** https://dy5mpxcnbr23i.cloudfront.net

## 4. Functional Verification

The following functionality was successfully exercised in the deployed environment:

| Component | Verified behaviour |
|---|---|
| Public reporting | Maintenance issue submitted successfully |
| Issue tracking | Unique tracking ID returned and issue retrieved |
| DynamoDB | Submitted maintenance record stored |
| Staff authentication | Cognito staff account authenticated |
| Staff authorisation | Protected administrative operations restricted |
| Staff dashboard | Maintenance issues listed and updated |
| Issue lifecycle | Open → In Progress → Resolved |
| Public status tracking | Reflected staff updates |
| Photograph upload | JPEG photograph uploaded to private S3 |
| Photograph access | Authorised temporary retrieval succeeded |
| S3 security | Anonymous photograph access returned HTTP 403 |
| API security | Unauthenticated administrative access returned HTTP 401 |
| Input validation | Empty title returned HTTP 400 |
| Missing record | Invalid/nonexistent tracking ID returned HTTP 404 |
| SNS notifications | Actual maintenance notification email delivered |
| CloudWatch | Successful notification-worker publishing recorded |

An unauthorised status-update attempt was also rejected, and the existing DynamoDB issue record remained unchanged.

## 5. Automated Testing

The captured pytest execution showed:

**18 automated tests passed.**

The tests exercised backend request processing, validation, tracking, administrative permissions, upload handling and notification-worker behaviour using mocked AWS dependencies.

These results demonstrate successful execution of the recorded test suite, but they do not represent performance or security certification.

## 6. AWS Infrastructure and Monitoring

Additional infrastructure checks confirmed:

- Two deployed Lambda functions.
- Two active DynamoDB tables.
- API Gateway routes integrated with Lambda.
- Private S3 photograph bucket with Block Public Access enabled.
- SQS notification queue and dead-letter queue configured.
- Notification-worker Lambda integration with SQS.
- SNS email subscription confirmed.
- CloudWatch logs showing successful notification publication.
- Sampled Lambda monitoring periods showing zero execution errors.
- SQS queues showing zero pending and in-flight messages at the time inspected.
- Account-wide AWS monthly budget configured at USD 5 with an email recipient.

These observations do not establish full load-handling capability or dead-letter queue recovery behaviour.

## 7. GitHub Repository and Assessment Evidence

The CampusFix source code and project documentation have been committed to the public GitHub repository:

https://github.com/MRDarkkk/ICT5205-CampusFix

The repository includes:

- `code/` — frontend and backend application.
- `deploy/` — AWS SAM infrastructure and deployment scripts.
- `tests/` — automated tests.
- `documentation/` — user manual, evidence register and verification record.
- `images/` — 12 uploaded application, AWS infrastructure and testing screenshots.
- `README.md` — project overview, architecture, API, testing and deployment information.

The evidence screenshots cover successful deployment, application functionality, AWS service integration, automated testing and notification processing.

## 8. Remaining Technical Limitations

The following have not been demonstrated through comprehensive live testing:

- Dead-letter queue handling and recovery after repeated processing failures.
- High-concurrency or large-scale load performance.
- Formal API response-time benchmarking.
- Independent penetration testing.
- Production-scale resilience and disaster recovery.
- Comprehensive protection against abusive use of public upload endpoints.

CampusFix remains an academic prototype rather than a production-certified maintenance system.

## 9. Remaining Assessment Tasks

The following items require final confirmation or completion:

- Review final report content against the official ICT5205 Assignment 3 marking rubric.
- Confirm required academic submission files and formats.
- Verify the signed group contribution agreement.
- Confirm individual reflection requirements.
- Review the user manual and deployment instructions for outdated statements.
- Verify the separate source-code printout deliverable.
- Finalise the presentation and record the required demonstration.
- Confirm tutor approval and the LMS submission deadline.
- Review AWS costs and perform resource cleanup after assessment when appropriate.

These items should only be marked completed once their final deliverables have been checked.

## 10. Conclusion

CampusFix has progressed beyond its original offline release and has been successfully deployed and functionally tested on AWS.

The implementation demonstrates a distributed serverless architecture incorporating secure staff access, private cloud storage, persistent data, asynchronous messaging, email notifications and operational monitoring.

The recorded evidence supports the completed functionality while preserving a clear distinction between verified outcomes and remaining prototype limitations.
