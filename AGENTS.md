# Repository Guidelines

## Project Structure & Module Organization
- `main.py` is the uvicorn entrypoint that re-exports the FastAPI app.
- `app/main.py` builds the FastAPI app, wiring routers and shared state.
- `app/api/routes/` holds modular routers (auth, sync, attachments, health); add new endpoints here.
- `app/services/` contains request-agnostic business logic; prefer adding logic here instead of in routers.
- `app/schemas/` defines Pydantic request/response models and shared error envelopes.
- `app/state.py` currently provides an in-memory store; swap this for a real data layer when needed.
- `Pipfile` pins Python 3.10; add runtime and dev dependencies here so `pipenv` produces a reproducible environment.
- `test_main.http` contains example requests for manual checks via an HTTP client (e.g., VS Code REST Client); update it when adding endpoints.
- `.idea/` holds editor settings; avoid committing user-specific changes unless they benefit the team.

## Build, Test, and Development Commands
- Install tooling: `pipenv install fastapi uvicorn` (add `pytest` when introducing automated tests). `pipenv shell` enters the virtualenv.
- Run the app locally: `pipenv run uvicorn main:app --reload --port 8000` (hot reload for development).
- Quick endpoint check: `pipenv run curl http://127.0.0.1:8000/hello/YourName` or use requests in `test_main.http`.
- Once tests exist: `pipenv run pytest` for the suite; add `--maxfail=1 -q` for faster feedback.

## Coding Style & Naming Conventions
- Target Python 3.10 with PEP 8 formatting (4-space indents, snake_case functions/variables, CapWords classes).
- Prefer type hints on route signatures and helpers; keep FastAPI response models explicit when added.
- Use small, single-purpose functions; group related routes logically and prefix paths consistently.
- Keep imports sorted standard-library → third-party → local; avoid unused imports to reduce startup time warnings.

## Testing Guidelines
- Place tests under `tests/` mirroring the module structure; name files `test_*.py` and functions `test_*`.
- Aim for coverage of route behaviors, status codes, and payload validation; include negative cases (missing params, bad data).
- For manual smoke tests, refresh `test_main.http` with sample payloads and expected responses.

## Commit & Pull Request Guidelines
- Commits: use short, imperative subjects (e.g., `Add hello route`, `Document local run steps`); group related changes logically.
- PRs: describe intent, key changes, and verification steps (commands run, screenshots of responses if UI/API behavior changes).
- Link related issues or tasks; call out breaking changes or new environment variables in the description.
- When staging for a commit, prefer `git add .` to include relevant changes instead of listing files individually.
