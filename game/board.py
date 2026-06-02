"""보드(격자) 관리 (점유맵 기반).

- 격자 크기(rows, cols)와 화살표 목록을 보유
- 점유맵(occupancy): 어떤 칸을 어떤 화살표가 차지하는지 {(r,c): Arrow}
- 좌표 변환 / 클릭 칸 -> 화살표
- 충돌 판정(머리 직선) / 제거(점유 해제)
"""
import pygame
import config as cfg


class Board:
    def __init__(self, rows, cols, arrows):
        self.rows = rows
        self.cols = cols
        self.arrows = arrows
        # 화살표가 차지한 모든 칸을 펼쳐 매핑
        self.occupancy = {}
        for a in arrows:
            for cell in a.cells:
                self.occupancy[cell] = a

        # 셀 크기는 고정. 보드 전체는 (0,0) 기준의 '월드' 좌표로 다룬다.
        # 화면보다 큰 보드는 PlayScene 의 카메라(줌/팬)로 본다.
        self.cell = cfg.CELL_SIZE
        self.width = cols * self.cell
        self.height = rows * self.cell

    # ---- 좌표 변환 (월드 = 보드 surface 로컬, 0 기준) ----
    def cell_to_pixel(self, row, col):
        return (col * self.cell, row * self.cell)

    def cell_center(self, row, col):
        return (col * self.cell + self.cell // 2,
                row * self.cell + self.cell // 2)

    def pixel_to_cell(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        return int(y // self.cell), int(x // self.cell)

    def arrow_at_pixel(self, x, y):
        """클릭(월드 좌표)에 해당하는 화살표를 넓은 터치 영역으로 찾는다.

        1) 클릭한 칸이 화살표 점유 칸이면 그 화살표.
        2) 아니면 반경(약 0.7칸) 안에서 '가장 가까운' 화살표 칸의 화살표.
           가장 가까운 것 하나만 고르므로 인접 화살표와 겹치지 않는다.
        """
        cell = self.pixel_to_cell(x, y)
        if cell is not None:
            a = self.occupancy.get(cell)
            if a is not None and not a.is_removed:
                return a
        best, best_d = None, self.cell * cfg.TOUCH_RADIUS_CELLS
        for a in self.arrows:
            if a.is_removed:
                continue
            for (r, c) in a.cells:
                cx, cy = self.cell_center(r, c)
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if d <= best_d:
                    best_d, best = d, a
        return best

    # ---- 핵심 로직: 충돌 판정 / 제거 ----
    def can_exit(self, arrow) -> bool:
        """머리의 진행 방향 직선이 보드 밖까지 비어 있으면 True (기차처럼 탈출)."""
        dr, dc = arrow.direction.delta
        r, c = arrow.head
        r, c = r + dr, c + dc                    # 머리 다음 칸부터
        while 0 <= r < self.rows and 0 <= c < self.cols:
            other = self.occupancy.get((r, c))
            if other is not None and other is not arrow and not other.is_removed:
                return False                     # 다른 화살표가 가로막음
            r, c = r + dr, c + dc
        return True                              # 보드 밖 도달 -> 탈출 가능

    def try_remove(self, arrow) -> bool:
        """제거 시도. 성공 True / 막힘 False(빨강 표시, 생명 차감은 호출부)."""
        if self.can_exit(arrow):
            for cell in arrow.cells:
                self.occupancy.pop(cell, None)
            arrow.is_removed = True
            arrow.is_blocked = False
            return True
        arrow.is_blocked = True
        return False

    def count_remaining(self) -> int:
        return sum(1 for a in self.arrows if not a.is_removed)

    def is_cleared(self) -> bool:
        return self.count_remaining() == 0

    # ---- 렌더링 ----
    def draw_dots(self, screen):
        """배경 점 격자: 각 칸 중심에 옅은 점을 찍는다.
        화살표가 빠져나간 자리엔 점만 남아 흔적처럼 보인다."""
        dot_r = max(2, self.cell // 16)
        for r in range(self.rows):
            for c in range(self.cols):
                pygame.draw.circle(screen, cfg.COLOR_DOT,
                                   self.cell_center(r, c), dot_r)

    def draw(self, surface):
        """보드 크기의 surface 에 (0,0) 기준으로 점 격자 + 화살표를 그린다."""
        self.draw_dots(surface)
        for arrow in self.arrows:
            if arrow.is_removed or arrow.hidden:
                continue
            arrow.draw(surface, 0, 0, self.cell)
