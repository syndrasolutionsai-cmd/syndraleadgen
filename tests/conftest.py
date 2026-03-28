import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport
from leadforge.api.main import app
from leadforge.api.deps import get_db
from leadforge.database import Base

TEST_DB_URL = "postgresql+asyncpg://leadforge:leadforge@localhost:5432/leadforge_test"

@pytest.fixture(scope="session")
def event_loop_policy():
    import asyncio
    return asyncio.DefaultEventLoopPolicy()

@pytest_asyncio.fixture(scope="session")
async def setup_db():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(setup_db):
    engine = setup_db
    async with engine.connect() as conn:
        await conn.begin()
        session_factory = async_sessionmaker(bind=conn, expire_on_commit=False)
        async with session_factory() as session:
            await conn.begin_nested()  # SAVEPOINT
            yield session
            await conn.rollback()  # rolls back to SAVEPOINT (and outer transaction)

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
