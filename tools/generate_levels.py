"""레벨 자동 생성기 (풀이 가능 보장).

원리(역방향 구성):
  빈 보드에 화살표를 하나씩 추가하되, 추가하는 화살표의 '머리 직선 경로'가
  이미 놓인 화살표/자기 몸통에 막히지 않도록 배치한다.
  그러면 '추가의 역순'으로 제거하면 항상 can_exit 가 성립 → 반드시 풀린다.

단계가 오를수록 격자 크기, 꼬리 길이(꺾임), 화살표 수를 늘린다.

실행:  python tools/generate_levels.py
결과:  levels/level_01.json ~ level_10.json 생성
"""
import json
import os
import random

DIRS = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
DELTAS = list(DIRS.values())
NAME_OF = {v: k for k, v in DIRS.items()}

LEVELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "levels")

# 단계별 (격자크기, 최대 꼬리 길이, 목표 화살표 수)
PARAMS = [
    (5, 3, 4),    # 1
    (5, 4, 5),    # 2
    (6, 4, 6),    # 3
    (6, 5, 7),    # 4
    (7, 5, 8),    # 5
    (7, 6, 9),    # 6
    (8, 6, 10),   # 7
    (8, 7, 12),   # 8
    (9, 7, 13),   # 9
    (9, 8, 15),   # 10
]


def gen_arrow(rows, cols, occ, max_len, rng, turn_prob):
    """랜덤 워크로 화살표 1개(cells, dir) 생성. 실패 시 None."""
    for _ in range(400):
        length = rng.randint(2, max_len)
        sr, sc = rng.randrange(rows), rng.randrange(cols)
        if (sr, sc) in occ:
            continue
        cells = [(sr, sc)]
        visited = {(sr, sc)}
        dr, dc = rng.choice(DELTAS)
        ok = True
        for _step in range(length - 1):
            if rng.random() < turn_prob:        # 방향 전환(꺾임)
                opts = [d for d in DELTAS if d != (-dr, -dc) and d != (dr, dc)]
                if opts:
                    dr, dc = rng.choice(opts)
            nr, nc = cells[-1][0] + dr, cells[-1][1] + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                ok = False
                break
            if (nr, nc) in visited or (nr, nc) in occ:
                ok = False
                break
            cells.append((nr, nc))
            visited.add((nr, nc))
        if not ok or len(cells) < 2:
            continue
        # 머리 방향 = 마지막 세그먼트 방향
        (pr, pc), (hr, hc) = cells[-2], cells[-1]
        hd = (hr - pr, hc - pc)
        # 머리 직선 경로(머리 다음 ~ 보드 밖)가 기존/자기 몸통에 막히면 안 됨
        r, c = hr + hd[0], hc + hd[1]
        clear = True
        while 0 <= r < rows and 0 <= c < cols:
            if (r, c) in occ or (r, c) in visited:
                clear = False
                break
            r, c = r + hd[0], c + hd[1]
        if not clear:
            continue
        return cells, NAME_OF[hd]
    return None


def gen_level(level_no, size, max_len, n_target, seed):
    rng = random.Random(seed)
    occ = {}
    arrows = []
    turn_prob = 0.35 + 0.04 * level_no      # 단계 오를수록 더 자주 꺾임
    attempts = 0
    while len(arrows) < n_target and attempts < n_target * 30:
        attempts += 1
        res = gen_arrow(size, size, occ, max_len, rng, turn_prob)
        if res is None:
            continue
        cells, dname = res
        for cell in cells:
            occ[cell] = len(arrows)
        arrows.append({"cells": [list(c) for c in cells], "dir": dname})
    return {
        "level": level_no,
        "name": f"{size}×{size} · {len(arrows)}개",
        "rows": size,
        "cols": size,
        "lives": 3,
        "arrows": arrows,
    }


def main():
    for i, (size, max_len, n_target) in enumerate(PARAMS, start=1):
        data = gen_level(i, size, max_len, n_target, seed=1000 + i)
        path = os.path.join(LEVELS_DIR, f"level_{i:02d}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        bent = sum(
            1 for a in data["arrows"]
            if len({(a["cells"][k+1][0]-a["cells"][k][0],
                     a["cells"][k+1][1]-a["cells"][k][1])
                    for k in range(len(a["cells"])-1)}) > 1
        )
        print(f"레벨 {i:2d}: {size}x{size}, 화살표 {len(data['arrows']):2d}개 "
              f"(꺾인 것 {bent}개) -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
