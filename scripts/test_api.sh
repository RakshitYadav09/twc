#!/usr/bin/env bash
# Quick smoke test using curl. Ensure server is running at http://127.0.0.1:8000
set -euo pipefail

BASE=http://127.0.0.1:8000

echo "Health:"
curl -s $BASE/health | jq || true

echo "Create org (temporary):"
RESP=$(curl -s -X POST $BASE/org/create -H "Content-Type: application/json" -d '{"organization_name":"smoketest","email":"smoke@example.com","password":"smoketest"}')
echo "$RESP" | jq || true

echo "Done"
