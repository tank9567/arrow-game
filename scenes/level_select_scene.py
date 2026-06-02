"""레벨 선택 화면: 레벨 번호 버튼을 격자로 보여주고 고른 레벨을 시작한다."""
import pygame
import config as cfg
from scenes.scene import Scene
from scenes.ui import Button, draw_text
from game.level import level_count, get_level


class LevelSelectScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []          # (index, Button, name)
        cols = 3
        bw, bh, gap_x, gap_y = 130, 100, 28, 46
        total_w = cols * bw + (cols - 1) * gap_x
        x0 = (cfg.WIDTH - total_w) // 2 + bw // 2
        y0 = 235
        last_row = 0
        for i in range(level_count()):
            r, c = divmod(i, cols)
            last_row = r
            cx = x0 + c * (bw + gap_x)
            cy = y0 + r * (bh + gap_y)
            btn = Button(str(i + 1), center=(cx, cy), size=(bw, bh), font_size=46)
            name = get_level(i).get("name", "")
            self.buttons.append((i, btn, name))

        # 홈 버튼: 마지막 버튼 행보다 충분히 아래, 화면 하단 중앙에 분리 배치
        home_y = y0 + last_row * (bh + gap_y) + bh // 2 + 70
        home_y = min(home_y, cfg.HEIGHT - 60)
        self.back_btn = Button("홈", center=(cfg.WIDTH // 2, home_y),
                               size=(220, 66), bg=(214, 196, 170))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn, _ in self.buttons:
                if btn.is_clicked(event.pos):
                    self.game.start_level(i)
                    return
            if self.back_btn.is_clicked(event.pos):
                self.game.go_home()

    def draw(self, screen):
        screen.fill(cfg.COLOR_BG)
        draw_text(screen, "레벨 선택", 50, (cfg.WIDTH // 2, 140))
        for i, btn, name in self.buttons:
            btn.draw(screen)
            # 버튼 아래 레벨 이름
            draw_text(screen, name, 20,
                      (btn.rect.centerx, btn.rect.bottom + 18))
        self.back_btn.draw(screen)
