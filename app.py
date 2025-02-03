from flask import Flask, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from openai import OpenAI

# Load environment variables
load_dotenv()
model = os.getenv("MODEL")
api_key = os.getenv("API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.secret_key = os.urandom(24)

# User credentials model
class UserCreds(db.Model):
    __tablename__ = 'new_user_creds'
    sNo = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(200), unique=True)

    def __init__(self, name, email, password=None, google_id=None):
        self.name = name
        self.email = email
        self.password = password
        self.google_id = google_id

# Create user-specific table
def create_db_table(email):
    table_name = f"{email.replace('@', '_').replace('.', '_')}_data"

    class Table(db.Model):
        __tablename__ = table_name
        sNo = db.Column(db.Integer, primary_key=True)
        prompt = db.Column(db.String(5000))
        responses = db.Column(db.String(8000))
        history = db.Column(db.JSON)
        timestamp = db.Column(db.DateTime, default=datetime.now())

        __table_args__ = {'extend_existing': True}

        def __init__(self, prompt, responses, history, timestamp):
            self.prompt = prompt
            self.responses = responses
            self.history = history
            self.timestamp = timestamp

    return Table

# Routes
@app.route("/", methods=['POST', 'GET'])
def signup_page():
    if request.method == 'POST':
        if request.is_json:
            data = request.json
            email = data.get("email")
            name = data.get("given_name")
            google_id = data.get("sub")

            existing_email = UserCreds.query.filter_by(email=email).first()

            if existing_email:
                flash('USER ALREADY EXISTS!', 'error')
                return jsonify({"success": True, "redirect_url": url_for('login_page', username=name)})
            else:
                new_user = UserCreds(name=name, email=email, google_id=google_id)
                db.session.add(new_user)
                db.session.commit()

                create_user_table(email)
                flash('Login Successful!', 'success')
                return jsonify({"success": True, "redirect_url": url_for('user_endpoint', username=name)})
        else:
            name = request.form.get("name")
            email = request.form.get("email")
            unhashed_password = request.form.get("password")
            password = bcrypt.generate_password_hash(unhashed_password).decode('utf-8')

            existing_email = UserCreds.query.filter_by(email=email).first()

            if existing_email:
                flash("USER ALREADY EXISTS!", "error")
                return redirect(url_for('signup_page'))
            else:
                new_user = UserCreds(name=name, email=email, password=password)
                db.session.add(new_user)
                db.session.commit()

                create_user_table(email)
                flash('Registered Successfully!', 'success')
                return redirect(url_for('login_page'))
    return render_template('signup.html')

@app.route("/login", methods=["POST", "GET"])
def login_page():
    if request.method == 'POST':
        if request.is_json:
            data = request.json
            email = data.get("email")
            password = data.get("ud")

            user = UserCreds.query.filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.password, password):
                username = user.name
                flash('Login Successful!', 'success')
                return jsonify({"success": True, "redirect_url": url_for('user_endpoint', username=username)})
            else:
                flash('Invalid Credentials, Please try again!', 'error')
                return jsonify({"success": False, "redirect_url": url_for('login_page')})
        else:
            email = request.form.get("email")
            password = request.form.get("password")

            user = UserCreds.query.filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.password, password):
                username = user.name
                flash('Login Successful!', 'success')
                return redirect(url_for('user_endpoint', username=username))
            else:
                flash('Invalid Credentials, Please try again!', 'error')

    return render_template('login.html')

@app.route("/<username>", methods=['POST', 'GET'])
def user_endpoint(username):
    user = UserCreds.query.filter_by(name=username).first()
    if not user:
        return "User not found", 404

    email = user.email
    table_model = create_db_table(email)

    if request.method == 'POST':
        prompt_data = request.form["prompt_data"]
        history = request.form.get("history")
        if history:
            history = json.loads(history)
        else:
            history = []
        history.append({"role": "user", "content": prompt_data})

        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'system', 'content': 'You are an assistant designed to extract key indicators and trading conditions from a given paragraph of information and generate a JSON file in a specific format structure.'}, *history],
            max_tokens=600,
            temperature=0.4
        )
        result = response.choices[0].message.content

        history.append({"role": 'assistant', "content": result})

        timestamp = datetime.now()

        create_entry = table_model(prompt=prompt_data, responses=result, history=history, timestamp=timestamp)
        db.session.add(create_entry)
        db.session.commit()

        return redirect(url_for('user_endpoint', username=username, result=result, history=json.dumps(history)))

    result = request.args.get('result')
    history = request.args.get('history', '[]')
    chat_history = table_model.query.all()
    return render_template('interfaceTesting.html', result=result, username=username, history=history,
                           chat_history=chat_history, timestamp=(datetime.now()).strftime('%d-%m-%Y %H:%M:%S'))

@app.route("/navigate_pages", methods=['POST'])
def navigate_pages():
    selected_users = request.form.get("users")
    return redirect(url_for('user_endpoint', username=selected_users))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Create user table function
def create_user_table(email):
    table_model = create_db_table(email)
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        existing_users = UserCreds.query.all()
        for user in existing_users:
            create_user_table(user.email)
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = False
    app.run()
