# utils/style_helper.py
from datetime import datetime

STYLE_DATA = {
    "professional": {
        "name": "Professional & High-Stakes",
        "materials": ["worsted wool", "high-twist cotton", "wool", "cotton", "silk"],
        "patterns": ["pinstripe", "micro-check", "solid", "subtle", "plain"],
        "colors": ["navy", "charcoal", "grey", "white", "black", "dark blue"],
        "key_categories": [
            "blazer",
            "trousers",
            "suit",
            "dress shirt",
            "oxfords",
            "pumps",
            "tie",
        ],
    },
    "date_night": {
        "name": "Date Night & Social Evenings",
        "materials": ["silk", "suede", "velvet", "merino wool", "leather", "cashmere"],
        "patterns": ["shadow stripe", "floral", "polka dot", "subtle"],
        "colors": [
            "burgundy",
            "emerald",
            "green",
            "black",
            "espresso",
            "dark brown",
            "midnight",
        ],
        "key_categories": [
            "leather jacket",
            "turtleneck",
            "dark wash denim",
            "slip dress",
            "slim-fit",
            "gown",
            "cocktail dress",
            "sequin",
            "velvet",
        ],
    },
    "smart_casual": {
        "name": "Smart Casual",
        "materials": ["chambray", "oxford cloth", "knit", "cotton", "twill", "denim"],
        "patterns": ["windowpane", "breton stripe", "gingham", "check", "striped"],
        "colors": [
            "beige",
            "olive",
            "slate",
            "grey",
            "terracotta",
            "cobalt blue",
            "navy",
            "white",
        ],
        "key_categories": [
            "chinos",
            "chelsea boots",
            "loafers",
            "white sneakers",
            "button-down",
        ],
    },
    "relaxed": {
        "name": "Relaxed & Travel",
        "materials": ["jersey", "tencel", "linen", "fleece", "stretch", "cotton blend"],
        "patterns": ["graphic", "large check", "camo", "bold print"],
        "colors": ["heather grey", "sage green", "orange", "warm", "light blue"],
        "key_categories": [
            "hoodie",
            "drawstring trousers",
            "bomber jacket",
            "canvas tote",
            "sweatshirt",
        ],
    },
}

SEASON_DATA = {
    "spring": {
        "name": "Spring",
        "materials": ["linen blend", "light cotton", "silk", "cotton"],
        "patterns": ["floral", "light stripe", "subtle"],
        "colors": [
            "pastel",
            "mint green",
            "cream",
            "light blue",
            "soft pink",
            "lavender",
        ],
        "key_categories": [
            "chinos",
            "light knit sweater",
            "trench coat",
            "light jacket",
        ],
    },
    "summer": {
        "name": "Summer",
        "materials": ["linen", "seersucker", "poplin", "cotton", "bamboo"],
        "patterns": ["gingham", "tropical", "striped", "bold"],
        "colors": ["white", "yellow", "ocean blue", "light blue", "coral", "beige"],
        "key_categories": ["knit polo", "linen shirt", "loafers", "shorts", "sundress"],
    },
    "autumn": {
        "name": "Autumn",
        "materials": ["flannel", "corduroy", "suede", "wool", "cotton"],
        "patterns": ["plaid", "herringbone", "check", "tartan"],
        "colors": ["rust", "olive green", "mustard", "brown", "burgundy", "orange"],
        "key_categories": ["boots", "overshirt", "shacket", "wool trousers", "scarf"],
    },
    "winter": {
        "name": "Winter",
        "materials": ["wool", "cashmere", "thick denim", "fleece", "heavy cotton"],
        "patterns": ["fair isle", "tweed", "herringbone", "knit", "solid"],
        "colors": ["burgundy", "navy", "forest green", "dark red", "charcoal", "black"],
        "key_categories": [
            "overcoat",
            "turtleneck",
            "scarf",
            "gloves",
            "thick sweater",
        ],
    },
}


def get_current_season():
    month = datetime.now().month
    if 3 <= month <= 5:
        return "spring"
    elif 6 <= month <= 8:
        return "summer"
    elif 9 <= month <= 11:
        return "autumn"
    else:
        return "winter"


def categorize_item(item):
    """Return category: top, bottom, footwear, accessory, onepiece, other"""
    if not item or not item.category:
        return "other"
    cat = item.category.lower()
    # First check for sets (multi‑piece items)
    set_keywords = [
        "set",
        "kurta set",
        "lehenga set",
        "sherwani set",
        "salwar set",
        "indo-western set",
    ]
    if any(k in cat for k in set_keywords):
        return "onepiece"
    # Regular categories
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
    accessory_keywords = [
        "watch",
        "belt",
        "bag",
        "cap",
        "hat",
        "sunglasses",
        "scarf",
        "jewellery",
        "tie",
    ]
    onepiece_keywords = ["dress", "gown", "jumpsuit", "romper"]
    if cat in top_keywords:
        return "top"
    elif cat in bottom_keywords:
        return "bottom"
    elif cat in footwear_keywords:
        return "footwear"
    elif cat in accessory_keywords:
        return "accessory"
    elif cat in onepiece_keywords:
        return "onepiece"
    return "other"


