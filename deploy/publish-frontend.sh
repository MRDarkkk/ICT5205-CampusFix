#!/usr/bin/env bash
# Publish only after the stack has been successfully created and verified.
set -euo pipefail
cd "$(dirname "$0")/.."
STACK=campusfix-dev
REGION=ap-southeast-2
output() { aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue|[0]" --output text; }
API_BASE="$(output ApiBaseUrl)"
SITE_BUCKET="$(output WebsiteBucketName)"
CLIENT_ID="$(output UserPoolClientId)"
SITE_URL="$(output WebsiteUrl)"
DIST_ID="$(output CloudFrontDistributionId)"
# No secrets: public runtime values only.
cat > code/frontend/config.js <<EOF
window.CAMPUSFIX_CONFIG = {
  apiBase: '${API_BASE}',
  region: '${REGION}',
  cognitoClientId: '${CLIENT_ID}'
};
EOF
aws s3 sync code/frontend/ "s3://${SITE_BUCKET}/" --region "$REGION" --exclude '*.map' --delete
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths '/*' >/dev/null
echo "Frontend published at ${SITE_URL}"
echo "CORS is already restricted to the CloudFront origin in the deployed SAM template."
