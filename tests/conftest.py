import pytest
from sqlalchemy import event
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
        session_factory = async_sessionmaker(bind=connection, expire_on_commit=False)
        session = session_factory()

        # session.commit() ends the outer (real) transaction by default, which
        # would make every commit permanent and turn the final rollback below
        # into a no-op on an already-finished transaction. The fix (SQLAlchemy's
        # own documented pattern for this): run everything inside a SAVEPOINT,
        # and transparently restart a new one each time the current one ends
        # (i.e. on every session.commit()/rollback()) so nested commits stay
        # nested no matter how many the test code issues.
        nested = await connection.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def _restart_savepoint(sync_session, transaction):
            nonlocal nested
            if not nested.is_active:
                nested = connection.sync_connection.begin_nested()

        try:
            yield session
        finally:
            await session.close()
            if outer_transaction.is_active:
                await outer_transaction.rollback()
    await engine.dispose()
