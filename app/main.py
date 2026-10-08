from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import get_db

from app.routers import auth

app = FastAPI(title=settings.project_name)
app.include_router(auth.router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "project": settings.project_name, "message": "Database connected successfully"}
