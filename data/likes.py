import sqlalchemy as sa
from .db_session import SqlAlchemyBase


class Like(SqlAlchemyBase):
    __tablename__ = 'likes'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey("recipes.id"))