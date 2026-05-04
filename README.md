# Last Model: System Failure Protocol

A cinematic AI survival game for Garage Inference. The project intentionally keeps the model small and the surrounding system strong: deterministic preprocessing, validation layers, retries, proof panels, and human decision gates do most of the work.

## What the model is

- Default local model: Qwen 3 0.6B through Ollama
- Remote fallback: Groq with Llama 3.1 8B Instant
- Runtime selection: `INFERENCE_MODE=local` or `INFERENCE_MODE=groq`

The app does not depend on the model being perfect. Each level wraps the model with task-specific extraction, scoring, verification, and formatting so the final output stays stable and explainable.

## What the project does

The game turns weak-model inference into a staged survival system:

- Level 1: code and log review
- Level 2: argument and fallacy analysis
- Level 3: behavioral transcript analysis
- Level 4: CSV and anomaly detection
- Level 5: crisis communication rewrite

Each task follows the same pattern: a naive model pass, a stronger system pass, and a proof panel that shows why the final answer is trusted.

## Sample inputs

The repository now includes clearer, higher-signal samples for each level:

- [samples/level1_auth_bypass_review.py](samples/level1_auth_bypass_review.py)
- [samples/level2_false_dilemma_argument.txt](samples/level2_false_dilemma_argument.txt)
- [samples/level3_shift_handoff_transcript.txt](samples/level3_shift_handoff_transcript.txt)
- [samples/level4_clinic_aid_anomaly.csv](samples/level4_clinic_aid_anomaly.csv)
- [samples/level5_incident_broadcast_summary.txt](samples/level5_incident_broadcast_summary.txt)

These files are designed to produce better model traces and more readable proof panels.

## Stack

- Frontend: Vite + React
- Backend: FastAPI + SSE streaming
- Inference: Ollama locally, Groq as fallback
- Default local model: Qwen 3 0.6B

## Quick start

1. Install frontend deps:
   ```bash
   cd frontend
   npm install
   ```

2. Prepare backend environment:
   ```bash
   cd backend
   copy .env.example .env
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the stack from the repo root:
   ```bash
   npm install
   npm run dev
   ```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Backend notes

- `/api/game/start` creates a session
- `/api/game/level/{session_id}/input` starts a level pipeline
- `/api/pipeline/{session_id}/stream` streams SSE events
- `/api/human/{session_id}/decision` resumes a paused pipeline

## Files of interest

- [backend/main.py](backend/main.py)
- [backend/config.py](backend/config.py)
- [backend/inference/client.py](backend/inference/client.py)
- [backend/pipelines/level1_cascade.py](backend/pipelines/level1_cascade.py)
- [backend/pipelines/level2_clause.py](backend/pipelines/level2_clause.py)
- [backend/pipelines/level3_hollow.py](backend/pipelines/level3_hollow.py)
- [backend/pipelines/level4_deadstar.py](backend/pipelines/level4_deadstar.py)
- [backend/pipelines/level5_broadcast.py](backend/pipelines/level5_broadcast.py)

## Notes

The project is built to show how a weak model can still drive a polished experience when the system around it is carefully engineered.
