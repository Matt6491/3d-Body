# FORM — Next Steps & Backlog

## Immediate Priority
- [x] Install frontend dependencies in a network-enabled environment (`npm install`).
- [x] Resolve Next.js/React Three Fiber build issues and run real dev server.
- [x] Verify live UI sections:
  - MY BODY (upload consent, baseline visualization, 35M Pushup QA profile)
  - TRAIN (exercise selection, routine builder, recovery/adherence controls)
  - FUTURE (timeline slider 0-52w, comparison slider, single/split camera)
  - MUSCLE MAP (anatomical region breakdown, reverse exercise lookup)

## Backend & Model Pipeline
- [ ] Implement production pose + segmentation adapter (MediaPipe or ONNX runtime) replacing contrast silhouette heuristic.
- [ ] Select or license production commercial human body mesh (SMPL-X commercial license or license-free rigged base mesh).
- [ ] Map `morphology.py` rules to production mesh vertex displacement / blend shapes.
- [ ] Add empirical hypertrophy dataset calibration and Bayesian confidence intervals (uncertainty ranges).

## Persistence & Infrastructure
- [ ] Supabase integration: PostgreSQL migrations, Row-Level Security (RLS).
- [ ] Secure private S3/Supabase Storage bucket for photo processing with auto-deletion lifecycle.
- [ ] Dedicated FastAPI backend deployment (Render/Fly.io/Cloud Run) with `NEXT_PUBLIC_FORM_API` endpoint configured.
- [ ] End-to-end browser automation tests (Playwright R3F canvas verification).
