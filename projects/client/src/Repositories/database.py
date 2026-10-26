from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import config


class Database:
    def __init__(self):
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )

    def _create_engine(self):
        database_url = (
            f"postgresql+psycopg2://{config.db_username}:"
            f"{config.db_password}@"
            f"{config.db_host}:"
            f"{config.db_port}/"
            f"{config.db_name}"
        )
        return create_engine(database_url)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# -------------------------------------------------------------------
# Single shared database instance (IMPORTANT)
# -------------------------------------------------------------------
database = Database()

# Expose commonly used objects
engine = database.engine
SessionLocal = database.SessionLocal
get_db = database.get_db