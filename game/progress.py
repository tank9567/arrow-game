"""진행 상황 저장/불러오기.

현재 도달한 레벨 인덱스를 save.json(프로젝트 루트)에 저장한다.
"""
import json
import os

SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save.json")


def load_progress() -> int:
    """저장된 레벨 인덱스를 반환. 없으면 0."""
    try:
        with open(SAVE_PATH, encoding="utf-8") as f:
            return int(json.load(f).get("level_index", 0))
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        return 0


def save_progress(level_index: int):
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump({"level_index": level_index}, f)
