import sqlalchemy as sa
from .db_session import SqlAlchemyBase


class View(SqlAlchemyBase):
    __tablename__ = 'views'

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer)
    recipe_id = sa.Column(sa.Integer)