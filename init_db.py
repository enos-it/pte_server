from pathlib import Path

from sqlalchemy import inspect, select

from app import db_host, db_user, db_password, db_name
from model import Base, Group, Site, SubGroup, Unit, get_engine


def initialize_database(engine):
    sql = Path(__file__).with_name("reference_data.sql").read_text(encoding="utf-8")
    if not sql.strip():
        raise RuntimeError("reference_data.sql is empty")

    with engine.begin() as connection:
        for table_name in inspect(connection).get_table_names():
            if connection.dialect.name == "sqlite" and table_name == "sqlite_sequence":
                continue
            quoted_name = connection.dialect.identifier_preparer.quote(table_name)
            if connection.exec_driver_sql(f"SELECT 1 FROM {quoted_name} LIMIT 1").first():
                raise RuntimeError(f"Database is not empty: table {table_name} contains data")

        Base.metadata.create_all(connection)
        for statement in sql.split(";"):
            if statement.strip():
                connection.exec_driver_sql(statement)

        for model in (Site, Group, SubGroup, Unit):
            ids = connection.execute(select(model.id).order_by(model.id)).scalars().all()
            if not ids or ids != list(range(1, len(ids) + 1)):
                raise RuntimeError(f"Unexpected reference IDs in {model.__tablename__}; use a fresh database")


if __name__ == "__main__":
    engine = get_engine(db_host, db_user, db_password, db_name)
    initialize_database(engine)
    print("Database tables and reference data initialized successfully.")
