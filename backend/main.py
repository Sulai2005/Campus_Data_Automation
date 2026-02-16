from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from database.db import engine
from database import models

# Import routers
from routers import auth, admin, students, reports, requests

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

app = FastAPI(
    title="Campus Data Workflow Automation System",
    version="1.0.0",
    description="Module-1 Prototype: Authentication & RBAC"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files pointing to frontend directory
# Get the parent directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mount static files (CSS, JS)
app.mount("/styles", StaticFiles(directory=os.path.join(FRONTEND_DIR, "styles")), name="styles")
app.mount("/scripts", StaticFiles(directory=os.path.join(FRONTEND_DIR, "scripts")), name="scripts")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "public"))

# Register API routers (all under /api prefix to avoid conflicts)
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(requests.router, prefix="/api")

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Frontend routes - serve HTML pages
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    """Serve admin dashboard page"""
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@app.get("/admin/upload", response_class=HTMLResponse)
async def admin_upload_page(request: Request):
    """Serve admin upload page"""
    return templates.TemplateResponse("admin/upload.html", {"request": request})


@app.get("/admin/students", response_class=HTMLResponse)
async def admin_students_page(request: Request):
    """Serve admin students page"""
    return templates.TemplateResponse("admin/students.html", {"request": request})


@app.get("/admin/reports", response_class=HTMLResponse)
async def admin_reports_page(request: Request):
    """Serve admin reports page"""
    return templates.TemplateResponse("admin/reports.html", {"request": request})


@app.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard_page(request: Request):
    """Serve student dashboard page"""
    return templates.TemplateResponse("student/dashboard.html", {"request": request})


@app.get("/student/requests", response_class=HTMLResponse)
async def student_requests_page(request: Request):
    """Serve student requests page"""
    return templates.TemplateResponse("student/requests.html", {"request": request})


@app.get("/admin/requests", response_class=HTMLResponse)
async def admin_requests_page(request: Request):
    """Serve admin requests page"""
    return templates.TemplateResponse("admin/requests.html", {"request": request})


# API status endpoint
@app.get("/api/status")
def api_status():
    return {
        "status": "Backend running",
        "module": "Module-1: Authentication & RBAC",
        "database": "SQLite",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }
