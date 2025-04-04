from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now import the routers
from api.routers import scraping, visualization

app = FastAPI(
    title="ArXiv Papers API",
    description="API for managing ArXiv papers scraping and visualization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scraping.router, prefix="/api/scraping", tags=["scraping"])
app.include_router(visualization.router, prefix="/api/visualization", tags=["visualization"])

# Mount static files for visualization images
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
plots_dir = os.path.join(data_dir, "plots")
if os.path.exists(plots_dir):
    app.mount("/plots", StaticFiles(directory=plots_dir), name="plots")

@app.get("/")
async def root():
    return {"message": "Welcome to ArXiv Papers API. Go to /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)