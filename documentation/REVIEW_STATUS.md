# Independent verification record — CampusFix offline release 0.1

This record distinguishes checks actually executed from future AWS verification.

## Verified locally

- Reviewed the official Assignment 3 brief and rubric, plus all 10 slides of the existing CampusFix proposal.
- Preserved all five proposed REST routes and added staff-only photo preview (`GET /admin/issues/{id}/photo`).
- Python backend compiled with `compileall`.
- Offline Python tests passed, including positive and negative submissions, protected staff endpoints, presigned upload, 404s, malformed JSON, SNS worker success/failure and best-effort duplicate handling.
- JavaScript syntax checked with `node --check` for all JS files.
- Bash scripts syntax checked with `bash -n`.
- CloudFormation/SAM template YAML parsed successfully, and structural checks verified required resources, private buckets, scoped policy actions and protected admin routes.
- Matched HTTP API CORS lists and CloudFront OAC empty OriginAccessIdentity to AWS documentation.

## Not yet verified — MUST confirm before claiming project completion

- The template has not been compiled by the AWS SAM CLI. Local runtime did not include SAM CLI or cfn-lint.
- No AWS CloudFormation change set, stack creation, IAM role deployment or real resource test has occurred.
- Browser login with Cognito and end-to-end API/S3 upload require a real AWS account deployment.
- SNS subscriber email confirmation and worker delivery require real AWS tests.
- No AWS costs, execution times or performance results have been measured.
- No assessment screenshots or real website URLs exist yet.
- Tutor approval, group signatures, LMS deadline, YouTube demo and actual report are outstanding.

The project is ready for **controlled AWS pre-deployment review and SAM validation**, not ready for final academic submission.

## AWS deployment and live verification — 16 October 2026

The original offline verification section above is retained as historical evidence.

### Verified on AWS

- AWS SAM template validated successfully and both Lambda functions built using Python 3.13.
- CloudFormation stack `campusfix-dev` deployed to Sydney (ap-southeast-2), status CREATE_COMPLETE.
- Public CampusFix website delivered successfully through S3 and CloudFront.
- Maintenance requests submitted, tracked and stored in DynamoDB.
- Cognito staff user created, confirmed and assigned to the `staff` group.
- Staff dashboard login and issue status transitions tested: open, in_progress and resolved.
- Public tracking reflected staff status changes.
- JPEG photo uploaded to private S3 storage; object metadata and AES256 encryption verified.
- Anonymous S3 photo request rejected with HTTP 403.
- Unauthenticated private photo API and staff endpoints rejected with HTTP 401.
- Authorised staff photo retrieval tested.
- SNS email subscription confirmed and actual maintenance notification received.
- Notification worker CloudWatch logs showed successful SNS publication.
- Main SQS queue and dead-letter queue reported zero pending and in-flight messages.
- Both Lambda functions returned zero execution errors in the sampled CloudWatch metric periods.
- Empty-title submission rejected with HTTP 400.
- Nonexistent issue tracking ID returned HTTP 404.
- Unauthorised status-change attempt returned HTTP 401; DynamoDB record remained resolved.
- AWS monthly budget configured at USD 5, account-wide, with one verified email recipient.

### Still outstanding

- Consolidate and verify all original assessment screenshots.
- Prepare and review the final academic report against the marking rubric.
- Finalise user manual, deployment instructions, source-code printout and submission structure.
- Verify and complete signed group contribution agreement.
- Confirm tutor approval, individual reflection requirements and LMS submission deadline.
- Finalise presentation and record the required demonstration.
- Document remaining prototype limitations, including untested DLQ failure recovery and public upload abuse protection.
- Review AWS expenditure and perform planned resource cleanup after assessment.

