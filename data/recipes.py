import sqlalchemy as sa
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class Recipe(SqlAlchemyBase):
    __tablename__ = 'recipes'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    created_at = sa.Column(sa.DateTime, default=sa.func.now())
    title = sa.Column(sa.String, nullable=True)
    text = sa.Column(sa.String, nullable=True)
    image = sa.Column(sa.String, nullable=True)
    category = sa.Column(sa.String, nullable=True)
    cuisine = sa.Column(sa.String, nullable=True)
    complexity = sa.Column(sa.Integer, nullable=True)
    ingredients = sa.Column(sa.String, nullable=False)
    cooking_time = sa.Column(sa.Integer, nullable=True)
    type = sa.Column(sa.String, nullable=True)
    likes = sa.Column(sa.Integer, default=0)
    views = sa.Column(sa.Integer, default=0)
    food_intake = sa.Column(sa.String, nullable=True)
    manual = sa.Column(sa.String, nullable=True)
    user = relationship("User", back_populates="recipes")
    comments = relationship("Comment", back_populates="recipe", cascade="all, delete")