"""화살표 데이터 모델 및 렌더링 (경로형).

Direction : 머리(화살촉)가 가리키는 방향 (dr, dc)
Arrow     : 여러 칸을 잇는 꺾인 경로(cells) + 머리 방향
            cells 는 '꼬리 -> 머리' 순서이며, cells[-1] 이 머리 칸이다.
"""
from enum import Enum
import pygame
import config as cfg


class Direction(Enum):
    UP    = (-1,  0)
    DOWN  = ( 1,  0)
    LEFT  = ( 0, -1)
    RIGHT = ( 0,  1)

    @property
    def delta(self):
        return self.value


class Arrow:
    def __init__(self, cells, direction: Direction):
        self.cells = [tuple(c) for c in cells]   # [(row, col), ...] 꼬리 -> 머리
        self.direction = direction
        self.is_removed = False
        self.is_blocked = False
        self.hidden = False        # 애니메이션 중 board.draw 에서 제외(PlayScene이 직접 그림)

    @property
    def head(self):
        return self.cells[-1]                     # 머리 칸

    def draw(self, screen, origin_x, origin_y, cell):
        """꺾인 꼬리(폴리라인) + 머리 화살촉을 그린다. (cell = 셀 픽셀 크기)"""
        if self.is_removed:
            return

        def center(r, c):
            return (origin_x + c * cell + cell // 2,
                    origin_y + r * cell + cell // 2)

        color = cfg.COLOR_ARROW_RED if self.is_blocked else cfg.COLOR_ARROW
        pts = [center(r, c) for (r, c) in self.cells]

        line_w = max(4, int(cell * 0.11))
        if len(pts) >= 2:
            pygame.draw.lines(screen, color, False, pts, line_w)

        # 머리: 화살촉(삼각형). 밑변을 머리 셀 중심(=꼬리 끝)에 붙여 자연스럽게.
        cx, cy = center(*self.head)
        dr, dc = self.direction.delta
        fx, fy = dc, dr
        px, py = -fy, fx
        head = cell * 0.30               # 화살촉 길이
        half = cell * 0.18               # 화살촉 폭 절반
        back = cell * 0.09               # 밑변을 살짝 뒤로 빼서 꼬리와 겹치게

        tip    = (cx + fx * (head - back), cy + fy * (head - back))
        base   = (cx - fx * back,          cy - fy * back)
        wing_l = (base[0] + px * half,     base[1] + py * half)
        wing_r = (base[0] - px * half,     base[1] - py * half)
        pygame.draw.polygon(screen, color, [tip, wing_l, wing_r])

    def __repr__(self):
        return f"Arrow(cells={self.cells}, dir={self.direction.name})"
