import os

from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer, String, Boolean, Text, DateTime
from sqlalchemy.pool import StaticPool

from datetime import datetime


__all__ = [
    "Model",
    "Account",
    "Question",
    ]


class Model:
    meta = None  # Table 集合, 只是 Initial
    engine = None # 存放連結 Database 的資訊, 只是 Initial
    conn = None  # 與 Database 的連結, 透過這個下 SQL 指令, 只是 Initial

    @classmethod
    def start_engine(cls, db_uri=None):
        """Intial Database 連結的資訊"""

        if db_uri is None or db_uri == "sqlite:///:memory:":
            cls.engine = create_engine(
                "sqlite:///:memory:",
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                )
        else:
            cls.engine = create_engine(db_uri)

    @classmethod
    def initial_meta(cls):
        cls.meta = MetaData()  # 紀錄 Database 有什麼

        Account.register(cls.meta)  # 把 Account 註冊到 Meta
        Question.register(cls.meta)  # 把 Question 註冊到 Meta

        cls.meta.create_all(cls.engine)
    
    @classmethod
    def connect(cls):
        """開始與 Database 的連結"""

        cls.conn = cls.engine.connect()
        return cls.conn
    
    @classmethod
    def disconnect(cls):
        """結束語 Database 的連結"""

        if cls.conn is not None:
            cls.conn.close()
            cls.conn = None


class Account:
    NAME = "tb-account" # Table 名字
    T = None # Table instance

    @classmethod
    def register(cls, meta):
        cls.T = Table(
            cls.NAME,
            meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("login_id", String, nullable=False, autoincrement=False,
                   unique=True), # NOT NULL
            Column("password", String, nullable=False, autoincrement=False),
            Column("create_at", DateTime, default=datetime.utcnow,
                   autoincrement=True),
            )


class Question:
    NAME = "tb-question"
    T = None

    @classmethod
    def register(cls, meta):
        cls.T = Table(
            cls.NAME,
            meta,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("title", String, nullable=False, autoincrement=False),
            Column("content", Text, nullable=False, autoincrement=False),
            Column("writer", String, nullable=False, autoincrement=False),  # 不是 FK
            # Column("writer", Integer, ForeignKey("tb-account.id")),
            Column("create_at", DateTime, default=datetime.now,
                   autoincrement=True),
            )


if __name__ == "__main__":
    Model.start_engine("sqlite:///test.db")
    Model.initial_meta()

    if os.path.isfile("test.db"):
        os.remove("test.db")
