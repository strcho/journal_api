from app.main import app, create_app

# Re-export FastAPI app for `uvicorn main:app`.
__all__ = ["app", "create_app"]


if __name__ == "__main__":
    import uvicorn

    # Use main_v2 for production with MongoDB/Redis support
    uvicorn.run("app.main_v2:app", host="0.0.0.0", port=8000, reload=True)
