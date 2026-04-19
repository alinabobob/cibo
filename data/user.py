import sqlalchemy as sa
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    email = sa.Column(sa.String, index=True, unique=True, nullable=False)
    username = sa.Column(sa.String, nullable=True)
    name = sa.Column(sa.String, nullable=True)
    age = sa.Column(sa.Integer, nullable=True)
    description = sa.Column(sa.String, nullable=True)
    hashed_password = sa.Column(sa.String, nullable=True)
    avatar = sa.Column(sa.String, nullable=True)
    subscribers = sa.Column(sa.Integer, default=0)
    recipes = relationship("Recipe", back_populates="user")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)