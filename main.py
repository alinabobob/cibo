from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data.user import User
from data.recipes import Recipe
from data.db_session import create_session
from data import db_session
from PIL import Image
from data.likes import Like
from data.comments import Comment
from data.views import View
from data.messages import Message
from flask import jsonify
from sqlalchemy import or_, and_
from contextlib import contextmanager
from data.subscriptions import Subscription
from flask import flash, redirect, url_for
import os
import uuid
from search_index import build_index, search, add_recipe_to_index, add_user_to_index
from waitress import serve


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


def get_recipes_by_category(category_name):
    session = create_session()
    recipes = session.query(Recipe).filter(Recipe.category.ilike(f'%{category_name}%')).all()
    return recipes, f"{category_name.capitalize()}"


@contextmanager
def session_scope():
    session = create_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.get(User, user_id)


@app.route('/')
def home():
    kitchens = [
                   "Австралийская",
                   "Австрийская",
                   "Азербайджанская",
                   "Азиатская",
                   "Арабская",
                   "Аргентинская",
                   "Армянская",
                   "Английская",
                   "Американская",
                   "Африканская",
                   "Башкирская",
                   "Балканская",
                   "Белорусская",
                   "Бельгийская",
                   "Болгарская",
                   "Бразильская",
                   "Британская",
                   "Бурятская",
                   "Венгерская",
                   "Вьетнамская",
                   "Восточная",
                   "Гавайская",
                   "Греческая",
                   "Грузинская",
                   "Датская",
                   "Дагестанская",
                   "Дальневосточная",
                   "Европейская",
                   "Египетская",
                   "Еврейская",
                   "Израильская",
                   "Индийская",
                   "Индонезийская",
                   "Ирландская",
                   "Иранская",
                   "Испанская",
                   "Итальянская",
                   "Кабардинская",
                   "Казахская",
                   "Канадская",
                   "Карельская",
                   "Карибская",
                   "Катайская",
                   "Корейская",
                   "Кубинская",
                   "Лапландская",
                   "Латвийская",
                   "Ливанская",
                   "Литовская",
                   "Марийская",
                   "Марокканская",
                   "Мексиканская",
                   "Молдавская",
                   "Монгольская",
                   "Немецкая",
                   "Норвежская",
                   "Осетинская",
                   "Перуанская",
                   "Польская",
                   "Португальская",
                   "Прибалтийская",
                   "Русская",
                   "Румынская",
                   "Северная",
                   "Сербская",
                   "Сибирская",
                   "Сицилийская",
                   "Словацкая",
                   "Славянская",
                   "Среднеазиатская",
                   "Тайская",
                   "Татарская",
                   "Таджикская",
                   "Тибетская",
                   "Турецкая",
                   "Тунисская",
                   "Туркменская",
                   "Удмуртская",
                   "Узбекская",
                   "Украинская",
                   "Филиппинская",
                   "Финская",
                   "Французская",
                   "Хорватская",
                   "Чехословацкая",
                   "Чешская",
                   "Чеченская",
                   "Чукотская",
                   "Шведская",
                   "Швейцарская",
                   "Шотландская",
                   "Эстонская",
                   "Якутская",
                   "Японская"
            ]
    session = create_session()
    recipes = session.query(Recipe).order_by(Recipe.created_at.desc()).limit(12).all()
    return render_template('home.html', kitchens=kitchens, recipes=recipes)


@app.route('/search')
def search_recipes():
    query = request.args.get('query')

    if not query:
        return render_template('search.html', recipes=[], users=[], query="")

    recipes_ids, users_ids = search(query)

    session = create_session()

    found_recipes = []
    found_users = []

    if recipes_ids:
        db_recipes = session.query(Recipe).filter(Recipe.id.in_(recipes_ids)).all()

        recipes_sorted = []
        for rid in recipes_ids:
            for rec in db_recipes:
                if str(rec.id) == rid:
                    recipes_sorted.append(rec)
                    break
        found_recipes = recipes_sorted

    if users_ids:
        db_users = session.query(User).filter(User.id.in_(users_ids)).all()

        users_sorted = []
        for uid in users_ids:
            for user in db_users:
                if str(user.id) == uid:
                    users_sorted.append(user)
                    break
        found_users = users_sorted

    if found_users and not found_recipes:
        return render_template('users_search.html', users=found_users, query=query)

    return render_template('search.html', recipes=found_recipes, users=found_users, query=query)


