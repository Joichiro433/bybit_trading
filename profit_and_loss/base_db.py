from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import constants
from logger import Logger

logger = Logger()

Base = declarative_base()
engine = create_engine(f'sqlite:///{constants.db_name}?check_same_thread=False')
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(e)
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    import profit_and_loss.pl_record
    Base.metadata.create_all(bind=engine)