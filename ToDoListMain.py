from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash



app = Flask(__name__)
load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

database = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "Login"


class User(UserMixin, database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(20), unique=True, nullable=False)
    password = database.Column(database.String(20), nullable=False)
    to_do_list_entries = database.relationship("Tasks", backref="user", lazy=True)

class Tasks(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'))
    to_do = database.Column(database.String(250), nullable=False)

with app.app_context():
    database.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/SignUp", methods=["GET", "POST"])
def signup():

    error_message = None

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            error_message = "Username is taken"
            return render_template("signup.html", error=error_message)
        
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password=password_hash)
        database.session.add(new_user)
        database.session.commit()

        return redirect(url_for("login"))
    
    return render_template("signup.html")

@app.route("/Login", methods=["GET", "POST"])
def login():

    error_message = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("User logged in successfully")
            return redirect(url_for("userdashboard"))
        
        return render_template("login.html", error=error_message)
    
    return render_template("login.html")


@app.route("/UserDashboard", methods=["GET", "POST"])
@login_required
def userdashboard():

    if request.method == "POST":

        current_tasks_post = []
        action = request.form.get("action")

        if action == "addtask":

            task = request.form.get("task")

            newTask = Tasks(user_id=current_user.id, to_do=task)
            database.session.add(newTask)
            database.session.commit()
            
            tasks_data = Tasks.query.filter_by(user_id=current_user.id).all()
            
            for data in tasks_data:
                current_tasks_post.append(data)
        
            return render_template("dashboard.html", username=current_user.username, task_list=current_tasks_post)
        
        elif action == "deletetask":

            task_id = request.form.get("task_id")
            Tasks.query.filter_by(id=task_id, user_id=current_user.id).delete()
            database.session.commit()

            tasks_data = Tasks.query.filter_by(user_id=current_user.id).all()
            
            for data in tasks_data:
                current_tasks_post.append(data)
            
            return render_template("dashboard.html", username=current_user.username, task_list=current_tasks_post)

            
    
    elif request.method == "GET":
        current_task_get = []

        task_data = Tasks.query.filter_by(user_id=current_user.id).all()

        for data in task_data:
            current_task_get.append(data)
        return render_template("dashboard.html", username=current_user.username, task_list=current_task_get)

if __name__ == "__main__":
    app.run(debug=True)