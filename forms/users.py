from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    name = StringField('Никнейм', validators=[DataRequired()])
    email = EmailField('Почта', validators=[Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class EditForm(FlaskForm):
    name = StringField('Никнейм', validators=[DataRequired()])
    email = EmailField('Почта', validators=[Email()])
    btc = StringField("Адрес биткоин кошелька")
    eth = StringField("Адрес эфириум кошелька")
    password = PasswordField('Пароль')
    password_again = PasswordField('Повторите пароль')
    submit = SubmitField('Сохранить изменения')


class LoginForm(FlaskForm):
    email = StringField("Почта или никнейм", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField('Войти')