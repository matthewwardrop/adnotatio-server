from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .models import Base


def init_db(db='sqlite:///::memory::'):

    if isinstance(db, str):
        db = create_engine(db, convert_unicode=True)
    if isinstance(db, Engine):
        db = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=db))

    Base.metadata.create_all(bind=db.session_factory.kw['bind'])
    return db
