# FORM — Project Status

Updated: 2026-09-13

## Current vertical slice

### Fully working in code and verified

- Repository is separated into `/frontend`, `/backend`, `/body-model`, `/computer-vision`, `/adaptation-engine`, `/exercise-data`, `/research`, `/tests`.
- FastAPI backend starts under `uvicorn` and exposes health, exercise data, photo analysis, body retrieval/deletion, analysis deletion, simulation, timeline, and the built-in pushup QA route.
- Adult confirmation and explicit photo-processing consent are enforced before analysis.
- Front/side/back uploads are required and restricted to JPEG/PNG/WebP plus byte-size/resolution/silhouette checks.
- Original image bytes are not persisted by the local MVP repository and go out of scope after analysis.
- Local silhouette pipeline estimates scaled body-proportion proxies from supplied height and front/side silhouettes.
- Coarse front-view joints and semantic region bands are produced for head, shoulders, chest, waist, hips, arms, thighs, calves, feet and overall silhouette.
- Optional known shoulder/waist/hip widths override uncertain silhouette estimates.
- `BodyModelProvider` abstraction exists; the active provider is the license-safe procedural `ParametricPrimitiveBodyProvider`.
- Renderer-independent morphology rules map each supported muscle to local anatomical regions/surfaces (e.g. biceps anterior arm, triceps posterior arm, quads anterior thigh).
- Next/React/R3F frontend source implements MY BODY, TRAIN, FUTURE and MUSCLE MAP views.
- 3D source uses one parameterized body across time and applies local muscle-specific geometry changes. Baseline proportions come from reconstructed measurements.
- Front/back/left/right controls, side-by-side comparison and pointer-draggable before/after divider are implemented.
- Structured routines can combine multiple exercises; simple mode supports repetitions/frequency and pushup capacity.
- External resistance can be recorded in structured mode. It is not converted into fake relative intensity without a strength baseline; RIR is used for effort.
- Recovery and adherence assumptions are user-adjustable inputs to the deterministic engine.
- Central exercise catalog contains all 31 requested initial exercises with primary/secondary/stabilizer roles.
- Reverse muscle-to-exercise lookup is implemented.
- Adaptation engine includes minimum-effective stimulus, saturating volume response, relative difficulty, recovery limitation, repeated-bout/non-progressive plateau behavior, experience response and starting-development headroom.
- Same 100-pushup prescription is capacity-sensitive: it earns less modeled stimulus as that work becomes easy relative to max capacity.
- Body-fat delta is hard-locked to zero in the training-only engine.
- Timeline checkpoints: 0, 2, 4, 8, 12, 26, 39 and 52 weeks. Frontend caches checkpoint states and smoothstep-interpolates intermediate slider positions.
- Supabase schema/RLS migration sketch exists with separated identity/body-analysis/photo metadata tables and private-storage intent.
- Docker/Render and Vercel scaffolding exists.
- Research assumptions and licensing notes are separated from application code.

## Actually tested in this session

- `python -m pytest -q`: **28 passing tests** in the final integrated run.
- Coverage includes exercise mappings/catalog schema, timeline interpolation, body-fat invariance, untrained-muscle invariance, diminishing returns, beginner vs advanced response, starting-development headroom, capacity-sensitive 100 pushups/day, multi-exercise routines, zero exercise, plateau behavior, CV analysis, invalid/blank CV input, consent/adult gates, upload/reconstruct/delete, simulation validation and known-measurement overrides.
- `python scripts/qa_pushups.py`: pass. At all checkpoints unrelated quads/hamstrings/calves/glutes/lats/biceps remain zero and body-fat delta remains zero.
- `python scripts/e2e_backend.py`: pass against a **real uvicorn process**, not just FastAPI TestClient: upload → reconstruct → timeline → targeted pushup adaptation → delete.
- Main frontend TS/TSX files pass TypeScript parser/transpile diagnostics via `scripts/check_tsx.js`.
- Static responsive-shell visual regression runs in real Chromium under Xvfb with Playwright injection:
  - desktop 1440×900 has no overflow;
  - mobile 390×844 has no horizontal overflow and hides the right rail;
  - accepted desktop/mobile baselines pass at RMS 0.0.
- The mobile visual pass found and fixed a footer/body overlap before baseline acceptance.
- Visual review also found/fixed measurement double-scaling and comparison-view rotation of body spacing.

