import os
import jinja2
import cherrypy

from hashlib import sha256

try:
    from .model import Model, Account, Question
except ImportError:
    from model import Model, Account, Question

from sqlalchemy.sql import select, update, and_


__all__ = [
    "MainHandler",
    ]

dirname = os.path.join(os.path.dirname(__file__), "template")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dirname))


class MainHandler:
    @staticmethod
    def hash_pwd(password):
        return sha256(password.encode()).hexdigest()

    @classmethod
    def get_keys(cls, data, **kwargs):
        keys = {}

        for key, value in kwargs.items():
            if key not in data:
                raise False

            try:
                keys[key] = data[key]
            except ValueError:
                raise False

        return keys

    @staticmethod
    def render(src, **params):
        return jinja_env.get_template(src).render(params)
    
    @cherrypy.expose  # function 名字跟 URL 有關
    def index(self, **data):  # index = "/"
        print("index")


        if cherrypy.request.method == "GET":
            return self.render("index.html")

        elif cherrypy.request.method == "POST":
            keys = self.get_keys(
                data,
                type=str,
                login_id=str,
                password=str,
                )

            # 如果所有的參數都沒有, 就傳回 index.html
            if keys is False:
                return self.render("index.html")
            
            conn = Model.connect()
            




            # 利用 login_id 查詢 DB
            ss = select([Account.T]).where(
                Account.T.c.login_id == keys["login_id"])
            result = conn.execute(ss)
            row = result.fetchone()
            # 通常一個帳號只有一個, 







            if keys["type"] == "login":
                # 必須找到相對的 帳號ID
                if row is not None:
                    # 密碼需要與 DB 密碼相符
                    if row["password"] == self.hash_pwd(keys["password"]):
                        Model.disconnect()
                        raise cherrypy.HTTPRedirect("/login/" + keys["login_id"])

            elif keys["type"] == "signup":
                # 如果有帳號以重複, 不能創建新帳號, 就傳回 index.html
                if row is None:
                    conn.execute(
                        Account.T.insert(),
                        {
                            "login_id": keys["login_id"],
                            "password": self.hash_pwd(keys["password"]),
                            }
                        )

                    Model.disconnect()
                    raise cherrypy.HTTPRedirect("/login/" + keys["login_id"])

            Model.disconnect()
            return self.render("index.html")
    
    @cherrypy.expose
    def test(self):
        print("test")
        return "test"

    @cherrypy.expose
    def login(self, login_id, **data):
        print("Login")

        if cherrypy.request.method == "GET":
            conn = Model.connect()

            ss = select([Question.T])
            result = conn.execute(ss)
            rows = result.fetchall()
            
            questions_html = ""
            for row in rows:
                questions_html += str(row["id"]) + ",<br>"   # br == break line == \n
                questions_html += row["title"] + ",<br>"
                questions_html += row["content"].replace("\n", "<br>") + ",<br>"
                questions_html += row["writer"] + ",<br>"
                questions_html += row["create_at"].strftime("%b %d, %p %I %m") + ",<br>"
                questions_html += "<br><br>"

            Model.disconnect()

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>已登入</title>
</head>
<body>
    <h3>{login_id} 已登入</h3>
    {questions_html}
</body>
</html>"""

        return html

        if cherrypy.request.method == "POST":
            keys = self.get_keys(
                data,
                title=str,
                content=str,
                )

            # 如果所有的參數都沒有, 就什麼都不做
            if keys is False:
                raise cherrypy.HTTPRedirect("/login/" + login_id)

            conn = Model.connect()
            
            conn.execute(
                Question.T.insert(),
                {
                    "title": keys["title"],
                    "content": keys["content"],
                    "writer": login_id,
                }
            )

            Model.disconnect()
            raise cherrypy.HTTPRedirect("/login/" + login_id)



if __name__ == "__main__":
    cherrypy.quickstart(MainHandler(), "/")
