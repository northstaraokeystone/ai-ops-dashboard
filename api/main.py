from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# CORRECTED: Use relative import to correctly find the routers directory
from .routers import integrity, gpu, roi, interaction  # <--- FIXED TYPO HERE
from api.core.config import settings

app = FastAPI(
    title="AI Operations API",
    description="ML monitoring APIs: integrity, GPU efficiency, ROI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(integrity.router)
app.include_router(gpu.router)
app.include_router(roi.router)
app.include_router(interaction.router)


@app.get("/")
async def root():
    return {"message": "AI Operations API", "version": "1.0.0"}


@app.get("/health")
async def health():
    secrets_loaded = bool(settings.naok_fulcrum_prime_key)
    return {"status": "healthy", "secrets_loaded": secrets_loaded}
