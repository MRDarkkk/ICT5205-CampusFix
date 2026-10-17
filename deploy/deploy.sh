#!/usr/bin/env bash
# Run manually in the AWS CloudShell after reviewing the template and budget.
set -euo pipefail
cd "$(dirname "$0")/.."
REGION="ap-southeast-2"
STACK="campusfix-dev"
command -v sam >/dev/null || { echo 'SAM CLI is not installed. Stop and follow README deployment prerequisites.'; exit 1; }
aws sts get-caller-identity --query '{Account:Account,Arn:Arn}'
echo "Deploying $STACK to $REGION. Review permissions and charges before confirming."
sam build --template-file deploy/template.yaml
sam deploy --stack-name "$STACK" --region "$REGION" --resolve-s3 \
  --capabilities CAPABILITY_IAM --confirm-changeset \
  --no-fail-on-empty-changeset
