"""결과 화면: 클리어(CLEAR) 또는 게임오버(GAMEOVER) 공용.

mode 에 따라 메시지/버튼을 다르게 보여준다.
"""
import pygame
import config as cfg
from game.state import GameState
from scenes.scene import Scene
from scenes.ui import Button, draw_text


class ResultScene(Scene):
    def __init__(self, game, mode: GameState, level_number: int):
        super().__init__(game)
        self.mode = mode
        self.level_number = level_number

        cx = cfg.WIDTH // 2
        if mode == GameState.CLEAR:
            self.title = "잘했어!"
            self.subtitle = f"{level_number}단계 완료!"
            self.primary = Button("다음 레벨", center=(cx, 640), size=(320, 84))
        else:
            self.title = "게임 오버"
            self.subtitle = "생명을 모두 사용했어요"
            self.primary = Button("다시하기", center=(cx, 640), size=(320, 84))
        self.home_btn = Button("홈", center=(cx, 750), size=(320, 84),
                               bg=(214, 196, 170))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.primary.is_clicked(event.pos):
                if self.mode == GameState.CLEAR:
                    self.game.go_next_level()
                else:
                    self.game.retry_level()
            elif self.home_btn.is_clicked(event.pos):
                self.game.go_home()

    def draw(self, screen):
        screen.fill(cfg.COLOR_BG)
        draw_text(screen, self.title, 60, (cfg.WIDTH // 2, 380))
        draw_text(screen, self.subtitle, 30, (cfg.WIDTH // 2, 470))
        self.primary.draw(screen)
        self.home_btn.draw(screen)
