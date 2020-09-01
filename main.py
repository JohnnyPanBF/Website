import hashlib
import os

import cherrypy
import jinja2
import MyDB

dir_name = os.path.join(os.path.dirname(__file__), "server/template")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir_name))


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

            print(login_cookie)
            if login_cookie is not None:
                raise cherrypy.HTTPRedirect("/question")

            return self.render("index.html")

        elif cherrypy.request.method == "POST":
            password = sha256(password)

            print(form_type)
            if form_type == "login":
                return self.handle_login(login_id, password)
            else:
                return self.handle_signup(login_id, password)

    def handle_login(self, login_id, password):

        if MyDB.Account.login(login_id, password) is False:
            return self.render("index.html", login_wrong=True)

        cherrypy.response.cookie["login_id"] = login_id
        cherrypy.response.cookie["login_id"]["path"] = "/"
        cherrypy.response.cookie["login_id"]["max-age"] = 3600

        raise cherrypy.HTTPRedirect("/question")

    def handle_signup(self, login_id, password):

        if MyDB.Account.insert_db(login_id, password) is False:
            return self.render("index.html", signup_wrong=True)

        cherrypy.response.cookie["login_id"] = login_id
        cherrypy.response.cookie["login_id"]["path"] = "/"
        cherrypy.response.cookie["login_id"]["max-age"] = 3600

        raise cherrypy.HTTPRedirect("/question")

    @cherrypy.expose
    def logout(self):
        login_cookie = cherrypy.request.cookie.get("login_id")

        if login_cookie is not None:
            cherrypy.response.cookie["login_id"] = ""
            cherrypy.response.cookie["login_id"]["expires"] = 0

        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def question(self, title=None, content=None):
        if cherrypy.request.method == 'GET':
            login_cookie = cherrypy.request.cookie.get("login_id")

            if login_cookie is None:
                raise cherrypy.HTTPRedirect("/")

            q_all = MyDB.Question.find()
            for i in q_all:
                print(i)
            return self.render('question.html', q_all=q_all)
        elif cherrypy.request.method == "POST":
            login_cookie = cherrypy.request.cookie.get("login_id")
            print(login_cookie)
            print(login_cookie.value)
            MyDB.Question.insert_db(login_cookie.value, title, content)

            raise cherrypy.HTTPRedirect("/question")


if __name__ == "__main__":
    cherrypy.quickstart(App(), "/", {
        "/": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": os.path.join(os.getcwd(), "server", "static"),
        }
    })
