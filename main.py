# from typing import List, Tuple
# from local_driver import Alg3D, Board # ローカル検証用
# from framework import Alg3D, Board # 本番用

# class MyAI(Alg3D):
#     def get_move(
#         self,
#         board: List[List[List[int]]], # 盤面情報
#         player: int, # 先手(黒):1 後手(白):2
#         last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
#     ) -> Tuple[int, int]:
#         # ここにアルゴリズムを書く
#         # --- デバッグ: いったん中身を見てみる ---
#         print(f"player={player}, last_move={last_move}")
#         print(f"board size: z={len(board)}, y={len(board[0])}, x={len(board[0][0])}")

#         # 最小実装：一番上の層(top=z=3)で空(0)のマスを左上から探す
#         top = len(board) - 1  # = 3
#         for y in range(len(board[0])):          # 0..3
#             for x in range(len(board[0][0])):   # 0..3
#                 if board[top][y][x] == 0:
#                     return (x, y)
#         # すべて埋まっていた時の保険
#         return (0, 0)

# === main.py (両対応版) ===
from typing import List, Tuple

Board = List[List[List[int]]]
Idx = range(4)

# --- 勝ちライン生成 ---
def _gen_lines():
    L = []
    for z in Idx:
        for y in Idx: L.append([(z,y,x) for x in Idx])  # x方向
    for z in Idx:
        for x in Idx: L.append([(z,y,x) for y in Idx])  # y方向
    for y in Idx:
        for x in Idx: L.append([(z,y,x) for z in Idx])  # z方向
    for z in Idx:  # 各層の2D斜め
        L.append([(z,i,i) for i in Idx])
        L.append([(z,i,3-i) for i in Idx])
    for x in Idx:  # y–z 斜め
        L.append([(i,i,x) for i in Idx])
        L.append([(i,3-i,x) for i in Idx])
    for y in Idx:  # x–z 斜め
        L.append([(i,y,i) for i in Idx])
        L.append([(i,y,3-i) for i in Idx])
    # 3D 主対角線
    L.append([(i,i,i) for i in Idx])
    L.append([(i,i,3-i) for i in Idx])
    L.append([(i,3-i,i) for i in Idx])
    L.append([(i,3-i,3-i) for i in Idx])
    return L

_LINES = _gen_lines()
_CENTERS = {(1,1),(2,1),(1,2),(2,2)}
_CORNERS = {(0,0),(0,3),(3,0),(3,3)}

def _to_mutable(bd: Board) -> list:
    return [[[bd[z][y][x] for x in Idx] for y in Idx] for z in Idx]

def _next_z(board: Board, x:int, y:int):
    for z in Idx:
        if board[z][y][x] == 0:
            return z
    return None  # 満杯列

def _simulate(board: Board, x:int, y:int, who:int):
    z = _next_z(board, x, y)
    if z is None: return None
    b2 = _to_mutable(board)
    b2[z][y][x] = who
    return b2

def _winner(board: Board) -> int:
    for line in _LINES:
        vs = [board[z][y][x] for (z,y,x) in line]
        if vs[0] != 0 and vs.count(vs[0]) == 4:
            return vs[0]
    return 0

def _threats(board: Board, who:int):
    T = set()
    for line in _LINES:
        cells = [(z,y,x) for (z,y,x) in line]
        vs = [board[z][y][x] for (z,y,x) in cells]
        if vs.count(who) == 3 and vs.count(0) == 1:
            zz,yy,xx = cells[vs.index(0)]
            if _next_z(board, xx, yy) == zz:  # 実際に置ける高さ
                T.add((xx,yy))
    return T

def _pos_bonus(x:int, y:int):
    if (x,y) in _CENTERS: return 3
    if (x,y) in _CORNERS: return 2
    return 0

def _evaluate(board: Board, me:int):
    opp = 2 if me == 1 else 1
    score = 0
    for line in _LINES:
        vs = [board[z][y][x] for (z,y,x) in line]
        mc, oc = vs.count(me), vs.count(opp)
        if mc and oc:
            continue
        if oc == 0:
            if mc == 3: score += 60
            elif mc == 2: score += 12
            elif mc == 1: score += 3
        if mc == 0:
            if oc == 3: score -= 80
            elif oc == 2: score -= 15
            elif oc == 1: score -= 4
    return score

def _infer_player(board: Board) -> int:
    flat = [board[z][y][x] for z in Idx for y in Idx for x in Idx]
    c1, c2 = flat.count(1), flat.count(2)
    return 1 if c1 == c2 else 2

def _first_legal(board: Board) -> Tuple[int,int]:
    for y in Idx:
        for x in Idx:
            if _next_z(board, x, y) is not None:
                return (x, y)
    return (0, 0)

def _choose_move(board: Board, me: int) -> Tuple[int,int]:
    opp = 2 if me == 1 else 1
    # 1) 即勝ち
    for y in Idx:
        for x in Idx:
            if _next_z(board,x,y) is None: continue
            b2 = _simulate(board,x,y,me)
            if b2 is not None and _winner(b2) == me:
                return (x,y)
    # 2) 即ブロック
    opp_th = _threats(board, opp)
    if opp_th:
        return max(opp_th, key=lambda xy: _pos_bonus(*xy))
    # 候補
    candidates = [(x,y) for y in Idx for x in Idx if _next_z(board,x,y) is not None]
    if not candidates:
        return (0,0)
    # 3) 直後に相手の即勝ちを生まない手
    safe = []
    for (x,y) in candidates:
        b2 = _simulate(board,x,y,me)
        if b2 is not None and not _threats(b2, opp):
            safe.append((x,y))
    if not safe:
        safe = candidates
    # 4) 評価 + 位置ボーナス
    best = max(safe, key=lambda xy: (_evaluate(_simulate(board,xy[0],xy[1],me), me) + _pos_bonus(*xy)))
    bx, by = int(best[0]), int(best[1])
    return (min(max(bx,0),3), min(max(by,0),3))

# === 提出用エクスポート（本番はこれだけ呼ばれる想定） ===
def get_move(board: Board) -> Tuple[int,int]:
    try:
        me = _infer_player(board)
        x, y = _choose_move(board, me)
        # 念のため合法保証
        return (x, y) if _next_z(board, x, y) is not None else _first_legal(board)
    except Exception:
        return _first_legal(board)

# === ローカル検証用API（local_driver.py が呼ぶ） ===
class MyAI:
    def get_move(self, board: Board, player: int, last_move: Tuple[int,int,int]) -> Tuple[int,int]:
        try:
            x, y = _choose_move(board, player)
            return (x, y) if _next_z(board, x, y) is not None else _first_legal(board)
        except Exception:
            return _first_legal(board)
