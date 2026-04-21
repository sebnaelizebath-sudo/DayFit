import os
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
from models import db, WardrobeItem, FavoriteOutfit
from utils.style_helper import (
    STYLE_DATA,
    SEASON_DATA,
    get_current_season,
    score_item_for_style_season,
    categorize_item,
)

wardrobe_bp = Blueprint("wardrobe", __name__, url_prefix="/wardrobe")


def login():
    return "user_id" in session


# ------------------------------
# AI DETECTION FUNCTIONS
# ------------------------------
def detect_season(category, material="", pattern="", color=""):
    """Smart season detection using category, material, pattern, and color."""
    cat = (category or "").lower()
    mat = (material or "").lower()
    pat = (pattern or "").lower()
    col = (color or "").lower()

    # Winter
    winter_materials = ["wool", "cashmere", "fleece", "thermal", "flannel"]
    winter_cats = ["coat", "jacket", "sweater", "hoodie", "boots"]
    if any(m in mat for m in winter_materials) or any(c in cat for c in winter_cats):
        return "Winter"

    # Rainy
    rainy_cats = ["raincoat", "umbrella", "waterproof"]
    if any(c in cat for c in rainy_cats) or "waterproof" in mat:
        return "Rainy"

    # Summer
    summer_materials = ["linen", "cotton", "seersucker", "poplin", "bamboo"]
    summer_cats = ["shorts", "t-shirt", "tank top", "sundress", "sandals"]
    summer_patterns = ["tropical", "gingham", "bold"]
    if (
        any(m in mat for m in summer_materials)
        or any(c in cat for c in summer_cats)
        or any(p in pat for p in summer_patterns)
    ):
        return "Summer"

    # Versatile items → All Season
    versatile_cats = [
        "jeans",
        "chinos",
        "shirt",
        "blouse",
        "skirt",
        "dress",
        "trousers",
        "kurta",
        "kurti",
    ]
    if any(c in cat for c in versatile_cats):
        return "All Season"

    return "Multi Season"


def detect_occasion(category, pattern="", color="", material=""):
    """Smart occasion detection using category, pattern, color, and material."""
    cat = (category or "").lower()
    pat = (pattern or "").lower()
    col = (color or "").lower()
    mat = (material or "").lower()

    # Festive / Wedding / Party (highest priority)
    festive_categories = [
        "kurta set",
        "lehenga set",
        "sherwani set",
        "salwar set",
        "indo-western set",
        "set (2-piece)",
        "set (3-piece)",
    ]
    festive_patterns = [
        "embroidered",
        "embroidery",
        "zari",
        "zardosi",
        "sequin",
        "stone work",
        "mirror work",
        "gota patti",
        "bandhani",
        "patola",
    ]
    festive_materials = [
        "silk",
        "banarasi",
        "kanjeevaram",
        "brocade",
        "velvet",
        "chanderi",
        "satin",
    ]
    festive_colors = [
        "orange",
        "maroon",
        "burgundy",
        "red",
        "gold",
        "royal blue",
        "emerald",
        "purple",
        "pink",
        "magenta",
        "yellow",
    ]

    if (
        any(k in cat for k in festive_categories)
        or any(p in pat for p in festive_patterns)
        or any(m in mat for m in festive_materials)
        or any(c in col for c in festive_colors)
    ):
        return "Party"

    # Formal
    formal_keywords = [
        "blazer",
        "suit",
        "tie",
        "dress shirt",
        "trousers",
        "pumps",
        "oxfords",
    ]
    if any(k in cat for k in formal_keywords):
        return "Formal"

    # Gym
    gym_keywords = ["gym", "sports", "track", "joggers", "leggings", "active", "sweat"]
    if any(k in cat for k in gym_keywords) or any(
        p in pat for p in ["sport", "athletic"]
    ):
        return "Gym"

    # Casual patterns
    casual_patterns = [
        "graphic",
        "print",
        "logo",
        "cartoon",
        "stripes",
        "check",
        "floral",
    ]
    if any(p in pat for p in casual_patterns):
        return "Casual"

    # Casual categories
    casual_cats = [
        "t-shirt",
        "jeans",
        "hoodie",
        "sweater",
        "shorts",
        "skirt",
        "top",
        "kurti",
        "kurta",
    ]
    if any(k in cat for k in casual_cats):
        return "Casual"

    # Dresses
    if "dress" in cat:
        work_friendly_colors = [
            "black",
            "navy",
            "grey",
            "charcoal",
            "dark blue",
            "brown",
            "beige",
        ]
        work_friendly_patterns = [
            "solid",
            "plain",
            "pinstripe",
            "micro-check",
            "subtle",
        ]
        if (pat in work_friendly_patterns or pat == "") and any(
            c in col for c in work_friendly_colors
        ):
            return "Work"
        else:
            return "Casual"

    # Work / smart casual
    work_keywords = ["shirt", "blouse", "trousers", "pants", "skirt", "chinos"]
    if any(k in cat for k in work_keywords):
        if any(p in pat for p in ["floral", "graphic", "embroidered"]):
            return "Casual"
        return "Work"

    return "Casual"


