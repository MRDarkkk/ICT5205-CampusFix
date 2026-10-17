# CampusFix — Smart Campus Maintenance System

ICT5205 Assignment 3 — AWS distributed application prototype.

**Development status:** source code and AWS SAM/CloudFormation infrastructure template have been prepared. **Not deployed or verified on AWS yet.** No real performance results are claimed.

## Purpose

CampusFix lets a reporter submit a maintenance issue (optional private photo) and track its status with an unguessable tracking ID. Authenticated maintenance staff can view recent reports and update their status. A queue and background worker notify a separately confirmed staff SNS email subscription.

## AWS architecture

- Private S3 website origin → CloudFront (HTTPS)
- Browser → API Gateway (HTTP API) → Lambda → DynamoDB / S3
- Lambda → SQS → worker Lambda → SNS (confirmed subscriber)
- Cognito JWT authentication plus `staff` group checks on admin routes
- Least-privilege IAM roles and seven-day CloudWatch log retention
- CloudFormation/SAM for repeatable deployment (IAM, S3, DynamoDB, Lambda, API, Cognito, SQS, SNS, CloudFront, CloudWatch)

## API

- `POST /issues` (public): title, description, location, category, priority, optional photo key
- `GET /issues/{id}` (public): limited record by random 128-bit tracking ID
- `POST /uploads/presign` (public): presigned S3 POST allowing JPEG/PNG/WebP up to 5 MB
- `GET /admin/issues` (staff JWT + group): list up to 25 recent items, optional status filter
- `PATCH /admin/issues/{id}` (staff JWT + group): status change
- `GET /admin/issues/{id}/photo` (staff JWT + group): short-lived URL to private photo

## Local checks

The Lambda runtime uses Python 3.13 and boto3. To run offline tests (with pytest installed):

```bash
python -m compileall -q code/backend
python -m pytest -q tests
```

Tests do not contact AWS; they exercise request validation, creation, tracking, access controls, upload validation, staff changes and notification processing using mocked AWS clients.

## Deployment

Read `deploy/DEPLOYMENT_GUIDE.md` **before** deploying. Deployment requires prior approval because it creates billable AWS resources and IAM roles. The scripts are designed for AWS CloudShell after AWS SAM CLI prerequisites are checked.

## Academic submission

Save authentic screenshots and measured results in `images/`. The technical report, signed group agreement, full source listing, contributor details and actual live URLs need to be completed after implementation. This package has no real deployment evidence. The proposal PowerPoint contained illustrations, not implementation screenshots.

## Security

Never commit keys, passwords, MFA codes or student IDs. Staff auth via Cognito. Private photos via presigned POST/GET. API authorization is server-side, not a hidden website link. Public issue tracking IDs should be treated as confidential. The project is an educational demonstration, not an emergency reporting system.
