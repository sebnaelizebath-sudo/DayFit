# routes/main_routes.py
from flask import Blueprint, render_template, redirect, url_for, session

main_bp = Blueprint("main", __name__)


# ================= HOME PAGE =================
@main_bp.route("/")
def home():
    """Landing page for non‑authenticated users."""
    # If user is already logged in, redirect to dashboard
    if "user_id" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("landing.html")


# ================= DASHBOARD (if you want a shortcut) =================
@main_bp.route("/dashboard")
def dashboard_redirect():
    """Shortcut to the dashboard blueprint."""
    return redirect(url_for("dashboard.dashboard"))


# ================= ADD ITEM (optional – use wardrobe blueprint instead) =================
# This is kept for backward compatibility; the actual add item is in wardrobe blueprint.
@main_bp.route("/add_item")
def add_item_redirect():
    return redirect(url_for("wardrobe.add_item_route"))
