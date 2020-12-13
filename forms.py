from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    IntegerField,
    SelectField,
    FileField,
)
from wtforms.validators import Required, length, email, regexp, Length, ValidationError
import re


def validate_mobile(form, field):
    if len(field.data) != 10:
        raise ValidationError("Mobile number must be of length 10")


def validate_adha(form, field):
    if re.match(r"^[2-9]{1}[0-9]{3}\\s[0-9]{4}\\s[0-9]{4}$", field.data) == None:
        raise ValidationError("Enter correct aadhar number")


def validate_adhar(form, field):
    if len(field.data) != 12:
        raise ValidationError("Enter correct aadhar number")


class signinForm(FlaskForm):
    name = StringField("name", [Required()])
    email = StringField("email", [Required(), email("enter valid email")])
    mobile = StringField("mobile number", [validate_mobile])
    password = PasswordField(
        "password",
        [Required(), length(min=8, max=10, message="must be 8 to 12 charecters")],
    )
    aadhar = StringField("Aadhar", [validate_adhar])

    submit = SubmitField("signin")


class loginForm(FlaskForm):
    email = StringField("email", [Required(), email(message="enter valid email")])
    password = PasswordField("password", [Required(), length(min=8, max=12)])
    submit = SubmitField("login")


class pin(FlaskForm):
    pincode = StringField("pin", [Required()])
    submit = SubmitField("search")


# prod_types = [
#     ("1", "fertilizer"),
#     ("2", "seed", ("3", "pesticide"), ("4", "machinary part")),
# ]
