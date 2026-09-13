#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pytest -q
python scripts/qa_pushups.py
python scripts/e2e_backend.py
node scripts/check_tsx.js frontend/app/page.tsx frontend/components/BodyViewer.tsx frontend/components/BeforeAfterCompare.tsx frontend/lib/api.ts
if command -v xvfb-run >/dev/null 2>&1; then
  xvfb-run -a python scripts/visual_regression.py
else
  echo "SKIP visual regression: xvfb-run unavailable"
fi
