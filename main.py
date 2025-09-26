from typing import List, Tuple
from local_driver import Alg3D, Board # ローカル検証用
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
def simulate(board: Board, x:int, y:int, who:int):
    z = next_z(board, x, y)
    if z is None:
        return None
    # ★ 盤面の完全な可変コピー（必ず list にする）
    b2 = [[[board[zz][yy][xx] for xx in range(4)] for yy in range(4)] for zz in range(4)]
    b2[z][y][x] = who
    return b2

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

            # 候補
            candidates = [(x,y) for y in range(4) for x in range(4) if next_z(board,x,y) is not None]
            if not candidates:
                # ★ 盤が埋まっているなど。とにかく合法っぽい保険を返す
                return (0,0)

            # 3) “支え”を避ける
            safe = []
            for (x,y) in candidates:
                b2 = simulate(board,x,y,me)
                if b2 is not None and not threats(b2, opp):
                    safe.append((x,y))
            if not safe:
                safe = candidates  # やむなし

            # 4) 評価 + 位置ボーナス
            def move_score(xy):
                x,y = xy
                b2 = simulate(board,x,y,me)
                return (evaluate(b2, me) if b2 is not None else -10**9) + pos_bonus(x,y)

            return max(safe, key=move_score)

        except Exception:
            # ★ どんな例外でも“合法手”を返す最終保険（強制配置を防ぐ）
            for y in range(4):
                for x in range(4):
                    if next_z(board,x,y) is not None:
                        return (x,y)
            return (0,0)
