from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


db=SQLAlchemy()




class Follow(db.Model):
 __tablename__ = 'follows'
 followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
 primary_key=True)
 follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
 primary_key=True)
 


class Users(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String , unique=True, nullable=False)
    password = db.Column(db.String , nullable=False)
    user_name = db.Column(db.String ,unique=True, nullable=False)
    blogs=db.relationship('Blogs')
    profile=db.relationship('Profile')
    followed = db.relationship('Follow',foreign_keys=[Follow.follower_id],
    backref=db.backref('follower', lazy='joined'),lazy='dynamic',cascade='all, delete-orphan')
    followers = db.relationship('Follow',foreign_keys=[Follow.followed_id],
    backref=db.backref('followed', lazy='joined'),lazy='dynamic',cascade='all, delete-orphan')




class Blogs(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    Blog_title = db.Column(db.String, nullable=False)
    Blog_img=db.Column(db.String,default="no-img.jpeg")
    Blog_preview = db.Column(db.String)
    Blog_content = db.Column(db.String)
    Blog_time=db.Column(db.DateTime(timezone=True),default=datetime.now())
    total_comments=db.Column(db.Integer,default=0)
    likes=db.Column(db.Integer,default=0)
    dislikes=db.Column(db.Integer,default=0)
    user_name=db.Column(db.String)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    



class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    profile_img=db.Column(db.String,default="no-profile-pic.jpeg")
    fullname = db.Column(db.String)
    about = db.Column(db.String)
    totalposts=db.Column(db.Integer,default=0)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'))


class Comments(db.Model):
    __tablename__="comments"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_name=db.Column(db.String,db.ForeignKey('users.user_name'))
    blog_id=db.Column(db.Integer,db.ForeignKey('blogs.id'))
    comment_time=db.Column(db.DateTime(timezone=True),default=datetime.now())
    comment=db.Column(db.String)
class Likes(db.Model):
    __tablename__="likes"
    user_name=db.Column(db.String,db.ForeignKey('users.user_name'),primary_key=True)
    blog_id=db.Column(db.Integer,db.ForeignKey('blogs.id'),primary_key=True)

class Dislikes(db.Model):
    __tablename__="dislikes"
    user_name=db.Column(db.String,db.ForeignKey('users.user_name'),primary_key=True)
    blog_id=db.Column(db.Integer,db.ForeignKey('blogs.id'),primary_key=True)
