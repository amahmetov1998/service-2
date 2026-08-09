from dataclasses import dataclass

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine


@dataclass
class AppDependencies:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
