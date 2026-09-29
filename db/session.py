from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from tool.yaml_utils import get_app_config

_conf = get_app_config("mysql_pulse_conf")

_engine = create_engine(
    f"mysql+pymysql://{_conf['user']}:{_conf['password']}@{_conf['host']}:{_conf['port']}/{_conf['database']}?charset=utf8mb4",
    pool_pre_ping=True,
)

_SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


# 给脚本使用
def create_session() -> Session:
    return _SessionLocal()


def get_db() -> Generator[Session, None, None]:
    db = _SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
