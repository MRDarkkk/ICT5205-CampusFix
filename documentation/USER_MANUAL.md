# CampusFix — User Manual
ICT5205 Assignment 3 | Smart Campus Maintenance System

## 1. Introduction

CampusFix is a cloud-based academic prototype that allows campus users to report maintenance problems and track their progress.

Authorised maintenance staff can sign in to review and update submitted requests.

Website:
https://dy5mpxcnbr23i.cloudfront.net

CampusFix is not an official campus emergency service. Urgent hazards should be reported directly to campus security or the appropriate emergency service.

## 2. Reporting a Maintenance Issue

1. Open the CampusFix website.
2. Locate the Report an Issue form.
3. Enter a short issue title.
4. Describe the maintenance problem.
5. Enter the building or location.
6. Select the appropriate issue category.
7. Choose the priority.
8. Optionally attach a JPEG, PNG or WebP photograph up to 5 MB.
9. Click Submit Maintenance Report.
10. Save the tracking ID displayed after successful submission.

The tracking ID is needed to check the issue later.

## 3. Tracking an Issue

1. Open the public CampusFix website.
2. Locate the Track Your Report section.
3. Enter the tracking ID received during submission.
4. Click Check Status.
5. Review the displayed issue information and current status.

Possible statuses:
- Open: The report has been submitted.
- In Progress: Maintenance staff are working on the issue.
- Resolved: Staff have marked the issue as completed.

Tracking IDs should be kept private because anyone possessing a valid ID may be able to view the limited public tracking information.

## 4. Maintenance Staff Login

1. Open the Staff Dashboard from the website navigation.
2. Enter the registered Cognito staff email.
3. Enter the permanent password.
4. Click Sign In.

Only authorised accounts assigned to the Cognito staff group can access the protected management functions.

If login fails, verify the account credentials and contact the system administrator.

## 5. Managing Maintenance Requests

After signing in:

1. View the list of recent maintenance requests.
2. Review each request's title, location, priority and status.
3. Use the status filter to display matching issues.
4. Select a new status when maintenance progress changes.
5. Click Save to submit the change.
6. Refresh the list to view updated information.

The public tracking page reflects saved status changes.

The dashboard displays a limited number of recent records and does not represent a complete historical reporting system.

## 6. Viewing Uploaded Photos

Maintenance requests may contain photographs.

Authorised staff can use the available photo-viewing option to retrieve an uploaded image.

Photos are stored in private Amazon S3 storage. Temporary signed URLs allow authorised viewing without making the bucket publicly accessible.

Do not share signed photo URLs.

## 7. Email Notifications

When a new maintenance issue is created, CampusFix attempts to send an asynchronous notification through Amazon SQS, AWS Lambda and Amazon SNS.

Confirmed email subscribers may receive a notification containing the new issue ID and category.

Email notification delivery depends on successful background processing and a confirmed SNS subscription.

## 8. Common Errors

- Invalid title or missing required information: correct the form and submit again.
- Unknown tracking ID: check the ID and retry.
- Staff login failure: confirm credentials and account status.
- Unauthorised access: a valid staff login is required.
- Photo upload failure: check the file format, file size and network connection.

Avoid repeatedly submitting the same maintenance issue after an uncertain response.

## 9. Security and Privacy

- Never share passwords or authentication tokens.
- Keep tracking IDs private.
- Avoid uploading sensitive photographs or personal information.
- Staff should use only authorised accounts.
- Sign out when finished using a shared computer.

## 10. Academic Prototype Limitations

CampusFix is designed for controlled academic demonstration rather than production campus deployment.

It does not replace institutional maintenance procedures, emergency response or formal service-level agreements.

