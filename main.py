import os
import jinja2
import cherrypy
import hashlib
import sqlalchemy

from datetime import datetime
from sqlalchemy import Table, Column
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import select


dirname = os.path.join(os.path.dirname(__file__), "server/template")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dirname))

Base = declarative_base()


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    login_id = Column(String)
    password = Column(String)
    create_at = Column(DateTime, default=datetime.utcnow)


engine = sqlalchemy.create_engine("sqlite:///server.db")
Base.metadata.create_all(engine)


def sha256(password):
    return hashlib.sha256(password.encode()).hexdigest()


# App
class App:
    @staticmethod
    def render(src, **params):
        return jinja_env.get_template(src).render(params)

    @cherrypy.expose  # function 名字跟 URL 有關
    def index(self, form_type=None, login_id=None, password=None):  # index = "/"
        if cherrypy.request.method == "GET":
            login_cookie = cherrypy.request.cookie.get("login_id")

            if login_cookie is not None:
                return self.render(
                    "index.html",
                    login_id=login_cookie.value)

            return self.render("index.html")
        
        elif cherrypy.request.method == "POST":
            password = sha256(password)

            if form_type == "login":
                return self.handle_login(login_id, password)
            else:
                return self.handle_signup(login_id, password)

    def handle_login(self, login_id, password):
        conn = engine.connect()

        rst = conn.execute(select([Account.__table__]).where(
            Account.__table__.c.login_id == login_id))
        row = rst.fetchone()

        if row is None:
            conn.close()
            return self.render("index.html", login_wrong=True)
        if row["password"] != password:
            conn.close()
            return self.render("index.html", login_wrong=True)
        
        conn.close()

        cherrypy.response.cookie["login_id"] = login_id
        cherrypy.response.cookie["login_id"]["path"] = "/"
        cherrypy.response.cookie["login_id"]["max-age"] = 3600

        raise cherrypy.HTTPRedirect("/")

    def handle_signup(self, login_id, password):
        conn = engine.connect()

        ss = select([Account.__table__]).where(
            Account.__table__.c.login_id == login_id)
        rst = conn.execute(ss)

        row = rst.fetchone()
        
        if row is not None:
            conn.close()
            return self.render("index.html", signup_wrong=True)

        conn.execute(Account.__table__.insert(), {
            "login_id": login_id,
            "password": password,
        })

        conn.close()

        cherrypy.response.cookie["login_id"] = login_id
        cherrypy.response.cookie["login_id"]["path"] = "/"
        cherrypy.response.cookie["login_id"]["max-age"] = 3600

        raise cherrypy.HTTPRedirect("/")
    
    @cherrypy.expose
    def logout(self):
        login_cookie = cherrypy.request.cookie.get("login_id")

        if login_cookie is not None:
            cherrypy.response.cookie["login_id"] = ""
            cherrypy.response.cookie["login_id"]["expires"] = 0

        raise cherrypy.HTTPRedirect("/")


if __name__ == "__main__":
    cherrypy.quickstart(App(), "/", {
        "/": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": os.path.join(os.getcwd(), "server", "static"),
        }
    })
