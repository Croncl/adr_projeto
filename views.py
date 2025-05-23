# filepath: d:\WS\ws_python\Analise_de_Redes_S5\AdR_projeto\views.py
from flask import render_template, redirect, url_for, flash
from main import app
from forms import LoginForm


@app.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == "admin" and form.password.data == "123":
            return redirect(url_for("blog"))
        else:
            flash("Usuário ou senha incorretos.")
    return render_template("home.html", form=form)


@app.route("/blog")
def blog():
    return render_template("blog.html")
