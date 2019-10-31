from flask import render_template

# receiving errors from errorhandler and render to user
def error(message, code = 400):
    return render_template("error.html", message=message, code=code), code
