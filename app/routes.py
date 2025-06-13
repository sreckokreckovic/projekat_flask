import datetime
from flask import abort, send_file
import io
import pandas as pd
from flask import (
    Blueprint,
    current_app,
    flash,
    render_template,
    jsonify,
    redirect,
    url_for,
)
from flask_login import login_user
from flask_mail import Mail, Message
from app.forms import RegistrationForm, LoginForm
from app.models import (
    Brand,
    Car,
    CarImage,
    FuelType,
    Location,
    Model,
    Reservation,
    TransmissionType,
    db,
    User,
)
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from sqlalchemy.orm import joinedload
from flask import request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from flask_login import logout_user


bp = Blueprint("main", __name__)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.login"))


@bp.route("/profil")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@bp.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Nemate pristup ovoj stranici.", "danger")
        return redirect(url_for("main.cars"))
    return render_template("admin/dashboard.html")


@bp.route("/admin/brands/add", methods=["GET", "POST"])
@login_required
def admin_add_brand():
    if current_user.role != "admin":
        flash("Nemate pristup.", "danger")
        return redirect(url_for("main.cars"))

    if request.method == "POST":
        name = request.form.get("name")
        if name:
            new_brand = Brand(name=name)
            db.session.add(new_brand)
            db.session.commit()
            flash("Brend je dodan.", "success")
            return redirect(url_for("main.admin_cars"))

    return render_template("admin/add_brand.html")


@bp.route("/admin/models/add", methods=["GET", "POST"])
@login_required
def admin_add_model():
    if current_user.role != "admin":
        flash("Nemate pristup.", "danger")
        return redirect(url_for("main.cars"))

    brands = Brand.query.all()

    if request.method == "POST":
        name = request.form.get("name")
        brand_id = request.form.get("brand_id")
        if name and brand_id:
            new_model = Model(name=name, brand_id=brand_id)
            db.session.add(new_model)
            db.session.commit()
            flash("Model je dodan.", "success")
            return redirect(url_for("main.admin_cars"))

    return render_template("admin/add_model.html", brands=brands)


@bp.route("/admin/cars")
@login_required
def admin_cars():
    if current_user.role != "admin":
        flash("Nemate pristup ovoj stranici.", "danger")
        return redirect(url_for("main.cars"))
    cars = Car.query.all()
    return render_template("admin/cars.html", cars=cars)


@bp.route("/admin/cars/add", methods=["GET", "POST"])
@login_required
def admin_add_car():
    if current_user.role != "admin":
        flash("Nemate pristup ovoj stranici.", "danger")
        return redirect(url_for("main.cars"))
    models = Model.query.all()
    if request.method == "POST":
        model_id = request.form.get("model_id")
        year = request.form.get("year")
        doors = request.form.get("doors")
        seats = request.form.get("seats")
        fuel = request.form.get("fuel")
        transmission = request.form.get("transmission")
        power = request.form.get("power")
        price_per_day = request.form.get("price_per_day")
        description = request.form.get("description")

        new_car = Car(
            model_id=model_id,
            year=year,
            doors=doors,
            seats=seats,
            fuel=fuel,
            transmission=transmission,
            power=power,
            price_per_day=price_per_day,
            description=description,
        )
        db.session.add(new_car)
        db.session.flush()
        image_file = request.files.get("image")
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)

            image_url = f"/static/uploads/{filename}"
            car_image = CarImage(car_id=new_car.id, url=image_url)
            db.session.add(car_image)

            db.session.commit()
            flash("Auto je uspješno kreiran!", "success")
            return redirect(url_for("main.admin_cars"))
        return redirect(url_for("main.admin_cars"))

    models = Model.query.all()
    return render_template(
        "admin/add_car.html",
        models=models,
        fuel_types=FuelType,
        transmission_types=TransmissionType,
    )


@bp.route("/admin/cars/edit/<int:car_id>", methods=["GET", "POST"])
@login_required
def admin_edit_car(car_id):
    if current_user.role != "admin":
        flash("Nemate pristup ovoj stranici.", "danger")
        return redirect(url_for("main.cars"))
    car = Car.query.get_or_404(car_id)
    if request.method == "POST":
        car.year = int(request.form.get("year"))
        car.doors = int(request.form.get("doors"))
        car.seats = int(request.form.get("seats"))
        car.fuel = FuelType[request.form.get("fuel")]
        car.transmission = TransmissionType[request.form.get("transmission")]
        car.power = int(request.form.get("power"))
        car.price_per_day = float(request.form.get("price_per_day"))
        car.description = request.form.get("description")

        db.session.commit()
        return redirect(url_for("main.admin_cars"))
    return render_template("admin/edit_car.html", car=car)


@bp.route("/admin/cars/delete/<int:car_id>", methods=["POST"])
@login_required
def admin_delete_car(car_id):
    if current_user.role != "admin":
        flash("Nemate pristup ovoj stranici.", "danger")
        return redirect(url_for("main.cars"))
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    db.session.commit()
    flash("Auto je obrisan.", "success")
    return redirect(url_for("main.admin_cars"))


