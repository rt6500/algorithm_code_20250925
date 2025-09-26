from typing import List, Tuple
# from local_driver import Alg3D, Board # ローカル検証用
from framework import Alg3D, Board # 本番用

class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]], # 盤面情報
        player: int, # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
    ) -> Tuple[int, int]:
        # ここにアルゴリズムを書く
        # センター優先で、満杯でない列を選ぶだけの簡易ロジック
        order = [
            (1,1),(2,1),(1,2),(2,2),
            (0,1),(3,1),(1,0),(1,3),
            (0,2),(3,2),(2,0),(2,3),
            (0,0),(3,0),(0,3),(3,3)
        ]
        for (x,y) in order:
            # 上から z=0..3 を見て 0(空) があれば置ける
            for z in range(4):
                if board[z][y][x] == 0:
                    print(f"[DBG] choose {(x,y)} at z={z}")
                    return (x, y)

        # すべて埋まっていれば保険で (0,0)
        print("[DBG] board full → fallback (0,0)")
        return (0, 0)
# class MyAI(Alg3D):
#     def get_move(self, board: List[List[List[int]]], player: int, last_move: Tuple[int,int,int]) -> Tuple[int,int]:
#         order = [(1,1),(2,1),(1,2),(2,2),(0,1),(3,1),(1,0),(1,3),
#                  (0,2),(3,2),(2,0),(2,3),(0,0),(3,0),(0,3),(3,3)]
#         for (x,y) in order:
#             # 列(x,y)が満杯でないなら置ける
#             for z in range(4):
#                 if board[z][y][x] == 0:
#                     print(f"[DBG] choose {(x,y)} at z={z}")
#                     return (x, y)
#         return (0, 0)  # 盤全埋まりの保険


# class MyAI(Alg3D):
#     def get_move(
#         self,
#         board: List[List[List[int]]],
#         player: int,
#         last_move: Tuple[int, int, int]
#     ) -> Tuple[int, int]:
#         print("[DBG] enter get_move", "player=", player, " last_move=", last_move)
#         order = [(1,1),(2,1),(1,2),(2,2),(0,1),(3,1),(1,0),(1,3),
#                  (0,2),(3,2),(2,0),(2,3),(0,0),(3,0),(0,3),(3,3)]
#         for (x,y) in order:
#             for z in range(4):
#                 if board[z][y][x] == 0:
#                     print(f"[DBG] choose {(x,y)} at z={z}")
#                     return (x, y)
#         print("[DBG] board full → fallback (0,0)")
#         return (0, 0)
    

