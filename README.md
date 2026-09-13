# FORM — Training Adaptation Simulator

Training-driven 3D body adaptation simulator modeling localized muscle hypertrophy across training timelines.

FORM keeps one parameterized body representation across the timeline. Exercise mappings drive deterministic, local muscle parameters; body composition is a separate subsystem and stays constant in the MVP.

## Features

- **Personal Reconstruction**: Baseline body geometry estimation from front, side, and back full-body photos with height and weight scaling, plus privacy controls.
- **Training Stimulus**: Simple or structured routines across 31 calibrated exercises with primary, secondary, and stabilizer muscle group roles.
- **Future Adaptation**: Deterministic training adaptation model with volume response, recovery limits, and experience response across 52 weeks.
- **3D Viewer & Comparison**: Interactive Three.js/R3F body viewer with rotation controls, single projected view, side-by-side comparison, and draggable divider.
- **Muscle Map**: Anatomical explorer and reverse muscle-to-exercise lookup.

## Running the Application

```bash
npm install
npm run dev
```

Open http://localhost:3000. Use the built-in **35M PUSHUP QA PROFILE** on the "My Body" tab to exercise the simulator without needing personal photos.
