"""레벨 데이터 -> Board 변환 및 JSON 레벨 로딩.

levels/ 폴더의 level_*.json 파일들을 이름순으로 읽어 레벨 목록을 만든다.
레벨 추가 = JSON 파일 추가 (코드 수정 불필요).
"""
import json
import os
import glob

from game.arrow import Arrow, Direction
from game.board import Board

LEVELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "levels")

# 방향 문자열 -> Direction Enum
DIR_MAP = {
    "UP": Direction.UP,
    "DOWN": Direction.DOWN,
    "LEFT": Direction.LEFT,
    "RIGHT": Direction.RIGHT,
}


def _validate_arrow(cells, direction):
    """화살표 데이터의 형식 오류를 로딩 단계에서 잡는다.

    - cells 는 상/하/좌/우로 한 칸씩 이어져야 한다(인접성).
    - dir(머리 방향)은 경로의 '마지막 세그먼트 방향'과 일치해야 한다.
      (어긋나면 화살촉이 뒤집혀 보이므로 막는다)
    """
    if len(cells) < 1:
        raise ValueError(f"화살표 cells 가 비어 있음: {cells}")
    for (r1, c1), (r2, c2) in zip(cells, cells[1:]):
        if abs(r2 - r1) + abs(c2 - c1) != 1:
            raise ValueError(f"화살표 cells 가 인접하지 않음: {(r1,c1)} -> {(r2,c2)}")
    if len(cells) >= 2:
        (r1, c1), (r2, c2) = cells[-2], cells[-1]
        seg = (r2 - r1, c2 - c1)
        if seg != direction.delta:
            raise ValueError(
                f"화살촉 방향(dir={direction.name}={direction.delta})이 "
                f"경로 끝 방향({seg})과 어긋남(뒤집힘): cells={cells}"
            )


def build_board(data: dict) -> Board:
    """레벨 dict 로부터 Board 객체를 생성한다.

    각 화살표는 cells(꼬리->머리 셀 목록) + dir(머리 방향) 로 정의된다.
    """
    arrows = []
    for a in data["arrows"]:
        direction = DIR_MAP[a["dir"]]
        _validate_arrow(a["cells"], direction)
        arrows.append(Arrow(a["cells"], direction))
    return Board(rows=data["rows"], cols=data["cols"], arrows=arrows)


def load_levels() -> list:
    """levels/level_*.json 들을 이름순으로 읽어 리스트로 반환."""
    paths = sorted(glob.glob(os.path.join(LEVELS_DIR, "level_*.json")))
    levels = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            levels.append(json.load(f))
    return levels


# 모듈 로드 시 한 번 읽어 캐시
LEVELS = load_levels()


def level_count() -> int:
    return len(LEVELS)


def get_level(index: int) -> dict:
    """index(0-based) 레벨 데이터를 반환."""
    return LEVELS[index]
