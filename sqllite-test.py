import sqlalchemy

from datetime import datetime
from sqlalchemy import Table, Column
from sqlalchemy.types import Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    login_id = Column(String)
    password = Column(String)
    create_at = Column(DateTime, default=datetime.utcnow)


engine = sqlalchemy.create_engine("sqlite:///john.db")

Base.metadata.create_all(engine)



conn = engine.connect()

acc_insert = [
    {
        "login_id": "michael",
        "password": "panpan",
    },

    {
        "login_id": "john",
        "password": "john",
    }
]

conn.execute(Account.__table__.insert(), acc_insert)

conn.close()

engine.dispose()