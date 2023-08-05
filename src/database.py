
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string, random

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks  = db.relationship('Bookmark', backref="user")
    #specifying that ist a reverse rxnshi

    def __repr__(self) -> str:
        return 'User>>>{self.username}'
    
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=False)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())


    def generate_short_characters(self):
        characters = string.digits+string.ascii_letters
        picked_chars =  ''.join(random.choices(characters, k=3))

        #ensuring that the string does not exist in the db
        link = self.query.filter_by(short_url=picked_chars).first()#ensuring its distinct
        if link:
            self.generate_short_characters() #it will try until it gets the unique one
        else:return picked_chars

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.short_url =  self.generate_short_characters()
        #above means that on initiazling will use the generate_short_characters to generate
        #the short_url
        


    def __repr__(self) -> str:
        return 'Bookmark>>>{self.url}'