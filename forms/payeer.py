from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email


class PayeerForm(FlaskForm):
    account = StringField('Номер счёта')
    email = EmailField('Почта')
    btc = StringField("Адрес биткоин кошелька payeer")
    eth = StringField("Адрес эфириум кошелька payeer")
    ltc = StringField("Адрес лайткоин кошелька payeer")
    submit = SubmitField('Сохранить изменения')


class AddPayeerForm(FlaskForm):
    account = StringField('Номер счёта', validators=[DataRequired()])
    email = EmailField('Почта', validators=[Email()])
    btc = StringField("Адрес биткоин кошелька payeer", validators=[DataRequired()])
    eth = StringField("Адрес эфириум кошелька payeer")
    ltc = StringField("Адрес лайткоин кошелька payeer")
    submit = SubmitField('Сохранить')


class AddUserApiForm(FlaskForm):
    apiid = StringField('id апи-пользователя', validators=[DataRequired()])
    apipass = StringField('секретный ключ апи-пользователя', validators=[DataRequired()])
    approval = BooleanField('Я прочёл/прочла соглашение', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class PaymentForm(FlaskForm):
    currency = SelectField('Выберите валюту', choices=['USD', 'EUR', 'RUB'])
    summ = StringField('Введите сумму', validators=[DataRequired()])
    to = StringField('Номер счёта получателя', validators=[DataRequired()])
    comment = StringField('Комментарий к переводу')
    submit = SubmitField('Подтвердить')