## Commands

### Backend

```bash
python -m pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run typecheck
npm run dev
# production:
npm run build
npm start
```

Set `NEXT_PUBLIC_FORM_API` if the API is not at `http://127.0.0.1:8000`.

### Verification

```bash
python -m pytest -q
python scripts/qa_pushups.py
python scripts/e2e_backend.py
node scripts/check_tsx.js frontend/app/page.tsx frontend/components/BodyViewer.tsx frontend/components/BeforeAfterCompare.tsx frontend/lib/api.ts
xvfb-run -a python scripts/visual_regression.py
```

## Approximations currently in use

- **Body reconstruction:** procedural primitives with personalized measured proportions, not a photorealistic human mesh.
- **Photo analysis:** contrast/silhouette heuristic plus coarse geometry landmarks, not production MediaPipe pose + segmentation.
- **Measurements:** scaled proxies suitable for visualization initialization, explicitly not medical measurements.
- **Morphs:** anatomically directional semantic bulges, not artist-authored/scan-calibrated production blend shapes.
- **Adaptation model:** deterministic heuristic normalized parameters. It is not yet empirically calibrated to predict an individual’s exact hypertrophy.
- **Age/sex:** collected and stored as profile context; the current engine does not invent unvalidated age/sex growth multipliers.
- **Absolute resistance kg:** recorded, but RIR/capacity drives relative difficulty until an exercise-specific strength baseline is available.
- **Body fat:** optional self-report initializes a separate body-composition parameter; it does not change over the exercise-only timeline.
- **Visual regression:** current automated screenshot harness covers the responsive shell with a deterministic SVG body, not the unbuilt R3F runtime.

## Known bugs / environment blockers

- This execution environment could not resolve/reach the npm registry, so Next/React/R3F packages could not be installed here. Therefore the real Next app could not be compiled or launched in this session.
- Chromium navigation to `file://` and localhost was blocked by container browser policy. Visual inspection was still performed by launching Chromium under Xvfb and injecting the deterministic preview HTML using Playwright.
- The environment injects an unrelated spreadsheet/artifact-tool Python startup hook that adds several seconds and may print warnings/errors; it does not affect FORM tests once startup completes.
- The local in-memory backend has no authentication and no durable account. “Delete account data” in the local UI purges the current body/analysis state; full identity-account deletion requires the production auth repository.

## External dependencies still needed

- Network-enabled npm install for the frontend dependency graph and production lockfile.
- Production-quality pose/person segmentation model implementation. MediaPipe is a candidate behind `MediaPipeAnalyzer`, but exact package/model assets must be pinned and reviewed.
- Commercially approved human body mesh/model provider with local muscle morph targets and fitting support.
- Supabase project credentials (or equivalent), private storage bucket and authentication.
- Longitudinal training/adaptation evidence or dataset for calibration and uncertainty ranges.

## Licensing issues

- MediaPipe’s official repository is Apache-2.0, but exact bundled model assets/dependencies should still be reviewed and notices retained.
- The official full SMPL-X Model & Software license is non-commercial research by default and points commercial users to commercial licensing. FORM does not bundle it.
- A distinct SMPL-X Body subset license exists, but it is not assumed to cover the full shape-fitting/model workflow.
- See `research/licensing.md`.

## Next implementation priorities

1. In a network-enabled environment: `npm install`, `npm run typecheck`, `npm run build`, run the real app, then execute the complete browser journey using the included synthetic photo fixtures.
2. Replace silhouette fallback with a production pose + segmentation adapter; preserve current response contract and tests.
3. Select/license/build a production body-model provider and map `morphology.py` rules to mesh blend shapes.
4. Implement Supabase repository/auth/private signed-photo workflow and deletion jobs.
5. Calibrate the adaptation engine and add projected ranges/uncertainty instead of only normalized point estimates.
6. Add real Next/R3F Playwright regression tests.

## Final verification

`scripts/verify.sh` completed with exit code 0 on 2026-09-13: 28 tests, pushup QA PASS, real-server E2E PASS, TSX parser checks OK, desktop/mobile visual regression PASS.

## Exact resume point

Start in `/mnt/data/FORM`. Read `TODO.md`, then run the verification commands above. The first code task should be **frontend dependency installation + real Next build/browser run**. Do not redesign architecture first; the next session should validate/fix the existing frontend runtime, then proceed to the pose/segmentation adapter.
