from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
import enum

db = SQLAlchemy()


class TransmissionType(enum.Enum):
    manual = "Manuelni"
    automatic = "Automatik"


class FuelType(enum.Enum):
    diesel = "Dizel"
    petrol = "Benzin"


class Brand(db.Model):
    __tablename__ = "brands"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    models = db.relationship("Model", backref="brand", lazy="True")


class Model(db.Model):
    __tablename__ = "models"
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    cars = db.relationship("Car", backref="model", lazy=True)


class Car(db.Model):
    __tablename__ = "cars"
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey("models.id"), nullable=False)
    year = db.Column(db.Integer)
    doors = db.Column(db.Integer)
    seats = db.Column(db.Integer)
    fuel = db.Column(Enum(FuelType), nullable=False)
    transmission = db.Column(Enum(TransmissionType), nullable=False)
    power = db.Column(db.Integer)
    price_per_day = db.Column(db.Float)
    description = db.Column(db.Text)

    images = db.relationship("CarImage", backref="car", lazy=True)
    reservations = db.relationship("Reservation", backref="car", lazy=True)


class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    role = db.Column(db.String(20), default="user")

    reservations = db.relationship("Reservation", backref="user", lazy=True)
    reviews = db.relationship("Review", backref="user", lazy=True)


class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date_from = db.Column(db.Date, nullable=False)
    date_to = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(20))

    pickup_location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    return_location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))

    pickup_location = db.relationship("Location", foreign_keys=[pickup_location_id])
    return_location = db.relationship("Location", foreign_keys=[return_location_id])


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)

    car = db.relationship("Car", backref="reviews")


class CarImage(db.Model):
    __tablename__ = "car_images"
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)
    url = db.Column(db.String(255), nullable=False)
