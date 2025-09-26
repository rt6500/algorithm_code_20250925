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

# === main.py (置き換え用) ===
from typing import List, Tuple

# 両環境対応: framework が無ければ local_driver の抽象だけ拝借
try:
    from framework import Alg3D, Board  # 本番
except Exception:
    from local_driver import Alg3D, Board  # ローカル

Idx = range(4)

# --- 勝ちライン生成 ---
def gen_lines():
    L = []
    for z in Idx:
        for y in Idx: L.append([(z,y,x) for x in Idx])  # x方向
    for z in Idx:
        for x in Idx: L.append([(z,y,x) for y in Idx])  # y方向
    for y in Idx:
        for x in Idx: L.append([(z,y,x) for z in Idx])  # z方向
    for z in Idx:
        L.append([(z,i,i) for i in Idx])
        L.append([(z,i,3-i) for i in Idx])
    for x in Idx:
        L.append([(i,i,x) for i in Idx])
        L.append([(i,3-i,x) for i in Idx])
    for y in Idx:
        L.append([(i,y,i) for i in Idx])
        L.append([(i,y,3-i) for i in Idx])
    L.append([(i,i,i) for i in Idx])
    L.append([(i,i,3-i) for i in Idx])
    L.append([(i,3-i,i) for i in Idx])
    L.append([(i,3-i,3-i) for i in Idx])
    return L

LINES = gen_lines()
CENTERS = {(1,1),(2,1),(1,2),(2,2)}
CORNERS = {(0,0),(0,3),(3,0),(3,3)}

def to_mutable(bd: Board) -> list:
    # tuple でも確実に書き換え可能へ
    return [[[bd[z][y][x] for x in Idx] for y in Idx] for z in Idx]

def next_z(board: Board, x:int, y:int):
    for z in Idx:
        if board[z][y][x] == 0:
            return z
    return None

def simulate(board: Board, x:int, y:int, who:int):
    z = next_z(board, x, y)
    if z is None: return None
    b2 = to_mutable(board)
    b2[z][y][x] = who
    return b2

def winner(board: Board) -> int:
    for line in LINES:
        vs = [board[z][y][x] for z,y,x in line]
        if vs[0] != 0 and all(v==vs[0] for v in vs):
            return vs[0]
    return 0

def threats(board: Board, who:int):
    T = set()
    for line in LINES:
        cells = [(z,y,x) for z,y,x in line]
        vs = [board[z][y][x] for z,y,x in cells]
        if vs.count(who) == 3 and vs.count(0) == 1:
            z,y,x = cells[vs.index(0)]
            if next_z(board, x, y) == z:  # 実際に置ける高さであること
                T.add((x,y))
    return T

def pos_bonus(x:int, y:int):
    if (x,y) in CENTERS: return 3
    if (x,y) in CORNERS: return 2
    return 0

def evaluate(board: Board, me:int):
    opp = 2 if me == 1 else 1
    score = 0
    for line in LINES:
        vs = [board[z][y][x] for z,y,x in line]
        mc, oc = vs.count(me), vs.count(opp)
        if mc and oc:  # 混在は無効
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

def infer_player(board: Board) -> int:
    # 盤面から手番を推定（1の数==2の数なら1、そうでなければ2）
    flat = [board[z][y][x] for z in Idx for y in Idx for x in Idx]
    c1, c2 = flat.count(1), flat.count(2)
    return 1 if c1 == c2 else 2

class MyAI(Alg3D):
    # 両対応: (board) も (board, player, last_move) も受け付ける
    def get_move(self, *args) -> Tuple[int,int]:
        try:
            if len(args) == 1:
                board = args[0]
                player = infer_player(board)
                last_move = None  # 本戦では未使用
            elif len(args) == 3:
                board, player, last_move = args
            else:
                # 想定外でも安全に処理
                board, player, last_move = args[0], infer_player(args[0]), None

            me, opp = player, (2 if player == 1 else 1)

            # 1) 即勝ち
            for y in Idx:
                for x in Idx:
                    if next_z(board,x,y) is None: continue
                    b2 = simulate(board,x,y,me)
                    if b2 is not None and winner(b2) == me:
                        return (x,y)

            # 2) 即ブロック
            opp_th = threats(board, opp)
            if opp_th:
                return max(opp_th, key=lambda xy: pos_bonus(*xy))

            # 候補
            candidates = [(x,y) for y in Idx for x in Idx if next_z(board,x,y) is not None]
            if not candidates:
                return (0,0)  # 盤詰まり保険

            # 3) 置いた直後に相手の即勝ちが生じない手
            safe = []
            for (x,y) in candidates:
                b2 = simulate(board,x,y,me)
                if b2 is not None and not threats(b2, opp):
                    safe.append((x,y))
            if not safe:
                safe = candidates

            # 4) 評価 + 位置ボーナス
            def move_score(xy):
                x,y = xy
                b2 = simulate(board,x,y,me)
                base = evaluate(b2, me) if b2 is not None else -10**9
                return base + pos_bonus(x,y)

            bx, by = max(safe, key=move_score)
            return (int(bx), int(by))

        except Exception:
            # 例外でも必ず合法手を返す
            for y in Idx:
                for x in Idx:
                    if next_z(board,x,y) is not None:
                        return (x,y)
            return (0,0)
