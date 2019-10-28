from flask import Flask, url_for, render_template

app = Flask(__name__)

"""App configurations"""
app.config["SECRET_KEY"] = 'development'
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    return render_template("layout.html")
