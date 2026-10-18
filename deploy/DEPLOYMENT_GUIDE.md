# CampusFix — AWS Deployment and Operations Guide

## 1. Project overview

CampusFix is a cloud-based campus maintenance reporting application developed for ICT5205 Assignment 3.

The application allows users to submit maintenance requests, upload photographs and track issue status. Authorised maintenance staff can manage requests through a protected dashboard.

## 2. AWS architecture

Region: ap-southeast-2 (Sydney)

Cloud services:
- Amazon S3 — private website and photo storage
- Amazon CloudFront — HTTPS frontend delivery
- Amazon API Gateway — HTTP API endpoints
- AWS Lambda — API processing and notification worker
- Amazon DynamoDB — maintenance records and notification event records
- Amazon Cognito — staff authentication
- Amazon SQS — asynchronous notification queue and dead-letter queue
- Amazon SNS — email notifications
- Amazon CloudWatch — logging and monitoring
- AWS IAM — execution roles and access permissions
- AWS CloudFormation / SAM — infrastructure deployment

## 3. Prerequisites

- AWS account with appropriate deployment permissions
- AWS CLI and AWS SAM CLI
- Python 3.13 compatible environment
- CampusFix source-code package
- AWS Budget notifications configured
- AWS region ap-southeast-2

Do not deploy using the AWS root account or share credentials.

## 4. Deployment verification

From the CampusFix project directory:

    aws sts get-caller-identity
    sam validate --lint --template-file deploy/template.yaml --region ap-southeast-2
    sam build --template-file deploy/template.yaml

Review the SAM template, IAM policies, deployment charges and proposed CloudFormation changes before execution.

## 5. Infrastructure deployment

The project includes:

    bash deploy/deploy.sh

This script builds and deploys the CloudFormation stack:

    campusfix-dev

It uses AWS SAM with explicit confirmation of the changeset.

For a controlled first deployment, prepare and review a CloudFormation change set before executing it.

Never repeat initial deployment commands unnecessarily against an existing stack.
Before executing the script, inspect `deploy/deploy.sh` and confirm the intended AWS account, region, stack name and deployment options.

## 6. Deployed environment

CloudFormation stack: campusfix-dev

Region: ap-southeast-2

Website:
https://dy5mpxcnbr23i.cloudfront.net

API:
https://d7mzpewa1j.execute-api.ap-southeast-2.amazonaws.com

Deployment status verified: CREATE_COMPLETE

Deployment and testing verified on 15–16 October 2026.

These identifiers describe the existing demonstration environment and may change if the stack is recreated.

## 7. Frontend publishing

After successful infrastructure deployment:

    bash deploy/publish-frontend.sh

The publishing script:
1. Retrieves AWS CloudFormation stack outputs.
2. Generates the public frontend configuration.
3. Synchronises frontend files to the website S3 bucket.
4. Invalidates the CloudFront distribution cache.

WARNING: The publishing script uses aws s3 sync --delete.
Confirm the destination bucket before running it.

The deployed API and S3 CORS configuration restricts browser
origins to the CloudFront website domain.
No FrontendOrigin parameter override is required.

## 8. Staff authentication

Amazon Cognito manages maintenance staff authentication.

Staff account setup:
1. Open the deployed Cognito user pool.
2. Create an authorised staff user.
3. Configure a permanent password.
4. Add the user to the staff group.
5. Sign in through the CampusFix staff dashboard.

Do not include passwords or authentication tokens in project files.

## 9. Notification configuration

CampusFix uses:

API Lambda -> SQS -> Notification Worker Lambda -> SNS -> Email

To receive notifications:
1. Open the deployed SNS topic.
2. Create an email subscription.
3. Confirm the subscription through the recipient's email.
4. Submit a new maintenance request.
5. Verify email delivery and CloudWatch logs.

## 10. Verified application tests

The following tests were completed:

- Public website loading
- Maintenance issue submission
- Tracking ID retrieval
- DynamoDB record verification
- Cognito staff authentication
- Staff dashboard access
- Issue status changes: Open -> In Progress -> Resolved
- Public tracking status updates
- Photo upload and storage in S3
- Anonymous S3 access denied: HTTP 403
- Unauthenticated photo API access denied: HTTP 401
- Authorised staff photo access
- SNS maintenance notification email delivery
- SQS and Lambda notification processing
- CloudWatch execution and error monitoring
- Empty title rejected: HTTP 400
- Nonexistent issue ID rejected: HTTP 404
- Unauthorised status update rejected: HTTP 401
- Database record remained unchanged after rejected update

Supporting screenshots of the AWS infrastructure, application workflows, automated testing and email notifications are available in the repository's `images/` directory. See `documentation/EVIDENCE_REGISTER.md` for the evidence summary.

## 11. Known limitations

- Prototype designed for controlled academic use.
- Staff dashboard lists a limited number of recent requests.
- Public photo-upload presigning has throttling and size restrictions but remains susceptible to automated abuse.
- Notification idempotency is best-effort; exactly-once delivery is not guaranteed.
- Dead-letter queue recovery under deliberately induced failures has not been tested.
- AWS charges may apply. Budget alerts do not impose a spending cap.
- Uploaded test photographs require cleanup after the demonstration.

## 12. Resource cleanup

After assessment and tutor demonstration:

1. Save all evidence and required project files.
2. Confirm that the live website is no longer needed.
3. Identify and empty the CampusFix S3 buckets.
4. Delete the CampusFix CloudFormation stack.
5. Inspect CloudFormation deletion events.
6. Check for remaining logs, storage and deployment artifacts.
7. Review AWS billing.

After stack deletion, separately review any manually created resources, SNS subscriptions, CloudWatch logs, AWS Budgets and other account-level configurations. Remove only resources associated with the CampusFix demonstration and confirm that no unexpected charges remain.
