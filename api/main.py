from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import integrity, gpu, roi

app = FastAPI(
    title="AI Operations API",
    description="ML monitoring APIs: integrity, GPU efficiency, ROI",
    version="1.0.0"
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

@app.get("/")
async def root():
    return {
        "message": "AI Operations API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
