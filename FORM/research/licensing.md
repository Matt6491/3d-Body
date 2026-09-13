# Licensing notes (reviewed 2026-09-13)

This is an engineering inventory, not legal advice.

## MediaPipe

The official `google-ai-edge/mediapipe` repository identifies the project as Apache-2.0 licensed:
https://github.com/google-ai-edge/mediapipe

FORM does not currently bundle MediaPipe or its model assets. Before enabling the optional adapter, pin the exact package/model assets and preserve all required notices.

## SMPL-X

Do **not** make the commercial product depend on the research-licensed SMPL-X Model & Software by default.

The official SMPL-X model-license page states that the Model & Software license is for non-commercial scientific research and directs commercial users to commercial licensing:
https://smpl-x.is.tue.mpg.de/modellicense.html

There is also a distinct SMPL-X Body Creative Commons license for a subset/body artifact, with terms that differ from the full parametric Model & Software:
https://smpl-x.is.tue.mpg.de/bodylicense.html

Because FORM needs shape fitting/parameterization, a production choice must be reviewed against the exact artifact/API being used. The current prototype therefore ships only `ParametricPrimitiveBodyProvider`, a clean-room procedural provider, and keeps future body-model implementations behind `BodyModelProvider`.

## Three.js / React Three Fiber / Next.js

Review and preserve the licenses of the exact npm dependency versions resolved in the production lockfile before distribution.
