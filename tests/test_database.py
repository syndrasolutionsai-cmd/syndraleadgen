import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from leadforge.database import get_db, engine


@pytest.mark.asyncio
async def test_engine_connects():
    async with engine.connect() as conn:
        result = await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_db_yields_session():
    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    await gen.aclose()