@app.route('/filter')
def filter_recipes():
    session = create_session()

    query = session.query(Recipe)

    category = request.args.get('category')
    cuisine = request.args.get('cuisine')
    food_intake = request.args.get('food_intake')
    recipe_type = request.args.get('type')

    time_min = request.args.get('time_min', type=int)
    time_max = request.args.get('time_max', type=int)

    if category:
        query = query.filter(Recipe.category.ilike(f'%{category}%'))

    if cuisine:
        query = query.filter(Recipe.cuisine.ilike(f'%{cuisine}%'))

    if food_intake:
        query = query.filter(Recipe.food_intake.ilike(f'%{food_intake}%'))

    if recipe_type:
        query = query.filter(Recipe.type.ilike(f'%{recipe_type}%'))

    if time_min is not None:
        query = query.filter(Recipe.cooking_time >= time_min)

    if time_max is not None:
        query = query.filter(Recipe.cooking_time <= time_max)

    recipes = query.all()
    return render_template('filtered_recipes.html', recipes=recipes)


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
        add_user_to_index(user)
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
        add_user_to_index(user)
        return redirect(f'/profile/{user.id}')
    return render_template('edit_profile.html', user=user)


@app.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    session = create_session()
    if request.method == 'POST':
        msg = Message()
        msg.sender_id = current_user.id
        msg.receiver_id = user_id
        msg.text = request.form.get('text')
        session.add(msg)
        session.commit()
    messages = (session.query(Message).filter(or_(and_(Message.sender_id == current_user.id,
                                                      Message.receiver_id == user_id),
                                                 and_(Message.sender_id == user_id,
                                                      Message.receiver_id == current_user.id)))
                .order_by(Message.created_at).all())
    user = session.get(User, user_id)
    return render_template('chat.html', messages=messages, user=user)


@app.route('/chats')
@login_required
def chats():
    session = create_session()
    messages = session.query(Message).filter(or_((Message.sender_id == current_user.id) |
                                                 (Message.receiver_id == current_user.id))).all()
    users = set()
    for m in messages:
        if m.sender_id != current_user.id:
            users.add(m.sender_id)
        if m.receiver_id != current_user.id:
            users.add(m.receiver_id)
    users = [session.get(User, uid) for uid in users]
    return render_template('chats.html', users=users)


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
            recipe.food_intake = request.form.get('food_intake')
            recipe.manual = request.form.get('manual')
        except Exception as e:
            return render_template('add_recipe.html',
                                   message="Название или описание введёно некорректно")
        try:
            f = request.files.get('image')
            if f and f.filename:
                ff = f"{uuid.uuid4()}.{f.filename.rsplit('.', 1)[-1]}"
                path = f"img/recipes/{ff}"
                full_path = os.path.join('static', path)
                process_image(f, full_path)
                recipe.image = path
        except ValueError:
            return render_template('add_recipe.html',
                                   message="Неизвестное расширение файла")
        session.add(recipe)
        session.commit()
        add_recipe_to_index(recipe)

        return redirect(f'/profile/{current_user.id}')
    return render_template('add_recipe.html')


