# api/main.py
from fastapi import FastAPI

# Routers (package-absolute imports)
from api.routers.ask import router as ask_router
from api.routers.brief import router as brief_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="TruthRun API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/healthz", tags=["ops"])
    def healthz():
        return {"status": "ok"}

    # Include routes
    app.include_router(ask_router)  # GET /ask
    app.include_router(brief_router)  # GET /brief

    return app


app = create_app()
