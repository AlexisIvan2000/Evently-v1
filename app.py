from flask import Flask,render_template, request, url_for, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user,logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from sqlalchemy import or_
import os, requests

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///datas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "evently2000"

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config['MAIL_USE_TLS'] = False
app.config["MAIL_USERNAME"] = os.environ.get("GMAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("GMAIL_PASSWORD","")
app.config["TICKETMASTER_API_KEY"] = os.environ.get("TICKETMASTER_API_KEY","")
mail = Mail(app)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(90))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("username").strip()
        password = request.form.get("password")
        user = Users.query.filter(
               or_(Users.username == identifier, Users.email == identifier)).first()

        if  user and check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for("events"))
        else:
            flash("Invalid username/email or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("All fields are required", "error")
            return redirect(url_for("register"))
        

        if Users.query.filter_by(username=username).first():
            flash("An account already exists with this username!", "error")
            return redirect(url_for("register"))
        if Users.query.filter_by(email=email).first():
            flash("An account already exists with this email!", "error")
            return redirect(url_for("register"))
        
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = Users(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        try:
            msg = Message(
                subject="Registration",
                recipients=[email],
                body=f"Welcome to Evently {username}!\n\nYour account has been created successfully."
            )

            mail.send(msg)
        except Exception as e:
            app.logger.warning(f"Email could not be sent: {e}")

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

    

@app.route("/event")
@login_required
def events():
    return render_template("event.html", username=current_user.username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/api/events")
@login_required
def api_events():
    city = request.args.get("city")
    state = request.args.get("state")
    type_event = request.args.get("type")
    page = request.args.get("page", 0)  

    params = {
        "apikey": app.config["TICKETMASTER_API_KEY"],
        "size": 10,  
        "page": page  
    }
    if city:
        params["city"] = city
    if state:
        params["stateCode"] = state
    if type_event:
        params["classificationName"] = type_event

    response = requests.get("https://app.ticketmaster.com/discovery/v2/events.json", params=params)

    events_data = []
    total_pages = 0

    if response.status_code == 200:
        data = response.json()
        if "page" in data:
            total_pages = data["page"]["totalPages"]
        if "_embedded" in data and "events" in data["_embedded"]:
            for e in data["_embedded"]["events"]:
                events_data.append({
                    "name": e["name"],
                    "date": e["dates"]["start"]["localDate"],
                    "url": e["url"],
                    "venue": e["_embedded"]["venues"][0]["name"] if "_embedded" in e and "venues" in e["_embedded"] else "",
                    "city": e["_embedded"]["venues"][0]["city"]["name"] if "_embedded" in e and "venues" in e["_embedded"] else ""
                })

    return {"events": events_data, "total_pages": total_pages, "current_page": int(page)}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)