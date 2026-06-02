"""게임 상태 정의."""
from enum import Enum


class GameState(Enum):
    HOME     = "home"        # 홈(메인) 화면
    PLAYING  = "playing"     # 게임 진행 중
    CLEAR    = "clear"       # 레벨 클리어
    GAMEOVER = "gameover"    # 생명 소진