# ------------------------------
# WARDROBE PAGE
# ------------------------------
@wardrobe_bp.route("/")
def wardrobe_page():
    if not login():
        return redirect(url_for("auth.login_page"))

    user_id = session["user_id"]
    items = WardrobeItem.query.filter_by(user_id=user_id).all()

    # Count categories (comprehensive keyword lists)
    top_keywords = [
        "shirt",
        "t-shirt",
        "tshirt",
        "top",
        "blouse",
        "kurti",
        "hoodie",
        "sweater",
        "jacket",
        "coat",
        "blazer",
    ]
    bottom_keywords = [
        "jeans",
        "pants",
        "trousers",
        "shorts",
        "skirt",
        "leggings",
        "cargo",
        "joggers",
    ]
    footwear_keywords = [
        "shoes",
        "sneakers",
        "boots",
        "sandals",
        "heels",
        "loafers",
        "flats",
        "oxfords",
    ]

    tops = bottoms = footwear = 0
    for item in items:
        cat = (item.category or "").lower().strip()
        if cat in top_keywords:
            tops += 1
        elif cat in bottom_keywords:
            bottoms += 1
        elif cat in footwear_keywords:
            footwear += 1

    # Intelligent gap analysis using style helper
    covered_styles = set()
    covered_seasons = set()
    current_season = get_current_season()

    for item in items:
        for style_key in STYLE_DATA:
            if score_item_for_style_season(item, style_key, current_season) > 30:
                covered_styles.add(style_key)
        if item.season:
            s = item.season.lower()
            if s == "all season":
                covered_seasons.update(["spring", "summer", "autumn", "winter"])
            elif s == "summer":
                covered_seasons.add("summer")
            elif s == "winter":
                covered_seasons.add("winter")
            elif s == "spring":
                covered_seasons.add("spring")
            elif s == "autumn":
                covered_seasons.add("autumn")
            elif s == "rainy":
                covered_seasons.add("spring")

    missing_items = []
    all_styles = set(STYLE_DATA.keys())
    for style in all_styles - covered_styles:
        missing_items.append(
            (
                f"Need {STYLE_DATA[style]['name']} Style",
                f"No items for {STYLE_DATA[style]['name'].lower()} style. Try adding a {STYLE_DATA[style]['key_categories'][0]}.",
            )
        )

    if current_season not in covered_seasons:
        season_name = SEASON_DATA[current_season]["name"]
        missing_items.append(
            (
                f"Need {season_name} Wear",
                f"No {season_name.lower()}-appropriate items. Consider adding {SEASON_DATA[current_season]['key_categories'][0]}.",
            )
        )

    # Basic category checks
    if tops == 0:
        missing_items.append(
            ("Need Tops", "Add shirts, t-shirts, or tops to your wardrobe.")
        )
    if bottoms == 0:
        missing_items.append(("Need Bottoms", "Add jeans, trousers, or skirts."))
    if footwear == 0:
        missing_items.append(("Need Footwear", "Add shoes, sneakers, or sandals."))

    return render_template(
        "wardrobe.html",
        items=items,
        total=len(items),
        tops=tops,
        bottoms=bottoms,
        footwear=footwear,
        missing_items=missing_items,
    )


# ------------------------------
# ADD ITEM
# ------------------------------
@wardrobe_bp.route("/add", methods=["GET", "POST"])
def add_item_route():
    if not login():
        return redirect(url_for("auth.login_page"))
    if request.method == "POST":
        category = request.form["category"]
        material = request.form.get("material", "")
        color = request.form.get("color", "")
        pattern = request.form.get("pattern", "")

        season = detect_season(category, material, pattern, color)
        occasion = detect_occasion(category, pattern, color, material)

        image = request.files.get("image")
        image_path = ""
        if image and image.filename:
            filename = secure_filename(image.filename)
            folder = os.path.join("static", "uploads")
            os.makedirs(folder, exist_ok=True)
            save_path = os.path.join(folder, filename)
            image.save(save_path)
            image_path = f"uploads/{filename}"

        item = WardrobeItem(
            user_id=session["user_id"],
            name=request.form["name"],
            category=category,
            color=color,
            material=material,
            pattern=pattern,
            season=season,
            occasion=occasion,
            image_path=image_path,
        )
        db.session.add(item)
        db.session.commit()
        flash("Item added successfully", "success")
        return redirect(url_for("wardrobe.wardrobe_page"))
    return render_template("add_item.html")


# ------------------------------
# EDIT ITEM
# ------------------------------
@wardrobe_bp.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if not login():
        return redirect(url_for("auth.login_page"))
    item = WardrobeItem.query.get_or_404(item_id)
    if request.method == "POST":
        category = request.form["category"]
        material = request.form.get("material", "")
        color = request.form.get("color", "")
        pattern = request.form.get("pattern", "")

        item.name = request.form["name"]
        item.category = category
        item.color = color
        item.material = material
        item.pattern = pattern
        item.season = detect_season(category, material, pattern, color)
        item.occasion = detect_occasion(category, pattern, color, material)

        image = request.files.get("image")
        if image and image.filename:
            filename = secure_filename(image.filename)
            folder = os.path.join("static", "uploads")
            os.makedirs(folder, exist_ok=True)
            save_path = os.path.join(folder, filename)
            image.save(save_path)
            item.image_path = f"uploads/{filename}"

        db.session.commit()
        flash("Item updated", "success")
        return redirect(url_for("wardrobe.wardrobe_page"))
    return render_template("edit_item.html", item=item)


# ------------------------------
# DELETE ITEM
# ------------------------------
@wardrobe_bp.route("/delete/<int:item_id>")
def delete_item(item_id):
    item = WardrobeItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted", "success")
    return redirect(url_for("wardrobe.wardrobe_page"))


# ------------------------------
# ADD TO FAVORITES (legacy, kept for compatibility)
# ------------------------------
@wardrobe_bp.route("/favorite/<int:item_id>")
def add_favorite(item_id):
    item = WardrobeItem.query.get_or_404(item_id)
    fav = FavoriteOutfit(
        user_id=session["user_id"],
        top_name=item.name,
        bottom_name="",
        footwear_name="",
        accessory_name="",
    )
    db.session.add(fav)
    db.session.commit()
    return redirect(url_for("favorites.favorites"))
