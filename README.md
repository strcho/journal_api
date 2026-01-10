# Journal API

FastAPI demo backend matching the draft sync API from the Flutter journal app. Implements auth, sync push/pull, and attachment upload/download with in-memory stores for quick prototyping.

## Prerequisites
- Python 3.10
- pipenv

## Setup
```sh
pipenv install
```

## Run
```sh
pipenv run uvicorn main:app --reload --port 8000
```

## Project Structure
- `main.py` – uvicorn entry that exposes the FastAPI app.
- `app/main.py` – app factory that wires routers and shared state.
- `app/api/routes/` – modular routers for auth, sync, attachments, and health checks.
- `app/services/` – request-agnostic business logic for auth, sync, and attachments.
- `app/schemas/` – Pydantic request/response models and shared error envelopes.
- `app/state.py` – in-memory store backing the demo implementation.

## Development
- Start the server: `pipenv run uvicorn main:app --reload --port 8000`
- Hot reload is enabled; edit code under `app/` and refresh requests.
- The app uses an in-memory store; data resets on restart. Swap `InMemoryStore` for a real data layer when ready.

## API Overview
- `POST /auth/login` – returns `accessToken`, `refreshToken`, and `deviceId` (accepts any credentials for now).
- `POST /auth/refresh` – exchanges a refresh token + deviceId for new tokens.
- `POST /sync/push` – push entries and attachment metadata; tracks revisions, reports conflicts/missingAttachments.
- `GET /sync/changes?since=<rev>` – pull changes newer than a revision.
- `PUT /attachments/{id}` – upload encrypted attachment content (octet-stream).
- `GET /attachments/{id}` – download attachment content.

All sync and attachment routes require `Authorization: Bearer <accessToken>`.

## Quickstart (manual)
Sample requests are in `test_main.http`. With the server running:
1. Login to get tokens.
2. Push entries + attachment metadata.
3. Upload attachment content.
4. Pull changes to verify revisions.
5. Download attachment.

## Notes
- Storage is in-memory only; data resets on restart.
- Conflict handling is last-write-wins based on server revision.
- Update `test_main.http` alongside new endpoints for easy manual checks.
