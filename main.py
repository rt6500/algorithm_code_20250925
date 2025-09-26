from typing import List, Tuple
# from local_driver import Alg3D, Board # ローカル検証用
from framework import Alg3D, Board # 本番用

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
from typing import List, Tuple
from local_driver import Alg3D, Board

# --- 勝ち筋生成（4x4x4 の全ライン） ---
def gen_lines():
    L = []
    idx = range(4)
    for z in idx:
        for y in idx: L.append([(z,y,x) for x in idx])  # x方向
    for z in idx:
        for x in idx: L.append([(z,y,x) for y in idx])  # y方向
    for y in idx:
        for x in idx: L.append([(z,y,x) for z in idx])  # z方向
    for z in idx:  # 各zの2D斜め
        L.append([(z,i,i) for i in idx])
        L.append([(z,i,3-i) for i in idx])
    for x in idx:  # y–z 斜め
        L.append([(i,i,x) for i in idx])
        L.append([(i,3-i,x) for i in idx])
    for y in idx:  # x–z 斜め
        L.append([(i,y,i) for i in idx])
        L.append([(i,y,3-i) for i in idx])
    # 3D 主対角線
    L.append([(i,i,i) for i in idx])
    L.append([(i,i,3-i) for i in idx])
    L.append([(i,3-i,i) for i in idx])
    L.append([(i,3-i,3-i) for i in idx])
    return L

LINES = gen_lines()
CENTERS = {(1,1),(2,1),(1,2),(2,2)}
CORNERS = {(0,0),(0,3),(3,0),(3,3)}

def next_z(board: Board, x:int, y:int):
    for z in range(4):
        if board[z][y][x] == 0:
            return z
    return None

def winner(board: Board) -> int:
    for line in LINES:
        vals = [board[z][y][x] for (z,y,x) in line]
        if vals[0] != 0 and all(v == vals[0] for v in vals):
            return vals[0]
    return 0

def threats(board: Board, who:int):
    T = set()
    for line in LINES:
        cells = [(z,y,x) for (z,y,x) in line]
        vals  = [board[z][y][x] for (z,y,x) in cells]
        if vals.count(who) == 3 and vals.count(0) == 1:
            z,y,x = cells[vals.index(0)]
            if next_z(board, x, y) == z:  # 実際に置ける高さ
                T.add((x,y))
    return T

def simulate(board: Board, x:int, y:int, who:int):
    z = next_z(board, x, y)
    if z is None:
        return None
    # ★ 常に“可変な list”に展開してから代入（tuple対策）
    b2 = [[[board[zz][yy][xx] for xx in range(4)] for yy in range(4)] for zz in range(4)]
    b2[z][y][x] = who
    return b2

def pos_bonus(x:int, y:int):
    if (x,y) in CENTERS: return 3
    if (x,y) in CORNERS: return 2
    return 0

def evaluate(board: Board, me:int):
    opp = 2 if me == 1 else 1
    score = 0
    for line in LINES:
        vals = [board[z][y][x] for (z,y,x) in line]
        mc, oc = vals.count(me), vals.count(opp)
        if mc and oc:  # 混在ラインは無効
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

class MyAI(Alg3D):
    def get_move(self, board: Board, player: int, last_move: Tuple[int,int,int]) -> Tuple[int,int]:
        try:
            me, opp = player, (2 if player == 1 else 1)

            # 1) 即勝ち
            for y in range(4):
                for x in range(4):
                    if next_z(board,x,y) is None: 
                        continue
                    b2 = simulate(board,x,y,me)
                    if b2 is not None and winner(b2) == me:
                        return (x,y)

            # 2) 即ブロック
            opp_th = threats(board, opp)
            if opp_th:
                return max(opp_th, key=lambda xy: pos_bonus(*xy))

            # 候補列挙
            candidates = [(x,y) for y in range(4) for x in range(4) if next_z(board,x,y) is not None]
            if not candidates:
                return (0,0)  # 盤詰まり保険

            # 3) 支え回避（直後に相手の即勝ちが生じない手）
            safe = []
            for (x,y) in candidates:
                b2 = simulate(board,x,y,me)
                if b2 is not None and not threats(b2, opp):
                    safe.append((x,y))
            if not safe:
                safe = candidates  # 全部危険なら妥協

            # 4) スコア + 位置ボーナス
            def move_score(xy):
                x,y = xy
                b2 = simulate(board,x,y,me)
                base = evaluate(b2, me) if b2 is not None else -10**9
                return base + pos_bonus(x,y)

            best = max(safe, key=move_score)
            # ★ 戻り値の型・範囲保証（最終保険）
            bx, by = int(best[0]), int(best[1])
            return (min(max(bx,0),3), min(max(by,0),3))

        except Exception:
            # 例外でも必ず“置ける手”を返す
            for y in range(4):
                for x in range(4):
                    if next_z(board,x,y) is not None:
                        return (x,y)
            return (0,0)