@app.route('/delete_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def delete_recipe(recipe_id):
    session = create_session()
    recipe = session.get(Recipe, recipe_id)
    if not recipe or recipe.user_id != current_user.id:
        return redirect('/')

    if request.method == 'POST':

        if recipe.image:
            try:
                os.remove(os.path.join('static', recipe.image))
            except:
                pass
        session.delete(recipe)
        session.commit()
        return redirect(f'/profile/{current_user.id}')

    return render_template('delete_recipe.html', recipe=recipe)


@app.route('/recipe/<int:recipe_id>')
def recipe_page(recipe_id):
    session = create_session()
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return "Рецепт не найден"
    recipe.views += 1
    if current_user.is_authenticated:
        view = View(user_id=current_user.id, recipe_id=recipe_id)
        session.add(view)
    comments = session.query(Comment).filter(Comment.recipe_id == recipe_id).order_by(Comment.created_at).all()
    comment_tree = build_com(comments)
    session.commit()
    return render_template('recipe.html', recipe=recipe, comments_tree=comment_tree)


@app.route('/recipes/breakfast')
def recipes_breakfast():
    recipes, category_title = get_recipes_by_category('Завтрак')
    return render_template('category_recipes.html', recipes=recipes, category_title=category_title)


@app.route('/recipes/lunch')
def recipes_lunch():
    recipes, category_title = get_recipes_by_category('Обед')
    return render_template('category_recipes.html', recipes=recipes, category_title=category_title)


@app.route('/recipes/dinner')
def recipes_dinner():
    recipes, category_title = get_recipes_by_category('Ужин')
    return render_template('category_recipes.html', recipes=recipes, category_title=category_title)


@app.route('/recipes/dessert')
def recipes_dessert():
    recipes, category_title = get_recipes_by_category('Десерт')
    return render_template('category_recipes.html', recipes=recipes, category_title=category_title)


@app.route('/recipes/drinks')
def recipes_drinks():
    recipes, category_title = get_recipes_by_category('Напитки')
    return render_template('category_recipes.html', recipes=recipes, category_title=category_title)


@app.route('/recipes')
def all_recipes():
    session = create_session()
    recipes = session.query(Recipe).all()
    return render_template('all_recipes.html', recipes=recipes)


@app.route('/api/recipes')
def api_recipes():
    session = create_session()
    recipes = session.query(Recipe).all()
    return jsonify([{"id": r.id,
                     "title": r.title,
                     "author": r.user.name} for r in recipes])


@app.route('/recipes/top')
def top_recipes():
    session = create_session()
    recipes = session.query(Recipe).order_by(Recipe.likes.desc()).all()
    return render_template('top_recipes.html', recipes=recipes)


@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    session = create_session()
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return "Рецепт не найден"
    if recipe.user_id != current_user.id:
        return redirect('/')
    if request.method == 'POST':
        recipe.title = request.form.get('title')
        recipe.text = request.form.get('text')
        recipe.category = request.form.get('category')
        recipe.cuisine = request.form.get('cuisine')
        recipe.type = request.form.get('type')
        f = request.files.get('image')
        if f and f.filename:
            ff = f"{uuid.uuid4()}.{f.filename.rsplit('.', 1)[-1]}"
            path = f"img/recipes/{ff}"
            full_path = os.path.join('static', path)
            process_image(f, full_path)
            recipe.image = path
        session.commit()
        add_recipe_to_index(recipe)
        return redirect(f'/profile/{current_user.id}')
    return render_template('edit_recipe.html', recipe=recipe)


@app.route('/like/<int:recipe_id>')
@login_required
def like(recipe_id):
    session = create_session()
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return redirect('/')
    if recipe.user_id == current_user.id:
        return redirect(request.referrer or '/')
    existing = session.query(Like).filter(Like.user_id == current_user.id,
                                          Like.recipe_id == recipe_id).first()
    if existing:
        return redirect(request.referrer or '/')
    like = Like(user_id=current_user.id, recipe_id=recipe_id)
    session.add(like)
    recipe.likes += 1
    session.commit()
    return redirect(request.referrer or '/')


@app.route('/subscribe/<int:user_id>')
@login_required
def subscribe(user_id):
    session = create_session()

    user = session.get(User, user_id)

    if not user:
        return redirect('/')

    if user.id == current_user.id:
        return redirect(request.referrer or '/')

    existing_subscription = session.query(Subscription).filter(
        Subscription.follower_id == current_user.id,
        Subscription.followed_id == user_id
    ).first()

    if existing_subscription:
        return redirect(request.referrer or '/')

    new_subscription = Subscription(
        follower_id=current_user.id,
        followed_id=user.id
    )

    user.subscribers += 1

    session.add(new_subscription)
    session.commit()

    return render_template('subscription_success.html', user=user)


@app.route('/subscribers/<int:user_id>')
@login_required
def subscribers(user_id):
    session = create_session()
    user = session.get(User, user_id)
    if not user:
        return "Пользователь не найден"

    subscriptions = session.query(Subscription).filter(Subscription.followed_id == user_id).all()

    followers = [session.get(User, sub.follower_id) for sub in subscriptions]

    return render_template('subscribers.html', user=user, followers=followers)


@app.route('/subscriptions')
@login_required
def subscriptions():
    session = create_session()
    subs = session.query(Subscription).filter(Subscription.follower_id == current_user.id).all()
    followed_users = [session.get(User, sub.followed_id) for sub in subs]
    return render_template('subscriptions.html', users=followed_users)


@app.route('/unsubscribe/<int:user_id>')
@login_required
def unsubscribe(user_id):
    session = create_session()
    sub = session.query(Subscription).filter(
        Subscription.follower_id == current_user.id,
        Subscription.followed_id == user_id
    ).first()

    if sub:
        followed_user = session.get(User, user_id)
        followed_user.subscribers -= 1
        session.delete(sub)
        session.commit()

        return render_template('unsubscribe_success.html', user=followed_user)

    return redirect(url_for('subscriptions'))


@app.route('/unsubscribe/confirm/<int:user_id>')
@login_required
def unsubscribe_confirm(user_id):
    return render_template('unsubscribe_confirm.html', user_id=user_id)


@app.route('/advice')
@login_required
def advice():
    session = create_session()
    likes = session.query(Like).filter(Like.user_id == current_user.id).all()
    views = session.query(View).filter(View.user_id == current_user.id).all()
    score = {}


    def add_score(recipe, weight):
        if recipe.id not in score:
            score[recipe.id] = 0
        score[recipe.id] += weight


    for like in likes:
        r = session.get(Recipe, like.recipe_id)
        if not r:
            continue
        conditions = []
        if r.category:
            conditions.append(Recipe.category == r.category)
        if r.cuisine:
            conditions.append(Recipe.cuisine == r.cuisine)
        if r.type:
            conditions.append(Recipe.type == r.type)
        if conditions:
            similar = session.query(Recipe).filter(or_(*conditions)).all()
        else:
            similar = []
        for s in similar:
            add_score(s, 3)
    for view in views:
        r = session.get(Recipe, view.recipe_id)
        if not r:
            continue
        conditions = []
        if r.category:
            conditions.append(Recipe.category == r.category)
        if r.cuisine:
            conditions.append(Recipe.cuisine == r.cuisine)
        if r.type:
            conditions.append(Recipe.type == r.type)
        if conditions:
            similar = session.query(Recipe).filter(or_(*conditions)).all()
        else:
            similar = []
        for s in similar:
            add_score(s, 1)
    user_ingredients = set()
    for like in likes:
        r = session.get(Recipe, like.recipe_id)
        if r and r.ingredients:
            user_ingredients |= set(r.ingredients.lower().split())
    for r in session.query(Recipe).all():
        if not r.ingredients:
            continue
        n = user_ingredients and set(r.ingredients.lower().split())
        if n:
            add_score(r, len(n) * 2)
    seen_ids = {l.recipe_id for l in likes} | {v.recipe_id for v in views}
    n = sorted([session.get(Recipe, rid) for rid in score if rid not in seen_ids],
               key=lambda r: score.get(r.id, 0),
               reverse=True)
    return render_template("advice.html", recipes=n[:20])


def build_com(comments):
    n = {}
    for i in comments:
        n[i.id] = {"comment": i, "children": []}
    nn = []
    for i in comments:
        if i.parent_id:
            if i.parent_id in n:
                n[i.parent_id]["children"].append(n[i.id])
        else:
            nn.append(n[i.id])
    return nn


@app.template_filter('datetime')
def format_datetime(value):
    if not value:
        return ""
    return value.strftime('%d.%m.%Y %H:%M')


@app.route('/comment/<int:recipe_id>', methods=['POST'])
@login_required
def add_comment(recipe_id):
    session = create_session()
    text = request.form.get('text')
    u = request.form.get('parent_id')
    if not text:
        return redirect(f'/recipe/{recipe_id}')
    c = Comment(user_id=current_user.id, recipe_id=recipe_id, text=text,
                      parent_id=u if u else None)
    session.add(c)
    session.commit()
    return redirect(f'/recipe/{recipe_id}')


if __name__ == '__main__':
    db_session.global_init("db/cibo.sqlite")
    build_index()
    app.run(port=8080, host='127.0.0.1')
    #serve(app, host='127.0.0.1', port=8080)