from functools import lru_cache
from urllib.parse import quote_plus

from sqlalchemy import BigInteger, create_engine, Column, Integer, String, Text, DateTime, Enum, func, LargeBinary, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.mysql import DOUBLE
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


@lru_cache(maxsize=32)
def get_engine(host, user, password, database):
    """Return a cached SQLAlchemy engine for a given database configuration."""
    url = f'mysql+mysqlconnector://{quote_plus(user)}:{quote_plus(password)}@{host}/{database}'
    return create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=5,
        max_overflow=10,
    )


@lru_cache(maxsize=32)
def get_session_factory(host, user, password, database):
    """Return a cached session factory using a shared engine for the database."""
    engine = get_engine(host, user, password, database)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session(host, user, password, database):
    """Create a request-scoped database session from the shared factory."""
    return get_session_factory(host, user, password, database)()

class Measures(Base):
    __tablename__ = 'measures'

    id = Column(Integer, primary_key=True)
    OID = Column(String(255), nullable=False, unique=True)
    meterId = Column(String(255), nullable=False)
    value = Column(DOUBLE, nullable=False)
    timestampMs = Column(BigInteger, nullable=False)
    enteredBy = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Measures(id={self.id}, OID='{self.OID}', meterId='{self.meterId}', value={self.value}, timestampMs={self.timestampMs}, enteredBy='{self.enteredBy}')>"