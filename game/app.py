"""Game: 진행 상태와 씬 전환을 총괄하는 컨트롤러.

메인 루프(main.py)는 이벤트/갱신/그리기를 현재 씬에 위임하고,
씬들은 self.game(=Game)의 메서드를 호출해 화면을 전환한다.
"""
from game.level import build_board, get_level, level_count
from game.progress import load_progress, save_progress
from game.state import GameState
from scenes.home_scene import HomeScene
from scenes.level_select_scene import LevelSelectScene
from scenes.play_scene import PlayScene
from scenes.result_scene import ResultScene


class Game:
    def __init__(self):
        # 저장된 진행을 불러와 이어서 시작 (레벨 범위 밖이면 보정)
        idx = load_progress()
        self.level_index = idx if 0 <= idx < level_count() else 0
        self.scene = HomeScene(self)

    # ---- 씬 전환 ----
    def change_scene(self, scene):
        self.scene = scene

    def go_home(self):
        self.change_scene(HomeScene(self))

    def go_level_select(self):
        self.change_scene(LevelSelectScene(self))

    def start_level(self, index):
        """index 레벨을 로드해 플레이 화면으로 전환."""
        self.level_index = index
        data = get_level(index)
        board = build_board(data)
        self.change_scene(
            PlayScene(self, board, lives=data.get("lives", 3),
                      level_name=f"레벨 {index + 1}")
        )

    def retry_level(self):
        self.start_level(self.level_index)

    def go_next_level(self):
        nxt = self.level_index + 1
        if nxt < level_count():
            self.start_level(nxt)
        else:
            self.go_home()           # 마지막 레벨이면 홈으로

    # ---- 플레이 결과 콜백 (PlayScene 이 호출) ----
    def on_level_clear(self):
        # 다음 레벨을 해금 상태로 저장 (마지막 레벨이면 현재 유지)
        next_idx = min(self.level_index + 1, level_count() - 1)
        save_progress(next_idx)
        self.change_scene(
            ResultScene(self, GameState.CLEAR, level_number=self.level_index + 1)
        )

    def on_game_over(self):
        self.change_scene(
            ResultScene(self, GameState.GAMEOVER, level_number=self.level_index + 1)
        )

    # ---- 루프 위임 ----
    def handle_event(self, event):
        self.scene.handle_event(event)

    def update(self, dt):
        self.scene.update(dt)

    def draw(self, screen):
        self.scene.draw(screen)
