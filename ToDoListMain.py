from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user



app = Flask(__name__)
load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

database = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/Login"

class User(UserMixin, database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(20), unique=True, nullable=False)
    password = database.Column(database.String(20), nullable=False)
    to_do_list_entries = database.relationship("Tasks", backref="user", lazy=True)

class Tasks(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'))
    to_do = database.Column(database.String(250), nullable=False)
