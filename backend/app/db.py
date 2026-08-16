from sqlmodel import SQLModel, Session, create_engine

from app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
    if DATABASE_URL.startswith("sqlite"):
        with engine.begin() as conn:
            columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(game)")}
            if "skill_level" not in columns:
                conn.exec_driver_sql("ALTER TABLE game ADD COLUMN skill_level INTEGER")
            if "human_color" not in columns:
                conn.exec_driver_sql("ALTER TABLE game ADD COLUMN human_color VARCHAR")


def get_session():
    with Session(engine) as session:
        yield session
