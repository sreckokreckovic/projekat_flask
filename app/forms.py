from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TelField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    first_name = StringField("Ime", validators=[DataRequired(), Length(min=2)])
    last_name = StringField("Prezime", validators=[DataRequired(), Length(min=2)])
    phone = TelField("Telefon", validators=[DataRequired(), Length(min=6, max=15)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Lozinka", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Ponovi lozinku",
        validators=[
            DataRequired(),
            EqualTo("password", message="Lozinke se ne poklapaju"),
        ],
    )
    submit = SubmitField("Registruj se")
