import json
from typing import Any, Dict

from app.config import settings


def load_analysis_mock() -> Dict[str, Any]:
    with settings.analysis_mock_path.open("r", encoding="utf-8") as f:
        return json.load(f)
