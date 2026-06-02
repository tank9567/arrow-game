"""게임 플레이 화면 (줌/팬 카메라 포함).

- 보드를 자기 크기의 surface(월드)에 그린 뒤, 카메라(scale=줌, pan=이동)를 적용해 화면에 표시.
  큰 격자는 화면보다 커도 휠로 확대/축소, 드래그로 이동해서 본다.
- 입력 구분:
    · 짧은 클릭(탭, 이동 없음)  → 화살표 빼내기(성공=기차 슬라이드 / 막힘=부딪힘)
    · 길게 누르기(이동 없음)    → 머리 진행 경로 미리보기
    · 드래그(이동)             → 화면 팬(이동)
    · 마우스 휠                → 줌(마우스 위치 기준)
"""
import pygame
import config as cfg
from scenes.scene import Scene
from scenes.ui import draw_lives, draw_text

MOVE_THRESH = 8          # 이 픽셀 이상 움직이면 '드래그(팬)'로 간주
ZOOM_STEP = 1.15
MAX_SCALE = 2.5


# ---- 폴리라인(경로) 유틸 ----
def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _point_along(pts, d):
    if d <= 0:
        return pts[0]
    for i in range(len(pts) - 1):
        seg = _dist(pts[i], pts[i + 1])
        if seg == 0:
            continue
        if d <= seg:
            return _lerp(pts[i], pts[i + 1], d / seg)
        d -= seg
    return pts[-1]


def _subpath(pts, start, end):
    result = [_point_along(pts, start)]
    acc = 0.0
    for i in range(len(pts) - 1):
        acc_next = acc + _dist(pts[i], pts[i + 1])
        if start < acc_next < end:
            result.append(pts[i + 1])
        acc = acc_next
    result.append(_point_along(pts, end))
    return result


