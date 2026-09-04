import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.rate_limit import limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    # The Limiter singleton (app/core/rate_limit.py) persists its in-memory
    # counters across tests within the same process. Without a reset, tests
    # that call the same now-rate-limited endpoint (3/min on public forms,
    # 30/min on admin routes, etc.) more than a few times across the whole
    # suite start seeing 429s that have nothing to do with what they're
    # actually testing.
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine(get_settings().database_url)
    async with engine.connect() as connection:
        outer_transaction = await connection.begin()
        # Session.join_transaction_mode defaults to "conditional_savepoint"
        # (SQLAlchemy 2.0): binding the session to a connection that already
        # has an open transaction makes it automatically open/restart its own
        # SAVEPOINT around every commit()/rollback(), so session.commit()
        # calls made by test or application code never touch -- let alone
        # end -- the outer transaction below. No manual savepoint bookkeeping
        # needed; a hand-rolled version of this (event listener restarting a
        # SAVEPOINT via connection.sync_connection) used to live here and
        # fought with this built-in behavior, causing intermittent
        # MissingGreenlet errors on the second nested commit.
        session_factory = async_sessionmaker(bind=connection, expire_on_commit=False)
        session = session_factory()

        try:
            yield session
        finally:
            await session.close()
            if outer_transaction.is_active:
                await outer_transaction.rollback()
    await engine.dispose()
