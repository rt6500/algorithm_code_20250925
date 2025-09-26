from typing import List, Tuple, Optional
# from local_driver import Alg3D, Board # ローカル検証用
from framework import Alg3D, Board # 本番用

# class MyAI(Alg3D):
#     def get_move(
#         self,
#         board: List[List[List[int]]], # 盤面情報
#         player: int, # 先手(黒):1 後手(白):2
#         last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
#     ) -> Tuple[int, int]:

class MyAI(Alg3D):
    def get_move(self, board: Board, player: int, last_move: Tuple[int,int,int]) -> Tuple[int,int]:
        opponent = 2 if player == 1 else 1

        # 1. 勝ち手を探す
        move = self.find_winning_move(board, player)
        if move:
            return move

        # 2. ブロック
        move = self.find_winning_move(board, opponent)
        if move:
            return move

        # 3. 中央優先
        for (x,y) in [(1,1),(2,1),(1,2),(2,2)]:
            if self.can_place(board, x, y):
                return (x,y)

        # 4. フォールバック
        for y in range(4):
            for x in range(4):
                if self.can_place(board, x, y):
                    return (x,y)
        return (0,0)  # 万一の保険

    def can_place(self, board: Board, x: int, y: int) -> bool:
        for z in range(4):
            if board[z][y][x] == 0:
                return True
        return False

    def find_winning_move(self, board: Board, player: int) -> Optional[Tuple[int,int]]:
        # 各 (x,y) 列について「仮に置いたら4目が完成するか」を判定
        for y in range(4):
            for x in range(4):
                z = self.next_z(board, x, y)
                if z is None:
                    continue
                # 仮に置いて勝てるか？
                board[z][y][x] = player
                if self.check_win(board, x, y, z, player):
                    board[z][y][x] = 0  # 戻す
                    return (x,y)
                board[z][y][x] = 0
        return None

    def next_z(self, board: Board, x: int, y: int) -> Optional[int]:
        for z in range(4):
            if board[z][y][x] == 0:
                return z
        return None

    def check_win(self, board: Board, x: int, y: int, z: int, player: int) -> bool:
        # ★ここが肝心： (x,y,z) を含む全方向の4目を確認する関数
        # 横・縦・高さ・斜めなど全部を網羅する必要あり
        # 今は未実装（骨組みだけ）
        return False

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
    

