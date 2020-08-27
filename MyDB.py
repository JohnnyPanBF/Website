import sqlalchemy

from datetime import datetime
from sqlalchemy import Table, Column, select
from sqlalchemy.types import Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    login_id = Column(String)
    password = Column(String)
    create_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def insert_db(cls, login_id, password):

        if cls.check(login_id) is None:

            acc_insert = [
                {
                    "login_id": login_id,
                    "password": password,
                },
            ]

            DB.db_connect().execute(Account.__table__.insert(), acc_insert)
            DB.db_close()
            return True
        else:
            return False

    @classmethod
    def check(cls, login_id):
        ss = select([Account.__table__]).where(
            cls.login_id == login_id)
        result = DB.db_connect().execute(ss)

        row = result.fetchone()

        return row

    @classmethod
    def login(cls, login_id, password):

        row = cls.check(login_id)

        if row is None or row["password"] != password:
            DB.db_close()
            return False
        else:
            DB.db_close()
            return True


class DB:
    engine = sqlalchemy.create_engine("sqlite:///johnny.db")
    Base.metadata.create_all(engine)
    conn = None

    @classmethod
    def db_connect(cls):
        if cls.conn is None:
            cls.conn = cls.engine.connect()
            return cls.conn
        elif cls.conn is not None:
            return cls.conn

    @classmethod
    def db_close(cls):
        cls.conn.close()
        cls.conn = None


