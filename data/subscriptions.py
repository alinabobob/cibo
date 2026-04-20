import sqlalchemy as sa
from .db_session import SqlAlchemyBase


class Subscription(SqlAlchemyBase):
    __tablename__ = 'subscriptions'

    id = sa.Column(sa.Integer, primary_key=True)
    follower_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    followed_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))