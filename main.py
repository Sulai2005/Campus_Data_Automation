from fastapi import FastAPI

from database.db import engine
from database import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Campus Data Workflow Automation System",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "status": "Backend running",
        "module": "Foundation",
        "database": "SQLite"
    }
