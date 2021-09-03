from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update_value(self, key, value):
        setattr(self, key, value)
        db.session.commit()

    def __repr__(self):
        return '<id: {} name: {}>'.format(self.id, self.name)


class Message(db.Model):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(),
                        nullable=False)
    sent_by = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __init__(self, text, sent_by):
        self.text = text
        self.sent_by = sent_by

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<id: {} text: {}>'.format(self.id, self.text)