def score_item_for_style_season(item, style_key, season_key, preferred_color=""):
    if not item:
        return 0
    style = STYLE_DATA.get(style_key, STYLE_DATA["smart_casual"])
    season = SEASON_DATA.get(season_key, SEASON_DATA["spring"])
    score = 0
    cat = (item.category or "").lower()
    # Material
    if item.material:
        mat = item.material.lower()
        if any(m in mat for m in style["materials"]):
            score += 15
        if any(m in mat for m in season["materials"]):
            score += 15
    # Pattern
    if item.pattern:
        pat = item.pattern.lower()
        if any(p in pat for p in style["patterns"]):
            score += 10
        if any(p in pat for p in season["patterns"]):
            score += 10
    # Color
    if item.color:
        col = item.color.lower()
        if any(c in col for c in style["colors"]):
            score += 15
        if any(c in col for c in season["colors"]):
            score += 10
        if preferred_color and preferred_color in col:
            score += 5
    # Category/key items
    if item.category:
        if any(k in cat for k in style["key_categories"]):
            score += 10
        if any(k in cat for k in season["key_categories"]):
            score += 10
    # Style penalties
    if style_key == "professional":
        if "jeans" in cat:
            score -= 80
        if "t-shirt" in cat or "tshirt" in cat:
            score -= 80
        if "short" in cat:
            score -= 80
        if "hoodie" in cat or "sweater" in cat:
            score -= 60
        if "dress" in cat:
            formal = (
                item.color
                and item.color.lower()
                in ["black", "navy", "charcoal", "grey", "dark blue"]
            ) and (
                not item.pattern
                or item.pattern.lower() in ["solid", "plain", "pinstripe"]
            )
            if not formal:
                score -= 50
            else:
                score += 20
        if "trousers" in cat or ("pants" in cat and "jeans" not in cat):
            score += 30
        if "dress shirt" in cat or ("shirt" in cat and "t-shirt" not in cat):
            score += 30
        if "blazer" in cat or "suit" in cat:
            score += 40
        if "denim" in cat and "jacket" in cat:
            score -= 40
    if style_key == "relaxed":
        if "blazer" in cat or "suit" in cat or "tie" in cat:
            score -= 30
    if style_key == "date_night":
        if "t-shirt" in cat or "hoodie" in cat:
            score -= 20
    return max(0, min(score, 100))


def colors_match(c1, c2):
    if not c1 or not c2:
        return True
    c1, c2 = c1.lower(), c2.lower()
    if c1 == c2:
        return True
    neutral = [
        "black",
        "white",
        "grey",
        "gray",
        "beige",
        "navy",
        "brown",
        "cream",
        "tan",
    ]
    if c1 in neutral or c2 in neutral:
        return True
    good_pairs = [
        ("blue", "white"),
        ("blue", "black"),
        ("blue", "grey"),
        ("red", "black"),
        ("red", "white"),
        ("red", "blue"),
        ("green", "beige"),
        ("green", "brown"),
        ("green", "black"),
        ("pink", "white"),
        ("pink", "black"),
        ("pink", "grey"),
        ("yellow", "blue"),
        ("yellow", "black"),
        ("yellow", "white"),
        ("purple", "white"),
        ("purple", "black"),
        ("purple", "grey"),
        ("orange", "black"),
        ("orange", "brown"),
        ("orange", "white"),
    ]
    return (c1, c2) in good_pairs or (c2, c1) in good_pairs


def infer_style_from_item(item):
    if not item:
        return "smart_casual"
    scores = {}
    current_season = get_current_season()
    for sk in STYLE_DATA:
        scores[sk] = score_item_for_style_season(item, sk, current_season)
    return max(scores, key=scores.get)


def map_occasion_to_style(occasion):
    occ = (occasion or "").lower()
    if occ in ["party", "wedding", "celebration", "festival", "cocktail", "evening"]:
        return "date_night"
    elif occ in ["formal", "interview", "meeting", "work", "business", "office"]:
        return "professional"
    elif occ in ["casual", "everyday", "college", "weekend", "shopping"]:
        return "smart_casual"
    elif occ in ["relaxed", "travel", "vacation", "gym", "sports", "hiking"]:
        return "relaxed"
    else:
        return "smart_casual"


def map_season_input(season_str):
    s = (season_str or "").lower()
    if s == "summer":
        return "summer"
    elif s == "winter":
        return "winter"
    elif s == "spring":
        return "spring"
    elif s in ["autumn", "fall"]:
        return "autumn"
    elif s == "rainy":
        return "spring"
    else:
        return get_current_season()
