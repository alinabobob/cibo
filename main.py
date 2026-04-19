from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.user import User
from data.recipes import Recipe
from data.db_session import create_session
from data import db_session
from PIL import Image
import os
import uuid


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def process_image(file, save_path):
    im = Image.open(file)
    max_width = 500
    max_height = 1000
    if im.width > max_width or im.height > max_height:
        im.thumbnail((max_width, max_height))
    im.save(save_path)


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.get(User, user_id)


@app.route('/')
def home():
    return render_template('home.html')


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
            r = request.form.get('remember') == 'on'
            login_user(user, remember=r)
            return redirect('/')
        return render_template('login.html',
                               message="Неверный email или пароль")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form.get('password') != request.form.get('password_again'):
            return render_template('register.html',
                                   message="Пароли не совпадают")
        session = create_session()
        if session.query(User).filter(User.email == request.form.get('email')).first():
            return render_template('register.html',
                                   message="Пользователь уже существует")
        user = User()
        try:
            user.email = request.form.get('email')
        except Exception as e:
            return render_template('register.html',
                                   message="Email введён некорректно")
        try:
            user.username = request.form.get('username')
        except Exception as e:
            return render_template('register.html',
                                   message="Username введён некорректно")
        try:
            user.name = request.form.get('name')
        except Exception as e:
            return render_template('register.html',
                                   message="Имя введёно некорректно")
        try:
            a = request.form.get('age')
            try:
                user.age = int(a)
            except ValueError:
                return render_template('register.html',
                                       message="Возраст должен быть числом")
        except Exception as e:
            return render_template('register.html',
                                   message="Возраст введён некорректно")
        try:
            user.description = request.form.get('description')
        except Exception as e:
            return render_template('register.html',
                                   message="Описание введёно некорректно")
        try:
            user.set_password(request.form.get('password'))
        except Exception as e:
            return render_template('register.html',
                                   message="Пароль введён некорректно")
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
    recipes = session.query(Recipe).filter(Recipe.user_id == user.id).all()
    return render_template("profile.html", user=user, recipes=recipes)


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
        f = request.files.get('avatar')
        if f and f.filename:
            ff = f"{uuid.uuid4()}.{f.filename.rsplit('.', 1)[-1]}"
            path = f"img/avatars/{ff}"
            f.save(os.path.join('static', path))
            user.avatar = path
        session.commit()
        return redirect(f'/profile/{user.id}')
    return render_template('edit_profile.html', user=user)


@app.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        session = create_session()
        recipe = Recipe()
        recipe.user_id = current_user.id
        try:
            recipe.title = request.form.get('title')
            recipe.category = request.form.get('category')
            recipe.cuisine = request.form.get('cuisine')
            recipe.complexity = request.form.get('complexity')
            recipe.ingredients = request.form.get('ingredients')
            recipe.cooking_time = request.form.get('cooking_time')
            recipe.type = request.form.get('type')
            recipe.text = request.form.get('text')
        except Exception as e:
            return render_template('add_recipe.html',
                                   message="Название или описание введёно некорректно")
        f = request.files.get('image')
        if f and f.filename:
            ff = f"{uuid.uuid4()}.{f.filename.rsplit('.', 1)[-1]}"
            path = f"img/recipes/{ff}"
            full_path = os.path.join('static', path)
            process_image(f, full_path)
            recipe.image = path
        session.add(recipe)
        session.commit()
        return redirect(f'/profile/{current_user.id}')
    return render_template('add_recipe.html')


@app.route('/recipe/<int:recipe_id>') #Страница рецепта, черновик, останьное тебе((
def recipe_page(recipe_id):
    session = create_session()
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return "Рецепт не найден"
    recipe.views += 1
    session.commit()
    return render_template('recipe.html', recipe=recipe)


@app.route('/recipes')
def all_recipes():
    session = create_session()
    recipes = session.query(Recipe).all()
    return render_template('all_recipes.html', recipes=recipes)


@app.route('/recipes/top')
def top_recipes():
    session = create_session()
    recipes = session.query(Recipe).order_by(Recipe.likes.desc()).all()
    return render_template('top_recipes.html', recipes=recipes)


@app.route('/like/<int:recipe_id>')
@login_required
def like(recipe_id):
    session = create_session()
    recipe = session.get(Recipe, recipe_id)
    if recipe:
        recipe.likes += 1
        session.commit()
    return redirect(request.referrer or '/')


@app.route('/subscribe/<int:user_id>')
@login_required
def subscribe(user_id):
    session = create_session()
    user = session.get(User, user_id)
    if user:
        user.subscribers += 1
        session.commit()
    return redirect(request.referrer or '/')


if __name__ == '__main__':
    db_session.global_init("db/cibo.sqlite")
    app.run(port=8080, host='127.0.0.1')