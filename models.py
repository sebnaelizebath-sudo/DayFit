from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(255))
    google_id = db.Column(db.String(255))
    profile_pic = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WardrobeItem(db.Model):
    __tablename__ = "wardrobe_item"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80))
    color = db.Column(db.String(50))
    season = db.Column(db.String(50))
    occasion = db.Column(db.String(50))  # <-- fixed: removed extra db.Column wrapper
    material = db.Column(db.String(80))
    pattern = db.Column(db.String(80))
    image_path = db.Column(db.String(300))
    status = db.Column(db.String(20), default="unused")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FavoriteOutfit(db.Model):
    __tablename__ = "favorite_outfit"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    top_id = db.Column(db.Integer, db.ForeignKey("wardrobe_item.id"), nullable=True)
    bottom_id = db.Column(db.Integer, db.ForeignKey("wardrobe_item.id"), nullable=True)
    footwear_id = db.Column(
        db.Integer, db.ForeignKey("wardrobe_item.id"), nullable=True
    )
    accessory_id = db.Column(
        db.Integer, db.ForeignKey("wardrobe_item.id"), nullable=True
    )
    used_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # relationships
    top = db.relationship("WardrobeItem", foreign_keys=[top_id])
    bottom = db.relationship("WardrobeItem", foreign_keys=[bottom_id])
    footwear = db.relationship("WardrobeItem", foreign_keys=[footwear_id])
    accessory = db.relationship("WardrobeItem", foreign_keys=[accessory_id])


class SavedOutfit(db.Model):
    __tablename__ = "saved_outfit"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(120), default="Outfit")
    top_name = db.Column(db.String(120))
    bottom_name = db.Column(db.String(120))
    footwear_name = db.Column(db.String(120))
    accessory_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
