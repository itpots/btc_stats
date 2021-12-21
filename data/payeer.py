import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Payeer(SqlAlchemyBase):
    __tablename__ = 'payeer'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    account = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=False, unique=False)
    btc = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=False)
    eth = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=False)
    ltc = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=False)
    api_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    api_pass = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
