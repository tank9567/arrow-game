"""UI 헬퍼: 폰트 캐시, 텍스트 그리기, 버튼.

한글 표시를 위해 Windows 기본 '맑은 고딕' 폰트를 사용한다.
"""
import pygame
import config as cfg

_font_cache = {}


def get_font(size):
    """크기별 폰트를 캐시해서 반환 (매 프레임 생성 방지)."""
    if size not in _font_cache:
        try:
            _font_cache[size] = pygame.font.Font(cfg.FONT_PATH, size)
        except FileNotFoundError:
            _font_cache[size] = pygame.font.SysFont(None, size)
    return _font_cache[size]


def draw_text(screen, text, size, center, color=None):
    """text 를 center 위치에 가운데 정렬로 그린다."""
    color = color or cfg.COLOR_TEXT
    surf = get_font(size).render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)
    return rect


def draw_water_drop(screen, cx, cy, r, color):
    """물방울(생명) 아이콘 하나 (위 뾰족 + 아래 둥근 모양)."""
    pygame.draw.circle(screen, color, (cx, cy + r // 3), r)
    points = [(cx, cy - r), (cx - int(r * 0.85), cy + int(r * 0.3)),
              (cx + int(r * 0.85), cy + int(r * 0.3))]
    pygame.draw.polygon(screen, color, points)


def draw_lives(screen, lives, max_lives=3):
    """좌상단에 생명(물방울) 표시. 남은 만큼 파랑, 소진은 회색."""
    r, gap, x0, y0 = 14, 40, 36, 44
    for i in range(max_lives):
        color = cfg.COLOR_LIFE if i < lives else cfg.COLOR_LIFE_EMPTY
        draw_water_drop(screen, x0 + i * gap, y0, r, color)


class Button:
    """클릭 가능한 사각형 버튼."""

    def __init__(self, text, center, size=(280, 70), font_size=32,
                 bg=None, fg=None):
        self.text = text
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.font_size = font_size
        self.bg = bg or cfg.COLOR_BTN
        self.fg = fg or cfg.COLOR_BTN_TEXT

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg, self.rect, border_radius=16)
        draw_text(screen, self.text, self.font_size, self.rect.center, self.fg)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
