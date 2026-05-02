import sqlalchemy as sa
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
from sqlalchemy.orm import backref


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    recipe_id = sa.Column(sa.Integer, sa.ForeignKey('recipes.id'))
    text = sa.Column(sa.String, nullable=False)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('comments.id'), nullable=True)
    created_at = sa.Column(sa.DateTime, default=sa.func.now())
    user = relationship("User")
    recipe = relationship("Recipe", back_populates="comments")
    replies = relationship("Comment", backref=backref('parent', remote_side=[id]), lazy='dynamic')