"""Arrows GO! - 진입점.

표준 게임 루프:
    입력 처리(events) -> 상태 갱신(update) -> 화면 그리기(draw)
실제 화면별 동작은 game.app.Game 이 현재 씬에 위임한다.
"""
import pygame
import config as cfg
from game.app import Game


def main():
    pygame.init()
    pygame.display.set_caption(cfg.TITLE)
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    clock = pygame.time.Clock()

    game = Game()

    running = True
    while running:
        dt = clock.tick(cfg.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                game.handle_event(event)

        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
