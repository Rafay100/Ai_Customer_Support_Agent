from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import database
from app.db.database import engine, Base

# Import routes
from app.api import routes

# Create database tables
Base.metadata.create_all(bind=engine)

# Create app
app = FastAPI(
    title="AI Customer Support Agent",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get static directory
STATIC_DIR = Path(__file__).parent / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include API routes
app.include_router(routes.router, prefix="/api")

# Root - serve UI
@app.get("/")
async def root():
    try:
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
        return HTMLResponse("<h1>UI not found</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
