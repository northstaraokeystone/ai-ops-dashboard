# api/main.py
from fastapi import FastAPI, Body, Header, status

# Routers
from api.routers.ask import router as ask_router
from api.routers.brief import router as brief_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="TruthRun API", version="0.1.0", docs_url="/docs", redoc_url="/redoc"
    )

    # Health & root expected by tests
    @app.get("/", tags=["ops"])
    def root():
        return {"status": "ok"}

    @app.get("/health", tags=["ops"])
    def health():
        return {"status": "ok"}

    @app.get("/healthz", tags=["ops"])
    def healthz():
        return {"status": "ok"}

    # Minimal idempotency endpoint for tests
    _store = {}

    @app.post("/interaction", status_code=status.HTTP_201_CREATED, tags=["ops"])
    def interaction(item: dict = Body(...), idempotency_key: str | None = Header(None)):
        key = idempotency_key or item.get("id") or "default"
        if key in _store:
            return {"status": "already_exists", "idempotency_key": key}
        _store[key] = item
        return {"status": "created", "idempotency_key": key}

    # Include existing routes
    app.include_router(ask_router)  # GET /ask
    app.include_router(brief_router)  # GET /brief
    return app


app = create_app()
