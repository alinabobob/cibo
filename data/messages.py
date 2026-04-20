import sqlalchemy as sa
from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    sender_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    receiver_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    text = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=sa.func.now())