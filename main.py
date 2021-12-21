from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.payeer import Payeer
from data.users import User
from forms.payeer import AddPayeerForm, PayeerForm, AddUserApiForm, PaymentForm
from forms.users import RegisterForm, EditForm, LoginForm
from data.payeer_api import PayeerAPI, validate_wallet
from data.func import translate
import waitress


app = Flask(__name__)
app.config['SECRET_KEY'] = 'btc_stats_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/btc_stats.db")
    waitress.serve(app, host='0.0.0.0', port=8080)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return redirect("/login")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect('/account')
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter((User.email == form.email.data) | (User.name == form.email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/account")
        return render_template("login.html",
                               message="Неправильный логин или пароль",
                               form=form, title='Авторизация')
    return render_template("login.html", title="Авторизация", form=form)


@app.route("/account",  methods=['GET', 'POST'])
@login_required
def cabinet():
    form = EditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        if user:
            form.name.data = user.name
            form.email.data = user.email
            form.btc.data = user.btc
            form.eth.data = user.eth
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        if user:
            if current_user.name != form.name.data:
                if db_sess.query(User).filter(User.name == form.name.data).first():
                    return render_template("account.html", title="Профиль", form=form,
                                           message="Такой никнейм уже есть",
                                           name=user.name)
                user.name = form.name.data
            if current_user.email != form.email.data:
                if db_sess.query(User).filter(User.email == form.email.data).first():
                    return render_template("account.html", title="Профиль", form=form,
                                           message="Такая почта уже есть",
                                           name=user.name)
                user.email = form.email.data
            user.btc = form.btc.data
            user.eth = form.eth.data
            if form.password.data:
                if len(form.password.data) >= 8:
                    if form.password_again.data:
                        if form.password.data == form.password_again.data:
                            user.set_password(form.password.data)
                        else:
                            return render_template("account.html", title="Профиль", form=form,
                                                   message="Пароли не совпадают",
                                                   name=user.name)
                else:
                    return render_template("account.html", title="Профиль", form=form,
                                           message="Пароль должен быть не короче 8 символов",
                                           name=user.name)
            db_sess.commit()
            return render_template("account.html", title="Профиль", form=form, message="Изменения сохранены",
                                   name=user.name)
        else:
            abort(404)
    return render_template("account.html", title="Профиль", form=form, name=current_user.name)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter((User.email == form.email.data) | (User.name == form.name.data)).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if len(form.password.data) < 8:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли должен быть не короче 8 символов")
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect("/account")
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/payeer_account", methods=['GET', 'POST'])
@login_required
def payeer_account():
    form = PayeerForm()
    balance_show = False
    if request.method == "GET":
        db_sess = db_session.create_session()
        payeer = db_sess.query(Payeer).filter(Payeer.user_id == current_user.id).first()
        if payeer:
            form.account.data = payeer.account
            form.email.data = payeer.email
            form.btc.data = payeer.btc
            form.eth.data = payeer.eth
            form.ltc.data = payeer.ltc
        else:
            return render_template("payeer.html", title="Payeer", button=True)
        if payeer.api_id and payeer.api_pass:
            p_account = PayeerAPI(payeer.account, payeer.api_id, payeer.api_pass)
            balance_show = p_account.get_balance()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        payeer = db_sess.query(Payeer).filter(Payeer.user_id == current_user.id).first()
        if payeer:
            if payeer.account != form.account.data:
                if db_sess.query(Payeer).filter(Payeer.account == form.account.data).first():
                    return render_template('payeer.html', title='Payeer',
                                           form=form,
                                           message="Счёт с таким номером уже есть")
                payeer.account = form.account.data
            if payeer.email != form.email.data:
                if db_sess.query(Payeer).filter(Payeer.email == form.email.data).first():
                    return render_template('payeer.html', title='Payeer', form=form,
                                           message='Аккаунт с такой почтой уже есть')
                payeer.email = form.email.data
            payeer.btc = form.btc.data
            payeer.eth = form.eth.data
            payeer.ltc = form.ltc.data
            db_sess.commit()
            if payeer.api_id and payeer.api_pass:
                p_account = PayeerAPI(payeer.account, payeer.api_id, payeer.api_pass)
                balance_show = p_account.get_balance()
                return render_template("payeer.html", title="Payeer",
                                       button=False, form=form, message="Изменения сохранены", balance=balance_show)
            else:
                return render_template("payeer.html", title="Payeer",
                                       button=False, form=form, message="Изменения сохранены")
        else:
            abort(404)
    return render_template("payeer.html", title="Payeer", button=False, form=form, balance=balance_show)


@app.route("/add_payeer", methods=['GET', 'POST'])
@login_required
def add_payeer():
    form = AddPayeerForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Payeer).filter(Payeer.account == form.account.data).first():
            return render_template('add_payeer.html', title='Добавление счёта',
                                   form=form,
                                   message="Счёт с таким номером уже есть")
        if db_sess.query(Payeer).filter(Payeer.email == form.email.data).first():
            return render_template('add_payeer.html', title='Добавление счёта',
                                   form=form,
                                   message="Счёт с такой почтой уже есть")
        payeer = Payeer()
        payeer.account = form.account.data
        payeer.email = form.email.data
        payeer.btc = form.btc.data
        payeer.eth = form.eth.data
        payeer.ltc = form.ltc.data
        current_user.payeer.append(payeer)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/payeer_account')
    return render_template('add_payeer.html', title='Добавление счёта', form=form)


@app.route('/payment_system', methods=['GET', 'POST'])
@login_required
def payment():
    db_sess = db_session.create_session()
    payeer = db_sess.query(Payeer).filter(Payeer.user_id == current_user.id).first()
    if payeer:
        if (not payeer.api_id) or (not payeer.api_pass):
            return redirect('/add_payeer_api')
        else:
            form = PaymentForm()
            if request.method == 'GET':
                db_sess = db_session.create_session()
                payeer = db_sess.query(Payeer).filter(Payeer.user_id == current_user.id).first()
                p_account = PayeerAPI(payeer.account, payeer.api_id, payeer.api_pass)
                balance = p_account.get_balance()
                return render_template('payment.html', title='Перевод', form=form, balance=balance)
            if form.validate_on_submit():
                db_sess = db_session.create_session()
                payeer = db_sess.query(Payeer).filter(Payeer.user_id == current_user.id).first()
                p_account = PayeerAPI(payeer.account, payeer.api_id, payeer.api_pass)
                recipient = form.to.data
                summ = form.summ.data
                currency = form.currency.data
                comment = form.comment.data
                balance = p_account.get_balance()
                if p_account.check_user(recipient):
                    if comment:
                        transaction = p_account.transfer(summ, recipient, currency, currency, comment)
                    else:
                        transaction = p_account.transfer(summ, recipient, currency, currency)
                    if transaction is True:
                        return redirect('/success')
                    else:
                        message = str(transaction)[2:-2]
                        message = translate(message)
                        if message == 'balanceError':
                            message = 'Недостаточно средств'
                        if message == 'передачаСебяЗапрещено':
                            message = 'Счета отправителя и получателя совпадают'
                        return render_template('payment.html', title='Перевод', form=form, balance=balance,
                                               message=message)
                else:
                    message = 'Получатель не найден'
                    return render_template('payment.html', title='Перевод', form=form, balance=balance, message=message)
    else:
        return redirect('/add_payeer')


@app.route('/success')
def success():
    db_sess = db_session.create_session()
    payeer = db_sess.query(Payeer).filter(Payeer.user_id == current_user.id).first()
    p_account = PayeerAPI(payeer.account, payeer.api_id, payeer.api_pass)
    balance = p_account.get_balance()
    return render_template('success.html', title='Перевод', balance=balance)


@app.route('/add_payeer_api', methods=['GET', 'POST'])
@login_required
def add_api():
    form = AddUserApiForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Payeer).filter(Payeer.api_id == form.apiid.data).first():
            return render_template('add_api.html', title='Подключение платёжной системы',
                                   form=form, message='Такой api_id уже есть')
        if db_sess.query(Payeer).filter(Payeer.api_pass == form.apipass.data).first():
            return render_template('add_api.html', title='Подключение платёжной системы',
                                   form=form, message='Такой api_pass уже есть')
        payeer = db_sess.query(Payeer).filter(Payeer.user_id == current_user.id).first()
        payeer.api_id = form.apiid.data
        payeer.api_pass = form.apipass.data
        if validate_wallet(payeer.account) is False:
            return render_template('add_api.html', title='Подключение платёжной системы',
                                   form=form, message='Неправильный номер счёта')
        p_account = PayeerAPI(payeer.account, payeer.api_id, payeer.api_pass)
        if p_account.auth_check() is False:
            payeer.api_id = None
            payeer.api_pass = None
            return render_template('add_api.html', title='Подключение платёжной системы',
                                   form=form, message='Ошибка авторизации')
        db_sess.commit()
        return redirect('/payment_system')
    return render_template('add_api.html', title='Подключение платёжной системы', form=form)


@app.route("/stats/<coin>")
def stats(coin):
    if coin == "btc":
        return render_template("stats.html", title="Курс биткоина")
    elif coin == "eth":
        return render_template("stats_eth.html", title="Курс эфириума")
    elif coin == "ltc":
        return render_template("stats_ltc.html", title="Курс лайткоина")
    elif coin == "coins":
        return render_template("stats_coins.html", title='Курсы криптовалют')


@app.route('/delete_payment')
def payment_delete():
    db_sess = db_session.create_session()
    payeer = db_sess.query(Payeer).filter(Payeer.user_id == current_user.id).first()
    payeer.api_pass = None
    payeer.api_id = None
    db_sess.commit()
    return redirect('/payeer_account')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.after_request
def redirect_to_sign(response):
    if response.status_code == 401:
        return redirect('/login')
    return response


if __name__ == '__main__':
    main()