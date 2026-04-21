import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from models import db
from extensions import bcrypt

# Load environment variables
load_dotenv()

# Blueprints
from auth.routes import auth_bp
from dashboard.routes import dashboard_bp
from wardrobe.routes import wardrobe_bp
from recommendations.routes import recommendations_bp
from favorites.routes import favorites_bp
from chatbot.routes import chatbot_bp
from profile.routes import profile_bp
from match.routes import match_bp

# Optional main blueprint (if you have one)
try:
    from routes.main_routes import main_bp

    HAS_MAIN_BP = True
except ImportError:
    HAS_MAIN_BP = False

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///dayfit.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max upload

# Create upload folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(wardrobe_bp, url_prefix="/wardrobe")
app.register_blueprint(recommendations_bp, url_prefix="/recommendations")
app.register_blueprint(favorites_bp, url_prefix="/favorites")
app.register_blueprint(chatbot_bp, url_prefix="/chatbot")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(match_bp, url_prefix="/match")

# If you have a main blueprint (for root routes)
if HAS_MAIN_BP:
    app.register_blueprint(main_bp)


# Fallback root route (if no main blueprint)
@app.route("/")
def home():
    return redirect(url_for("auth.landing_page"))


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return (
        """
    <html>
    <body style="background:#0b1120;color:white;text-align:center;padding:50px;">
        <h1>404</h1>
        <h3>Page Not Found</h3>
        <a href="/" style="color:#22c55e;">Go Home</a>
    </body>
    </html>
    """,
        404,
    )


@app.errorhandler(500)
def server_error(error):
    return (
        """
    <html>
    <body style="background:#0b1120;color:white;text-align:center;padding:50px;">
        <h1>500</h1>
        <h3>Internal Server Error</h3>
        <a href="/" style="color:#22c55e;">Go Home</a>
    </body>
    </html>
    """,
        500,
    )


# Create database tables (only if they don't exist)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
