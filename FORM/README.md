# FORM

Training-driven body adaptation simulator vertical slice.

FORM keeps one parameterized body representation across the timeline. Exercise mappings drive deterministic, local muscle parameters; body composition is a separate subsystem and stays constant in the MVP.

## Quick start

Backend:

```bash
python -m pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. Use the built-in **35M PUSHUP QA PROFILE** to exercise the simulator without personal photos.

## Test

```bash
python -m pytest -q
python scripts/qa_pushups.py
```

See `PROJECT_STATUS.md` for verified functionality and current limitations.