@bp.route("/admin/users")
@login_required
def admin_users():
    if current_user.role != "admin":
        flash("Nemate pristup ovoj stranici.", "danger")
        return redirect(url_for("main.cars"))
    users = User.query.filter(User.role != "admin").all()
    return render_template("admin/users.html", users=users)


@bp.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def admin_edit_user(user_id):
    if current_user.role != "admin":
        flash("Nemate pristup ovoj stranici.", "danger")
        return redirect(url_for("main.cars"))
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.first_name = request.form.get("first_name")
        user.last_name = request.form.get("last_name")
        user.phone = request.form.get("phone")
        user.email = request.form.get("email")
        user.role = request.form.get("role")
        db.session.commit()
        flash("Korisnik ažuriran.", "success")
        return redirect(url_for("main.admin_users"))

    return render_template("admin/edit_user.html", user=user)


@bp.route("/admin/users/delete/<int:user_id>", methods=["POST"])
@login_required
def admin_delete_user(user_id):
    if current_user.role != "admin":
        flash("Nemate pristup ovoj stranici.", "danger")
        return redirect(url_for("main.cars"))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Korisnik obrisan.", "success")
    return redirect(url_for("main.admin_users"))


@bp.route("/")
def cars():
    cars = Car.query.options(joinedload(Car.model).joinedload(Model.brand)).all()
    return render_template("cars.html", cars=cars)


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


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Ulogovani ste!", "success")
            if user.role == "admin":
                return redirect(url_for("main.admin_dashboard"))
            else:
                return redirect(url_for("main.cars"))
        else:
            flash("Pokusajte ponovo!", "danger")

    return render_template("login.html", form=form)


@bp.route("/rezervacija/<int:car_id>", methods=["GET", "POST"])
@login_required
def create_reservation(car_id):
    car = Car.query.get_or_404(car_id)
    locations = Location.query.all()

    if request.method == "POST":

        try:
            date_from = datetime.datetime.strptime(
                request.form["date_from"], "%Y-%m-%d"
            ).date()
            date_to = datetime.datetime.strptime(
                request.form["date_to"], "%Y-%m-%d"
            ).date()
            pickup_location_id = int(request.form["pickup_location"])
            return_location_id = int(request.form["return_location"])
        except (KeyError, ValueError):
            flash("Neispravan unos podataka.", "error")
            return render_template("kalendar.html", car=car, locations=locations)

        if date_from > date_to:
            flash("Datum početka mora biti prije datuma završetka.", "error")
            return render_template("kalendar.html", car=car, locations=locations)

        days = (date_to - date_from).days + 1
        total_price = days * car.price_per_day

        new_reservation = Reservation(
            car_id=car.id,
            user_id=current_user.id,
            date_from=date_from,
            date_to=date_to,
            total_price=total_price,
            pickup_location_id=pickup_location_id,
            return_location_id=return_location_id,
        )

        db.session.add(new_reservation)
        db.session.commit()

        flash("Rezervacija uspješno kreirana!", "success")
        return redirect(url_for("main.cars"))

    return render_template("kalendar.html", car=car, locations=locations)


@bp.route("/rezervacije")
@login_required
def reservations():
    user_reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    return render_template("reservations.html", reservations=user_reservations)


@bp.route("/admin/rezervacije", methods=["GET", "POST"])
@login_required
def admin_reservations():
    if request.method == "POST":
        name = request.form.get("name")
        address = request.form.get("address")
        city = request.form.get("city")

        if name:
            new_location = Location(name=name, address=address, city=city)
            db.session.add(new_location)
            db.session.commit()
            flash("Lokacija uspješno dodata.", "success")
        else:
            flash("Naziv lokacije je obavezan.", "danger")
        return redirect(url_for("main.admin_reservations"))

    reservations = Reservation.query.all()
    locations = Location.query.all()
    return render_template(
        "admin/reservations.html", reservations=reservations, locations=locations
    )


@bp.route("/admin/reservations/export")
@login_required
def export_reservations():
    if current_user.role != "admin":
        abort(403)

    reservations = Reservation.query.all()

    data = []
    for r in reservations:
        data.append(
            {
                "ID": r.id,
                "Korisnik": (
                    f"{r.user.first_name} {r.user.last_name}" if r.user else "Nepoznat"
                ),
                "Email": r.user.email if r.user else "Nepoznat",
                "Auto": (
                    f"{r.car.model.brand.name} {r.car.model.name}"
                    if r.car
                    else "Nepoznat"
                ),
                "Godina": r.car.year if r.car else "",
                "Datum od": r.date_from.strftime("%Y-%m-%d"),
                "Datum do": r.date_to.strftime("%Y-%m-%d"),
                "Mjesto preuzimanja": (
                    r.pickup_location.name if r.pickup_location else ""
                ),
                "Mjesto vraćanja": r.return_location.name if r.return_location else "",
                "Ukupna cijena (€)": (
                    f"{r.total_price:.2f}" if r.total_price else "0.00"
                ),
            }
        )

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Rezervacije")
    output.seek(0)

    return send_file(
        output,
        download_name="rezervacije.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
