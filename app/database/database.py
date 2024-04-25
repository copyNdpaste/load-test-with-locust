from dotenv import load_dotenv

load_dotenv(verbose=True)

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from log.log import logger

DB_USER = os.getenv("DB_USER")
DB_PW = os.getenv("DB_PW")
DB_PORT = os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

READ_DB_HOST = os.getenv("READ_DB_HOST")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

READ_SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PW}@{READ_DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

replica_engine = create_engine(
    READ_SQLALCHEMY_DATABASE_URL,
    encoding="utf-8",
    pool_size=100,
    max_overflow=50,
    pool_recycle=30 * 60,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 30},
)
ReplicaSession = scoped_session(
    sessionmaker(autocommit=True, autoflush=True, bind=replica_engine)
)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=250,
    max_overflow=20,
    pool_recycle=30 * 60,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 30},
)
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def get_read_session():
    session = ReplicaSession()
    logger.debug(f"session : {session}")
    try:
        yield session
        logger.debug(f"after yield")
    except Exception as e:
        session.rollback()
        logger.error(f"get_read_session e : {e}")
    finally:
        session.close()


def get_session():
    session = Session()
    yield session

    try:
        logger.info("get_session commit start")
        session.commit()
        logger.info("get_session commit end")
    except Exception as e:
        logger.error(f"get_session rollback e : {e}")
        session.rollback()
    finally:
        logger.info("get_session close")
        session.close()


read_session = next(get_read_session())
session = next(get_session())
Base = declarative_base()
