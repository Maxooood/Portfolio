from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    from app.models.base import Base
    # Import all models so they are registered on Base.metadata
    import app.models.user  # noqa
    import app.models.equipment  # noqa
    import app.models.ppr  # noqa
    import app.models.request  # noqa
    import app.models.work  # noqa
    import app.models.report  # noqa
    import app.models.service  # noqa
    import app.models.audit  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
