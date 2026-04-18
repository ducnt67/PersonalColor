import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"

PALETTES_DIR = DATA_DIR / "palettes"
PROFILES_DIR = DATA_DIR / "profiles"

MODEL_PATH = MODELS_DIR / "best_personal_color_model.pth"
STYLE_CSS_PATH = ASSETS_DIR / "css" / "style.css"

# Constants
FITZ_MAP = {
    0: "Type 1",
    1: "Type 2",
    2: "Type 3",
    3: "Type 4",
    4: "Type 5",
    5: "Type 6"
}

UNDER_MAP = {
    0: "Lạnh (Cool)",
    1: "Trung tính (Neutral)",
    2: "Ấm (Warm)"
}

SEASON_MAP = {
    0: "Spring",
    1: "Summer",
    2: "Autumn",
    3: "Winter"
}

SEASON_DESC = {
    "Spring": "Tươi sáng, mềm mại và đầy sức sống. Hợp với các gam màu trong trẻo, nhẹ nhàng và nữ tính.",
    "Summer": "Dịu mát, thanh lịch, tinh tế. Hợp với những màu lạnh, mềm và không quá chói.",
    "Autumn": "Ấm, sâu, sang và trưởng thành. Rất hợp với các gam đất, caramel, olive, nâu ấm.",
    "Winter": "Sắc nét, tương phản cao, hiện đại. Hợp với những màu rõ, lạnh và nổi bật."
}

SEASON_STYLE_TIPS = {
    "Spring": [
        "Ưu tiên các outfit sáng, nhẹ, tươi mới và trẻ trung.",
        "Trang sức vàng nhạt hoặc rose gold thường tạo cảm giác hài hòa.",
        "Makeup hợp: coral, peach, warm pink, champagne."
    ],
    "Summer": [
        "Ưu tiên các tông lạnh nhẹ, mềm và thanh lịch.",
        "Trang sức bạc, platinum hoặc vàng trắng thường phù hợp hơn.",
        "Makeup hợp: dusty rose, cool pink, mauve, soft berry."
    ],
    "Autumn": [
        "Ưu tiên tông đất, trầm ấm, tạo cảm giác sang và sâu.",
        "Trang sức vàng cổ điển, bronze, copper khá phù hợp.",
        "Makeup hợp: terracotta, brick, cinnamon, warm nude."
    ],
    "Winter": [
        "Ưu tiên màu sắc rõ, sạch, độ tương phản cao.",
        "Trang sức bạc, kim loại sáng, đá lạnh sẽ nổi bật hơn.",
        "Makeup hợp: ruby, berry, wine, cool red, mauve lạnh."
    ]
}
