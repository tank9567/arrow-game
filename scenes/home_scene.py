"""홈(메인) 화면: 타이틀 + 플레이 버튼."""
import pygame
import config as cfg
from scenes.scene import Scene
from scenes.ui import Button, draw_text


class HomeScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.play_btn = Button("플레이", center=(cfg.WIDTH // 2, 720),
                               size=(320, 90), font_size=40)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_btn.is_clicked(event.pos):
                self.game.go_level_select()

    def draw(self, screen):
        screen.fill(cfg.COLOR_BG)
        draw_text(screen, cfg.TITLE, 64, (cfg.WIDTH // 2, 380))
        self.play_btn.draw(screen)
        draw_text(screen, f"레벨 {self.game.level_index + 1}", 26,
                  (cfg.WIDTH // 2, 780), cfg.COLOR_BTN_TEXT)
