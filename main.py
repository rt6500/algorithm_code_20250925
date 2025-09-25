from typing import List, Tuple
from local_driver import Alg3D, Board # ローカル検証用
# from framework import Alg3D, Board # 本番用

class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]], # 盤面情報
        player: int, # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
    ) -> Tuple[int, int]:
        # ここにアルゴリズムを書く
        # --- デバッグ: いったん中身を見てみる ---
        print(f"player={player}, last_move={last_move}")
        print(f"board size: z={len(board)}, y={len(board[0])}, x={len(board[0][0])}")

        # 最小実装：一番上の層(top=z=3)で空(0)のマスを左上から探す
        top = len(board) - 1  # = 3
        for y in range(len(board[0])):          # 0..3
            for x in range(len(board[0][0])):   # 0..3
                if board[top][y][x] == 0:
                    return (x, y)
        # すべて埋まっていた時の保険
        return (0, 0)
