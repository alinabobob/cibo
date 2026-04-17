import sqlalchemy as sa
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import relationship


class Recipe(SqlAlchemyBase):
    __tablename__ = 'recipes'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    title = sa.Column(sa.String, nullable=True)
    text = sa.Column(sa.String, nullable=True)
    image = sa.Column(sa.String, nullable=True)
    user = relationship("User", back_populates="recipes")