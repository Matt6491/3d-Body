# FORM research boundary

This directory separates scientific assumptions from application and rendering code.

## Current status

The MVP adaptation engine is a deterministic **heuristic training-response model**, not a validated predictor of individual hypertrophy. Its normalized coefficients must not be presented as experimentally exact muscle-growth percentages or centimeters.

The application currently makes only these product-level modeling commitments:

- exercise taxonomy distinguishes primary, secondary, and stabilizer roles;
- added training stimulus has diminishing returns rather than linear growth;
- training experience changes response magnitude;
- repeated identical training approaches a plateau without progressive overload;
- recovery/adherence can constrain response;
- exercise-only simulation keeps body-composition parameters constant.

Those commitments are encoded as transparent configurable assumptions in `adaptation-engine/config.json`. Before production claims, each assumption should be tied to a reviewed evidence record and calibrated against longitudinal measured data.

## Evidence workflow

Add one JSON object per assumption to `assumptions.json`. Each record has an `evidenceStatus` field:
- `heuristic-unvalidated`
- `literature-supported`
- `calibrated`
- `deprecated`

Do not promote a record to `literature-supported` without recording a real bibliographic source that has been checked. Do not promote to `calibrated` without recording the dataset, cohort, outcome measure, and calibration procedure.

No source in this directory should be fabricated.
