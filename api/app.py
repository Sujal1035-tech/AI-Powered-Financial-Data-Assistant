import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.search import router as search_router

app = FastAPI(
    title="AI Financial Data Assistant API",
    description="Semantic search and insights for financial transactions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_router, prefix="/api", tags=["search"])

@app.get("/")
async def root():
    return {
        "message": "AI Financial Data Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "transactions": "/api/transactions",
            "insights": "/api/insights"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)