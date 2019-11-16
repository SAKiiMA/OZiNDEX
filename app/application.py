from flask import Flask, url_for, render_template, session, request
from flask_session import Session
from werkzeug.exceptions import HTTPException, InternalServerError

from tempfile import mkdtemp

# see utils.py for utility functions
from utils import errorfeedback, genchart, get_df, country_chart, hist


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



@app.route("/stats", methods=['GET'])
def stats():
    """ return some statistical data to be viewed in a table """

    year_list = df.columns[2:-1]
    table = []

    table.append(["TOTAL NUMBER OF MIGRANTS", "{:,.0f}".format(df["sum"].sum()), "Over a Period of 73 Years From 1945 to 2018"])
    table.append(["AVERAGE NUMBER OF MIGRANTS", "{:,.0f}".format(df["sum"].sum() / 73), "-"])
    table.append(["MINIMUM NUMBER OF MIGRANTS FROM A COUNTRY", "{:,.0f}".format(df["sum"].min()), "'Chad' from 1945 to 2018"])
    table.append(["MAXIMUM NUMBER OF MIGRANTS FROM A COUNTRY", "{:,.0f}".format(df["sum"].max()), "'UK & Ireland' from 1945 to 2018"])
    table.append(["MINIMUM NUMBER OF MIGRANTS IN A YEAR", "{:,.0f}".format(df[year_list].sum(axis=0).min()), "Almost Two Years from Oct 1945 to Jun 1947"])
    table.append(["MAXIMUM NUMBER OF MIGRANTS IN A YEAR", "{:,.0f}".format(df[year_list].sum(axis=0).max()), "from 2012 to 2013"])
    table.append(["MAXIMUM NUMBER OF MIGRANTS FROM A SINGLE COUNTRY AND IN A YEAR", "{:,.0f}".format(df[year_list].max().max()), "UK & Ireland from 1968 to 1969 "])

    return render_template("stats.html", table=table, image=hist(df))



@app.route("/data", methods=['GET'])
def data():
    """ renders all data frame as a html table """

    # creating a list out of data frame to be used in html template
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
