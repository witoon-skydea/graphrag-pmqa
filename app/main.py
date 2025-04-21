import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.graph_db import graph_db, close_db_connection as close_graph_db
from app.db.vector_db import vector_db, close_db_connection as close_vector_db

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Import and include API routers
from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.claude import router as claude_router
from app.api.pmqa import router as pmqa_router

app.include_router(documents_router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])
app.include_router(search_router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
app.include_router(claude_router, prefix=f"{settings.API_V1_STR}/claude", tags=["claude"])
app.include_router(pmqa_router, prefix=f"{settings.API_V1_STR}/pmqa", tags=["pmqa"])

@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to GraphRAG PMQA API", "status": "online"}

@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    """
    Health check endpoint to verify all services are running.
    """
    health_status = {
        "api": "healthy",
        "neo4j": "unknown",
        "chroma": "unknown",
    }
    
    # Check Neo4j connection
    try:
        with graph_db.get_session() as session:
            result = session.run("RETURN 1 as test")
            test_value = result.single()["test"]
            if test_value == 1:
                health_status["neo4j"] = "healthy"
            else:
                health_status["neo4j"] = "unhealthy"
    except Exception as e:
        health_status["neo4j"] = f"unhealthy: {str(e)}"
    
    # Check ChromaDB connection
    try:
        # Simple check to see if we can list collections
        collections = vector_db.client.list_collections()
        health_status["chroma"] = "healthy"
    except Exception as e:
        health_status["chroma"] = f"unhealthy: {str(e)}"
    
    # Determine overall status
    if all(value == "healthy" for value in health_status.values()):
        overall_status = "healthy"
    else:
        overall_status = "unhealthy"
        
    return {
        "status": overall_status,
        "services": health_status,
        "timestamp": "current_timestamp"  # Will be replaced with actual timestamp in production
    }

# Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Actions to run on application startup.
    """
    # This is where we would initialize resources that need to be available at startup
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to run on application shutdown.
    """
    # Close database connections
    close_graph_db()
    close_vector_db()

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="GraphRAG API for PMQA 4.0",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Run the application directly if this file is executed
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
