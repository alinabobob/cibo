from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.user import User
from data.db_session import create_session
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.get(User, user_id)


@app.route('/')
def b():
    return render_template('base.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session = create_session()
        user = session.query(User).filter(User.email == request.form.get('email')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect('/')
        return render_template('login.html', message="Неверный email или пароль")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form.get('password') != request.form.get('password_again'):
            return render_template('register.html', message="Пароли не совпадают")
        session = create_session()
        if session.query(User).filter(User.email == request.form.get('email')).first():
            return render_template('register.html', message="Пользователь уже существует")
        user = User()
        user.email = request.form.get('email')
        user.username = request.form.get('username')
        user.name = request.form.get('name')
        user.age = int(request.form.get('age'))
        user.description = request.form.get('description')
        user.set_password(request.form.get('password'))
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html')


@app.route('/profile/<int:user_id>')
def profile(user_id):
    session = create_session()
    user = session.get(User, user_id)
    if not user:
        return "Пользователь не найден"
    return render_template("profile.html", user=user, recipes=[])


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    session = create_session()
    user = session.get(User, current_user.id)
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.name = request.form.get('name')
        user.age = int(request.form.get('age'))
        user.description = request.form.get('description')
        session.commit()
        return redirect(f'/profile/{user.id}')
    return render_template('edit_profile.html', user=user)


if __name__ == '__main__':
    db_session.global_init("db/cibo.sqlite")
    app.run(port=8080, host='127.0.0.1')