from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, SubmitField, EmailField, StringField
from wtforms.validators import InputRequired, Email, EqualTo, Length


# define our own FlaskForm subclass for our form
class RegisterForm(FlaskForm):
    username = StringField("Username: ", validators=[InputRequired()])
    # email = EmailField("Email: ", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password: ", validators=[InputRequired(), Length(min=8, max=256)]
    )
    confirm_password = PasswordField(
        "Confirm Password: ", validators=[EqualTo("password")]
    )
    submit = SubmitField("Register")


# define our own FlaskForm subclass for our form
class LoginForm(FlaskForm):
    username = StringField("Username: ", validators=[InputRequired()])
    # email = EmailField("Email: ", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password: ", validators=[InputRequired(), Length(min=8, max=256)]
    )
    submit = SubmitField("Login")
