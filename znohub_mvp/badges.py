import json
import os
import time

BADGES = {
    "Стародавня історія України": {
        "emoji": "🪨",
        "title": "Кам'яна людина",
        "desc": "Ти знаєш стародавню історію як справжній трипілець!",
        "image": "images/badge_ancient.jpeg",
    },
    "Козацька Україна": {
        "emoji": "⚔️",
        "title": "Козацький характер",
        "desc": "Гетьмани б тобою пишалися!",
        "image": "images/badge_cossack.jpeg",
    },
    "Художні роботи": {
        "emoji": "🎨",
        "title": "Знавець мистецтв",
        "desc": "Шевченко і Білокур схвалюють!",
        "image": "images/badge_art.jpeg",
    },
}

BADGES_FILE = "badges.json"


def load_badges():
    if os.path.exists(BADGES_FILE):
        with open(BADGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_badge(topic):
    data = load_badges()
    data[topic] = {"earned_at": time.strftime("%Y-%m-%d %H:%M")}
    with open(BADGES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)