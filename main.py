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

DIRS = [
    (1,0,0),(0,1,0),(0,0,1),           # x, y, z
    (1,1,0),(1,-1,0),                  # xy 面の斜め
    (1,0,1),(1,0,-1),                  # xz 面の斜め
    (0,1,1),(0,1,-1),                  # yz 面の斜め
    (1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1)# 空間対角
]

class MyAI(Alg3D):
    def get_move(
        self, board: List[List[List[int]]], player: int, last_move: Tuple[int,int,int]
    ) -> Tuple[int,int]:
        opp = 2 if player == 1 else 1

        # 1) 自分が今すぐ勝てるならそこ
        m = self.find_winning_move(board, player)
        if m: return m

        # 2) 相手が今すぐ勝てる手をブロック
        m = self.find_winning_move(board, opp)
        if m: return m

        # 3) 中央優先（満杯でない列のみ）
        for (x,y) in [(1,1),(2,1),(1,2),(2,2)]:
            if self.next_z(board, x, y) is not None:
                return (x,y)

        # 4) その他の合法手
        for y in range(4):
            for x in range(4):
                if self.next_z(board, x, y) is not None:
                    return (x,y)

        return (0,0)  # 全埋まり保険

    # --- helpers ---
    def next_z(self, board, x, y) -> Optional[int]:
        for z in range(4):
            if board[z][y][x] == 0:
                return z
        return None

    def inb(self, x,y,z) -> bool:
        return 0 <= x < 4 and 0 <= y < 4 and 0 <= z < 4

    def line_count(self, board, x,y,z, dx,dy,dz, player) -> int:
        """(x,y,z) を含む直線で連なっている個数を数える（両方向）。"""
        cnt = 1
        # 正方向
        nx,ny,nz = x+dx, y+dy, z+dz
        while self.inb(nx,ny,nz) and board[nz][ny][nx] == player:
            cnt += 1
            nx += dx; ny += dy; nz += dz
        # 逆方向
        nx,ny,nz = x-dx, y-dy, z-dz
        while self.inb(nx,ny,nz) and board[nz][ny][nx] == player:
            cnt += 1
            nx -= dx; ny -= dy; nz -= dz
        return cnt

    def check_win(self, board, x,y,z, player) -> bool:
        for dx,dy,dz in DIRS:
            if self.line_count(board, x,y,z, dx,dy,dz, player) >= 4:
                return True
        return False

    def find_winning_move(self, board, player) -> Optional[Tuple[int,int]]:
        """重力を考慮して next_z に仮置き→4連完成する列を探す。"""
        for y in range(4):
            for x in range(4):
                z = self.next_z(board, x, y)
                if z is None:
                    continue
                board[z][y][x] = player
                win = self.check_win(board, x,y,z, player)
                board[z][y][x] = 0
                if win:
                    return (x,y)
        return None


# class MyAI(Alg3D):
#     def get_move(self, board: Board, player: int, last_move: Tuple[int,int,int]) -> Tuple[int,int]:
#         opponent = 2 if player == 1 else 1

#         # 1. 勝ち手を探す
#         move = self.find_winning_move(board, player)
#         if move:
#             return move

#         # 2. ブロック
#         move = self.find_winning_move(board, opponent)
#         if move:
#             return move

#         # 3. 中央優先
#         for (x,y) in [(1,1),(2,1),(1,2),(2,2)]:
#             if self.can_place(board, x, y):
#                 return (x,y)

#         # 4. フォールバック
#         for y in range(4):
#             for x in range(4):
#                 if self.can_place(board, x, y):
#                     return (x,y)
#         return (0,0)  # 万一の保険

#     def can_place(self, board: Board, x: int, y: int) -> bool:
#         for z in range(4):
#             if board[z][y][x] == 0:
#                 return True
#         return False

#     def find_winning_move(self, board: Board, player: int) -> Optional[Tuple[int,int]]:
#         # 各 (x,y) 列について「仮に置いたら4目が完成するか」を判定
#         for y in range(4):
#             for x in range(4):
#                 z = self.next_z(board, x, y)
#                 if z is None:
#                     continue
#                 # 仮に置いて勝てるか？
#                 board[z][y][x] = player
#                 if self.check_win(board, x, y, z, player):
#                     board[z][y][x] = 0  # 戻す
#                     return (x,y)
#                 board[z][y][x] = 0
#         return None

#     def next_z(self, board: Board, x: int, y: int) -> Optional[int]:
#         for z in range(4):
#             if board[z][y][x] == 0:
#                 return z
#         return None

#     def check_win(self, board: Board, x: int, y: int, z: int, player: int) -> bool:
#         # ★ここが肝心： (x,y,z) を含む全方向の4目を確認する関数
#         # 横・縦・高さ・斜めなど全部を網羅する必要あり
#         # 今は未実装（骨組みだけ）
#         return False

