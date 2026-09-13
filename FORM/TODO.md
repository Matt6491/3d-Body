# FORM TODO

Updated: 2026-09-13

## P0 — resume here

- Install frontend npm dependencies in a network-enabled environment and run `npm run typecheck`, `npm run build`, then the real Next/R3F app in Chromium. The current execution environment could not reach the npm registry.
- Replace `SilhouetteAnalyzer` with a validated pose + person-segmentation implementation behind the same analysis contract. Keep the local fallback for offline QA.
- Implement a production-grade `BodyModelProvider` with a commercially approved parametric mesh/rig and localized morph targets. Do not make the product depend on research-only SMPL-X terms.
- Calibrate adaptation-engine configuration against reviewed longitudinal evidence/datasets. Current coefficients are transparent heuristics, not individual predictions.

## P1

- Implement authenticated Supabase repository adapter, private photo bucket, signed upload/download URLs, RLS, deletion jobs, and real account deletion.
- Add browser E2E tests against the real Next app: onboarding, upload fixtures, reconstruction, pushup routine, timeline scrub, divider drag, muscle map.
- Add a real R3F/WebGL visual regression test once frontend dependencies are installed; current visual regression covers the responsive shell only.
- Map `body-model/morphology.py` semantic morph rules to production mesh blend shapes.
- Add optional baseline circumference inputs with explicit definitions and units; do not mix circumference with current silhouette width proxies.
- Add strength-baseline fields (e.g. estimated 1RM or exercise-specific capacity) before using absolute resistance kg to infer relative load.
- Add session distribution for simple high-rep routines (all-at-once vs sets through the day).

## P2

- Texture projection onto the approved body mesh with face removal and privacy review.
- Better capture guidance, per-photo quality overlays, retake flow, camera-distance/pose checks.
- Add side/back silhouette landmarks rather than only front-region semantic bands.
- Add uncertainty ranges to visual output after calibration rather than a single normalized delta.
- Accessibility audit: keyboard divider dragging, focus rings, reduced motion, screen-reader labels for muscle map.
- Device/WebGL capability fallback and lower-poly mesh path.
- Observability that never logs private body images or signed URLs.

## Explicit non-goals until evidence/licensing exists

- No independent AI-generated future photos.
- No automatic fat loss from exercise selection.
- No claim that normalized muscle deltas equal centimeters, kilograms of muscle, or exact hypertrophy percentages.
- No bundled SMPL-X Model & Software in a commercial build without the correct license.
