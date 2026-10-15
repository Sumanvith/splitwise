import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.config import settings
from app.database import Base, get_db  # GUESS: Base and get_db live in app/database.py
from app.models import user, group, expense, settlement  # noqa: F401  (register tables on Base.metadata)

# GUESS: settings.DATABASE_URL is the asyncpg URL ending in /<dbname>
TEST_DATABASE_URL = settings.database_url.rsplit("/", 1)[0] + "/splitwise_test"


@pytest.fixture
async def client():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    await engine.dispose()