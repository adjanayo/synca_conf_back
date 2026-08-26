#!/usr/bin/env bash
# ROADMAP 8.4 -- daily mysqldump -> Backblaze B2, 30d retention.
# Run on the VPS host (not inside a container) via cron, e.g.:
#   0 3 * * * cd /path/to/synca_conf_back && ./scripts/backup_mysql.sh >> /var/log/synca-backup.log 2>&1
#
# Reuses the same B2 bucket/creds as app uploads (app/core/config.py) under a
# dedicated "backups/" prefix -- one bucket, one set of secrets to rotate.
# Retention is enforced by a B2 lifecycle rule on that prefix (set once via
# `aws s3api put-bucket-lifecycle-configuration`, see bottom of this file),
# not by this script deleting anything itself.
set -euo pipefail

cd "$(dirname "$0")/.."
set -a
source .env
set +a

: "${B2_ENDPOINT_URL:?B2_ENDPOINT_URL not set in .env}"
: "${B2_KEY_ID:?B2_KEY_ID not set in .env}"
: "${B2_APPLICATION_KEY:?B2_APPLICATION_KEY not set in .env}"
: "${B2_BUCKET_NAME:?B2_BUCKET_NAME not set in .env}"

TIMESTAMP="$(date +%Y-%m-%dT%H-%M-%S)"
DUMP_FILE="/tmp/syncaconf-${TIMESTAMP}.sql.gz"

docker compose -f docker-compose.prod.yml exec -T db \
  mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" \
  --single-transaction --routines --triggers "${MYSQL_DATABASE}" \
  | gzip > "${DUMP_FILE}"

AWS_ACCESS_KEY_ID="${B2_KEY_ID}" \
AWS_SECRET_ACCESS_KEY="${B2_APPLICATION_KEY}" \
  aws s3 cp "${DUMP_FILE}" \
  "s3://${B2_BUCKET_NAME}/backups/syncaconf-${TIMESTAMP}.sql.gz" \
  --endpoint-url "${B2_ENDPOINT_URL}"

rm -f "${DUMP_FILE}"
echo "Backup uploaded: backups/syncaconf-${TIMESTAMP}.sql.gz"

# One-time setup (run manually once, not on every cron tick) to make B2
# auto-expire objects under backups/ after 30 days -- ROADMAP 8.4 retention:
#
# cat > /tmp/lifecycle.json <<'EOF'
# {
#   "Rules": [{
#     "ID": "expire-backups-30d",
#     "Filter": {"Prefix": "backups/"},
#     "Status": "Enabled",
#     "Expiration": {"Days": 30}
#   }]
# }
# EOF
# AWS_ACCESS_KEY_ID="$B2_KEY_ID" AWS_SECRET_ACCESS_KEY="$B2_APPLICATION_KEY" \
#   aws s3api put-bucket-lifecycle-configuration --bucket "$B2_BUCKET_NAME" \
#   --lifecycle-configuration file:///tmp/lifecycle.json --endpoint-url "$B2_ENDPOINT_URL"