class PlayScene(Scene):
    def __init__(self, game, board, lives, level_name=""):
        super().__init__(game)
        self.board = board
        self.lives = lives
        self.level_name = level_name

        # 입력 상태
        self.press_arrow = None
        self.down_pos = (0, 0)
        self.down_time = 0
        self.last_pos = (0, 0)
        self.moved = False
        self.preview_arrow = None
        self.anim = None

        self._reset_camera()

    # ---- 카메라 ----
    def _reset_camera(self):
        vx, vy, vw, vh = self._viewport()
        fit = min(vw / self.board.width, vh / self.board.height, 1.0)
        self.min_scale = fit
        self.scale = fit
        sw, sh = self.board.width * fit, self.board.height * fit
        self.pan_x = vx + (vw - sw) / 2
        self.pan_y = vy + (vh - sh) / 2

    def _viewport(self):
        vx = cfg.BOARD_SIDE_MARGIN
        vy = cfg.BOARD_TOP
        vw = cfg.WIDTH - 2 * cfg.BOARD_SIDE_MARGIN
        vh = cfg.HEIGHT - cfg.BOARD_TOP - cfg.BOARD_BOTTOM_MARGIN
        return vx, vy, vw, vh

    def _to_world(self, sx, sy):
        return ((sx - self.pan_x) / self.scale, (sy - self.pan_y) / self.scale)

    def _zoom_at(self, sx, sy, factor):
        wx, wy = self._to_world(sx, sy)
        self.scale = max(self.min_scale, min(MAX_SCALE, self.scale * factor))
        self.pan_x = sx - wx * self.scale
        self.pan_y = sy - wy * self.scale

    # ---- 입력 ----
    def handle_event(self, event):
        if self.anim is not None:
            return                              # 애니메이션 중 입력 잠금
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            self._zoom_at(mx, my, ZOOM_STEP if event.y > 0 else 1 / ZOOM_STEP)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.down_pos = self.last_pos = event.pos
            self.down_time = pygame.time.get_ticks()
            self.moved = False
            self.press_arrow = self.board.arrow_at_pixel(*self._to_world(*event.pos))
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self._on_drag(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._on_release(event.pos)

    def _on_drag(self, pos):
        if not self.moved:
            if _dist(self.down_pos, pos) > MOVE_THRESH:
                self.moved = True
                self.last_pos = pos
        else:
            self.pan_x += pos[0] - self.last_pos[0]
            self.pan_y += pos[1] - self.last_pos[1]
            self.last_pos = pos
            self.preview_arrow = None

    def _on_release(self, pos):
        if (not self.moved and self.press_arrow is not None
                and pygame.time.get_ticks() - self.down_time < cfg.LONG_PRESS_MS):
            self._tap(self.press_arrow)
        self.press_arrow = None
        self.preview_arrow = None
        self.moved = False

    def _tap(self, arrow):
        if self.board.can_exit(arrow):
            self._start_exit_anim(arrow)
            self.board.try_remove(arrow)
        else:
            self._start_blocked_anim(arrow)

    # ---- 애니메이션 시작 ----
    def _body_path(self, arrow):
        centers = [self.board.cell_center(r, c) for (r, c) in arrow.cells]
        body = sum(_dist(centers[i], centers[i + 1]) for i in range(len(centers) - 1))
        return centers, body

    def _start_exit_anim(self, arrow):
        b = self.board
        centers, body = self._body_path(arrow)
        dr, dc = arrow.direction.delta
        hx, hy = b.cell_center(*arrow.head)
        ext = (b.rows + b.cols + 2) * b.cell
        path = centers + [(hx + dc * ext, hy + dr * ext)]
        arrow.hidden = True
        self.anim = {"mode": "exit", "arrow": arrow, "path": path,
                     "body": body, "total": body + ext, "d": 0.0}

    def _start_blocked_anim(self, arrow):
        b = self.board
        centers, body = self._body_path(arrow)
        dr, dc = arrow.direction.delta
        r, c = arrow.head
        r, c = r + dr, c + dc
        empty = 0
        while 0 <= r < b.rows and 0 <= c < b.cols:
            o = b.occupancy.get((r, c))
            if o is not None and o is not arrow and not o.is_removed:
                break
            empty += 1
            r, c = r + dr, c + dc
        # 장애물 직전까지(빈 칸 수만큼) 전진 + 살짝 부딪히는 여유
        adv = empty * b.cell + b.cell * 0.45
        hx, hy = b.cell_center(*arrow.head)
        path = centers + [(hx + dc * adv, hy + dr * adv)]
        arrow.hidden = True
        self.anim = {"mode": "blocked", "phase": "forward", "arrow": arrow,
                     "path": path, "body": body, "total": body + adv,
                     "max_d": adv, "d": 0.0}

    # ---- 갱신 ----
    def update(self, dt):
        if self.anim is not None:
            self._update_anim(dt)
            return
        if self.press_arrow is not None and not self.moved:
            held = pygame.time.get_ticks() - self.down_time
            self.preview_arrow = self.press_arrow if held >= cfg.LONG_PRESS_MS else None
        else:
            self.preview_arrow = None

    def _update_anim(self, dt):
        a = self.anim
        step = cfg.ANIM_SPEED_PX_PER_MS * dt
        if a["mode"] == "exit":
            a["d"] += step
            if a["d"] >= a["total"]:
                self.anim = None
                if self.board.is_cleared():
                    self.game.on_level_clear()
        else:
            if a["phase"] == "forward":
                a["d"] += step
                if a["d"] >= a["max_d"]:
                    a["d"] = a["max_d"]
                    a["arrow"].is_blocked = True   # 부딪히는 순간 빨강
                    a["phase"] = "hold"
                    a["hold"] = 0.0
            elif a["phase"] == "hold":
                a["hold"] += dt                    # 부딪힌 채 잠깐 멈춤
                if a["hold"] >= 120:
                    a["phase"] = "back"
            else:
                a["d"] -= step
                if a["d"] <= 0:
                    a["arrow"].hidden = False       # 제자리 복귀
                    self.anim = None
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game.on_game_over()

    # ---- 렌더링 ----
    def draw(self, screen):
        screen.fill(cfg.COLOR_BG)
        # 1) 보드를 월드 surface 에 그린다
        world = pygame.Surface((self.board.width, self.board.height))
        world.fill(cfg.COLOR_BG)
        self.board.draw(world)
        if self.anim is not None:
            self._draw_anim(world)
        else:
            self._draw_preview(world)
        # 2) 카메라(줌/팬) 적용해 화면에 blit
        sw = max(1, int(self.board.width * self.scale))
        sh = max(1, int(self.board.height * self.scale))
        scaled = pygame.transform.smoothscale(world, (sw, sh))
        screen.blit(scaled, (int(self.pan_x), int(self.pan_y)))
        # 3) 상단 UI (카메라 영향 없음)
        draw_lives(screen, self.lives)
        draw_text(screen, self.level_name, 30, (cfg.WIDTH // 2, 44))

    def _draw_anim(self, surf):
        a = self.anim
        path, body, d, total = a["path"], a["body"], a["d"], a["total"]
        tail_d = d
        head_d = min(d + body, total)
        if tail_d >= total:
            return
        cell = self.board.cell
        color = cfg.COLOR_ARROW_RED if a["arrow"].is_blocked else cfg.COLOR_ARROW
        pts = _subpath(path, tail_d, head_d)
        line_w = max(4, int(cell * 0.11))
        if len(pts) >= 2:
            pygame.draw.lines(surf, color, False, pts, line_w)
        hx, hy = _point_along(path, head_d)
        dr, dc = a["arrow"].direction.delta
        fx, fy = dc, dr
        px, py = -fy, fx
        head, half, back = cell * 0.30, cell * 0.18, cell * 0.09
        tip = (hx + fx * (head - back), hy + fy * (head - back))
        base = (hx - fx * back, hy - fy * back)
        wing_l = (base[0] + px * half, base[1] + py * half)
        wing_r = (base[0] - px * half, base[1] - py * half)
        pygame.draw.polygon(surf, color, [tip, wing_l, wing_r])

    def _draw_preview(self, surf):
        a = self.preview_arrow
        if a is None or a.is_removed:
            return
        start = self.board.cell_center(*a.head)
        dr, dc = a.direction.delta
        big = self.board.width + self.board.height
        end = (start[0] + dc * big, start[1] + dr * big)
        color = cfg.COLOR_ARROW_RED if a.is_blocked else cfg.COLOR_PREVIEW
        pygame.draw.line(surf, color, start, end, max(4, int(self.board.cell * 0.09)))
