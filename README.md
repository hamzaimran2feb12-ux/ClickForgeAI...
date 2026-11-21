# ClipForge AI — Deployable Starter (not production-certified)

A mobile-friendly video clipping web app with a FastAPI/FFmpeg export backend and Docker setup.

## Run with Docker (recommended)
1. Install Docker Desktop or Docker Engine.
2. From this folder run `docker compose up --build`.
3. Open http://localhost:8000.
4. Health check: http://localhost:8000/health

## Run without Docker
Install Python 3.10+, FFmpeg (including ffprobe), then in `backend`: `pip install -r requirements.txt` and `uvicorn main:app --reload`.

## Features currently implemented
- Responsive UI and annual/monthly plan display.
- Upload validation, 250 MB cap, temporary input cleanup.
- FFmpeg vertical MP4 exports, up to three distributed segments.
- Health endpoint and Docker container.

## Not yet production features
Highlight selection is a time-distribution heuristic, not trained AI. Transcript-based selection, speech transcription, animated captions, face-aware reframing, user accounts, quota enforcement, cloud storage, payment processing, Google Play Billing, server-side purchase verification, abuse controls, and production security/privacy review are NOT implemented. Plan cards are informational only. Do not charge users or publicly host sensitive videos until these systems are built and reviewed.

## Next Android/Play Store steps
Wrap the HTTPS web app using a maintained Android WebView/TWA framework, implement Google Play Billing and server-side purchase validation, set up privacy policy and data deletion, test on real devices, sign an AAB and complete Play Console review. This package does not include a compiled APK/AAB.
