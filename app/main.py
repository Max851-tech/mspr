"""FastAPI application entry point with OpenAPI configuration."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, exercises, foods, users
from app.api.routes.admin import exercises as admin_exercises
from app.api.routes.admin import foods as admin_foods
from app.api.routes.admin import users as admin_users

# OpenAPI tag metadata for documentation
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. Create, read, update, delete user accounts and profiles.",
    },
    {
        "name": "auth",
        "description": "Authentication: login (JWT) and current user.",
    },
    {
        "name": "admin",
        "description": "Admin-only operations. List all users, export data, view statistics.",
    },
    {
        "name": "foods",
        "description": "Search and browse food reference data. Public endpoints with fuzzy search and category filtering.",
    },
    {
        "name": "admin-foods",
        "description": "Admin operations for food management. CRUD, soft delete, restore, bulk operations, and audit trail.",
    },
    {
        "name": "exercises",
        "description": "Search and browse exercise reference data. Public endpoints with fuzzy search and multi-field filtering.",
    },
    {
        "name": "admin-exercises",
        "description": "Admin operations for exercise management. CRUD, soft delete, restore, bulk operations, and audit trail.",
    },
]

# Create FastAPI application instance
app = FastAPI(
    title="HealthAI Coach API",
    description="Backend API for health and fitness tracking platform.",
    version="0.1.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
if _origins:
    _cors_origins = [o.strip() for o in _origins.split(",") if o.strip()]
else:
    _cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin_users.router)
app.include_router(foods.router)
app.include_router(admin_foods.router)
app.include_router(exercises.router)
app.include_router(admin_exercises.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint returning API info."""
    return {
        "message": "HealthAI Coach API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["root"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
