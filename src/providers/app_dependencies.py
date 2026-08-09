from src.config import create_session_factory, AppDependencies, create_engine, settings


def create_app_dependencies() -> AppDependencies:

    engine = create_engine(settings.db.url)
    session_factory = create_session_factory(engine)

    return AppDependencies(
        engine=engine,
        session_factory=session_factory,
    )
