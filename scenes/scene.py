"""모든 씬의 기반 클래스.

각 씬은 표준 게임 루프 3단계를 구현한다:
    handle_event(event) -> update(dt) -> draw(screen)
씬 전환은 self.game.change_scene(...) 으로 한다.
"""


class Scene:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass
