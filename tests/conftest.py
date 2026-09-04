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
        session_factory = async_sessionmaker(bind=connection, expire_on_commit=False)
        session = session_factory()

        # Every test (and the app code it exercises through the FastAPI
        # dependency override) shares this single connection/transaction,
        # rolled back wholesale at teardown -- so a real commit() is never
        # needed for writes to be visible to later queries in the same test,
        # a flush() already gives that (same connection, same transaction).
        # Faking commit() as flush() sidesteps SAVEPOINT-per-commit isolation
        # entirely: both a hand-rolled restart-savepoint-on-commit listener
        # and SQLAlchemy's own built-in "conditional_savepoint" join mode
        # (the alternative, more "correct" ways to let real nested commits
        # happen) intermittently raise MissingGreenlet with the asyncmy
        # driver. Real rollback() (e.g. forms.py catching IntegrityError) is
        # left untouched -- the DB requires a real rollback after a failed
        # statement before the connection can be used again, and since we
        # never issue a real commit either, nothing it ends is ever actually
        # persisted: the connection is dropped unpersisted at teardown either
        # way.
        async def _commit_as_flush() -> None:
            await session.flush()

        session.commit = _commit_as_flush

        try:
            yield session
        finally:
            await session.close()
            if outer_transaction.is_active:
                await outer_transaction.rollback()
    await engine.dispose()
