
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.connection import Base, engine

# Import models before creating database tables.
from app.models import User, Task, Execution

# Import API routers.
from app.api.routes.auth import router as auth_router
from app.api.routes.generate import router as generate_router
from app.api.routes.execute import router as execute_router
from app.api.routes.tasks import router as tasks_router

# Create database tables.
Base.metadata.create_all(bind=engine)


# Initialize FastAPI application.
app = FastAPI(
    title=settings.app_name,
    description="Secure AI-generated code execution platform.",
    version="1.0.0",
)


# Configure CORS.
origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# Register API routers.
app.include_router(auth_router, prefix="/api/v1")
app.include_router(generate_router, prefix="/api/v1")
app.include_router(execute_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")

# Health check endpoint.
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": "1.0.0",
    }


# Root endpoint.
@app.get("/")
def root():
    return {
        "message": "Welcome to ProofRun API",
        "docs": "/docs",
    }
