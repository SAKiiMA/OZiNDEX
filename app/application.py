from flask import Flask, url_for, render_template, Session
from flask_session import Session

from tempfile import mkdtemp

# see addfunc.py for helpper functions
from addfunc import error

app = Flask(__name__)

"""App configurations"""
app.config["SECRET_KEY"] = 'development'
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")


"""Handling errors"""
@app.errorhandler(Exception)
def exception(e):
    return error(e.name, e.code)
