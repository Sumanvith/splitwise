from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.config import settings
from app.database import get_db

from app.routers import auth, groups, expenses, settlements

app = FastAPI(title=settings.project_name)
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(expenses.router)
app.include_router(settlements.router)


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "project": settings.project_name, "message": "Database connected successfully"}
