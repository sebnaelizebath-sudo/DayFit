from flask import Blueprint, redirect, session, request, url_for
from extensions import db, bcrypt
from models import User
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
import os
import pathlib

google_bp = Blueprint("google", __name__)

# =========================
# CONFIG
# =========================
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = (
    "860199755249-srb5ftm9qdctc8obmo86ee5vi5t6k6kk.apps.googleusercontent.com"
)

# IMPORTANT: correct path
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_uri="http://127.0.0.1:5000/auth/callback",
)


# =========================
# LOGIN GOOGLE
# =========================
@google_bp.route("/login/google")
def login_google():
    flow.authorization_url(prompt="consent")

    authorization_url, state = flow.authorization_url()
    session["state"] = state

    return redirect(authorization_url)


# =========================
# CALLBACK
# =========================
@google_bp.route("/google/callback")
def callback():

    # 🔐 STATE CHECK (IMPORTANT SECURITY FIX)
    if session.get("state") != request.args.get("state"):
        return "State mismatch error", 400

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    request_session = google.auth.transport.requests.Request()

    # ✅ SAFE ID TOKEN
    id_info = id_token.verify_oauth2_token(
        credentials._id_token, request_session, GOOGLE_CLIENT_ID
    )

    email = id_info.get("email")
    name = id_info.get("name")
    picture = id_info.get("picture")
    google_id = id_info.get("sub")

    # =========================
    # USER CHECK / CREATE
    # =========================
    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email, google_id=google_id, profile_pic=picture)
        db.session.add(user)
        db.session.commit()

    # =========================
    # SESSION
    # =========================
    session["user_id"] = user.id

    return redirect(url_for("main.dashboard"))


# =========================
# LOGOUT
# =========================
@google_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login_page"))
