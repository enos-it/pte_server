from functools import lru_cache
from urllib.parse import quote_plus
from sqlalchemy import BigInteger, create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.mysql import DOUBLE

Base = declarative_base()


class Site(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class Group(Base):
    __tablename__ = 'meter_groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class SubGroup(Base):
    __tablename__ = 'subgroups'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class Unit(Base):
    __tablename__ = 'units'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class MeterName(Base):
    __tablename__ = 'meter_names'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


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
    siteId = Column(Integer, ForeignKey('sites.id'), nullable=False)
    groupId = Column(Integer, ForeignKey('meter_groups.id'), nullable=False)
    subGroupId = Column(Integer, ForeignKey('subgroups.id'), nullable=False)
    unitId = Column(Integer, ForeignKey('units.id'), nullable=False)
    meterNameId = Column(Integer, ForeignKey('meter_names.id'), nullable=False)
    value = Column(DOUBLE, nullable=False)
    timestampMs = Column(BigInteger, nullable=False)
    enteredBy = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Measures(id={self.id}, OID='{self.OID}', siteId={self.siteId}, groupId={self.groupId}, subGroupId={self.subGroupId}, unitId={self.unitId}, meterNameId={self.meterNameId}, value={self.value}, timestampMs={self.timestampMs}, enteredBy='{self.enteredBy}')>"