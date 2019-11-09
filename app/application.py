from flask import Flask, url_for, render_template, session, request
from flask_session import Session
from werkzeug.exceptions import HTTPException, InternalServerError

from tempfile import mkdtemp

# see utils.py for utility functions
from utils import errorfeedback, genchart, get_df


app = Flask(__name__)

"""App configurations"""
app.config["SECRET_KEY"] = 'development'
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# loading data as a panda's dataframe
df = get_df()


@app.route("/" , methods=['GET'])
def index():
    return render_template("index.html")


@app.route("/option", methods=['GET'])
def option():
    """ return charts based on user selected option """
    return genchart(request.args.get("option"), df)



"""Handling errors"""
@app.errorhandler(Exception)
def exception(e):
    if  isinstance(e, HTTPException):
        return errorfeedback(e.name, e.code, e.description)
    else:
        e = InternalServerError()
        return errorfeedback(e.name, e.code, e.description)
