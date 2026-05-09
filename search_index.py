import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import MultifieldParser
from data.db_session import create_session
from data.recipes import Recipe
from data.user import User

INDEX_DIR = "search_index"


def get_index():
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
        return index.create_in(INDEX_DIR, get_schema())
    return index.open_dir(INDEX_DIR)


def get_schema():
    return Schema(
        id=ID(stored=True, unique=True),
        title=TEXT(stored=True),
        text=TEXT(stored=True),
        cuisine=TEXT(),
        category=TEXT()
    )


def add_recipe_to_index(recipe):
    ix = get_index()
    writer = ix.writer()
    writer.update_document(
        id=str(recipe.id),
        title=recipe.title,
        text=recipe.text,
        cuisine=recipe.cuisine or "",
        category=recipe.category or ""
    )
    writer.commit()


def add_user_to_index(user):
    ix = get_index()
    writer = ix.writer()
    writer.update_document(
        id="u_" + str(user.id),
        title=user.name,
        text=user.username + " " + (user.description or ""),
        cuisine="",
        category=""
    )
    writer.commit()


def build_index():
    ix = get_index()
    writer = ix.writer()

    session = create_session()

    recipes = session.query(Recipe).all()
    for recipe in recipes:
        writer.update_document(
            id="r_" + str(recipe.id),
            title=recipe.title,
            text=recipe.text,
            cuisine=recipe.cuisine or "",
            category=recipe.category or ""
        )

    users = session.query(User).all()
    for user in users:
        writer.update_document(
            id="u_" + str(user.id),
            title=user.name,
            text=user.username + " " + (user.description or ""),
            cuisine="",
            category=""
        )

    print(f"Индекс Whoosh обновлен. Добавлено {len(recipes)} рецептов и {len(users)} пользователей.")
    writer.commit()


def search(query_str):
    ix = get_index()
    parser = MultifieldParser(["title", "text"], schema=ix.schema)

    query = parser.parse(query_str)

    recipes_ids = []
    users_ids = []

    with ix.searcher() as searcher:
        hits = searcher.search(query, limit=30)
        for hit in hits:
            doc_id = hit['id']
            if doc_id.startswith('r_'):
                recipes_ids.append(doc_id[2:])
            elif doc_id.startswith('u_'):
                users_ids.append(doc_id[2:])

    return recipes_ids, users_ids