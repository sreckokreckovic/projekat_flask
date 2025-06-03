from flask import Blueprint, flash, render_template, jsonify, redirect, url_for
from flask_login import login_user
from app.forms import RegistrationForm,LoginForm
from app.models import db, User
from werkzeug.security import generate_password_hash,check_password_hash
from app import db

bp = Blueprint("main", __name__)


@bp.route("/")
def show():
    return "Početna stranica"

@bp.route("/registration", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("Već postoji korisnik sa unešenom email adresom", "warning")
            return redirect(url_for("main.register"))

        hash_pass = generate_password_hash(form.password.data)

        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            email=form.email.data,
            password=hash_pass,
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Uspješno kreiran nalog!", "success")
        return redirect(url_for("main.login"))
    return render_template("registration.html", form=form)

@bp.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and check_password_hash(user.password,form.password.data):
            login_user(user)
            flash('Ulogovani ste!','success')

            if user.role == "admin":
                return render_template('admin_panel.html')
            else:
                return "Korisnik" #kasnije cu dodati kada dobijemo frontend dio dje da preusmjeri
        else:
            flash("Pokusajte ponovo!",'danger')
    return render_template ('login.html',form = form)
