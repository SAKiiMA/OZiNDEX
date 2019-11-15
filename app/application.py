from flask import Flask, url_for, render_template, session, request
from flask_session import Session
from werkzeug.exceptions import HTTPException, InternalServerError

from tempfile import mkdtemp

# see utils.py for utility functions
from utils import errorfeedback, genchart, get_df, country_chart


app = Flask(__name__)

"""App configurations"""
app.config["SECRET_KEY"] = 'development'
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# loading data as a panda's dataframe
df = get_df()


@app.route("/" , methods=['GET'])
def index():
    return render_template("index.html")



@app.route("/option", methods=['GET'])
def option():
    """ return charts based on user selected option """
    return genchart(request.args.get("option"), df)



@app.route("/compare", methods=['GET'])
def compare():
    return render_template("compare.html", nations=sorted(list(df.index)))



@app.route("/compare_chart", methods=['GET'])
def compare_chart():
    """ return charts based on user selected country """
    return country_chart(request.args.get("nation1"), request.args.get("nation2"), df)



@app.route("/data", methods=['GET'])
def data():
    """ renders all data frame as a html table """

    # creating to list out of data frame to be used in html template
    header = df.reset_index().columns.tolist()
    data = df.reset_index().values.tolist()
    
    return render_template("data.html", header=header, data=data)



@app.errorhandler(Exception)
def exception(e):
    """Handling errors"""
    if  isinstance(e, HTTPException):
        return errorfeedback(e.name, e.code, e.description)
    else:
        e = InternalServerError()
        return errorfeedback(e.name, e.code, e.description)
