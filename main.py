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


# 4x4x4 のユニーク方向 13種（正反対は同じ扱いにまとめる）
DIRS: List[Tuple[int,int,int]] = [
    (1,0,0), (0,1,0), (0,0,1),                 # x, y, z
    (1,1,0), (1,-1,0),                         # xy
    (1,0,1), (1,0,-1),                         # xz
    (0,1,1), (0,1,-1),                         # yz
    (1,1,1), (1,1,-1), (1,-1,1), (1,-1,-1),    # 立体対角
]

SIZE = 4
EMPTY = 0

def in_bounds(x:int,y:int,z:int)->bool:
    return 0 <= x < SIZE and 0 <= y < SIZE and 0 <= z < SIZE

def next_z(board: Board, x:int, y:int) -> Optional[int]:
    for z in range(SIZE):
        if board[z][y][x] == EMPTY:
            return z
    return None

def check_win_after(board: Board, x:int, y:int, z:int, player:int) -> bool:
    """(x,y,z) に player が置いた直後に4連か？"""
    for dx,dy,dz in DIRS:
        cnt = 1
        # 正方向
        nx, ny, nz = x+dx, y+dy, z+dz
        while in_bounds(nx,ny,nz) and board[nz][ny][nx] == player:
            cnt += 1; nx += dx; ny += dy; nz += dz
        # 逆方向
        nx, ny, nz = x-dx, y-dy, z-dz
        while in_bounds(nx,ny,nz) and board[nz][ny][nx] == player:
            cnt += 1; nx -= dx; ny -= dy; nz -= dz
        if cnt >= 4:
            return True
    return False

def list_moves(board: Board) -> List[Tuple[int,int,int]]:
    """(x,y,z)（zは落下後）で返す"""
    res = []
    for y in range(SIZE):
        for x in range(SIZE):
            z = next_z(board, x, y)
            if z is not None:
                res.append((x,y,z))
    return res

def copy_board(board: Board) -> Board:
    return [ [ row[:] for row in plane ] for plane in board ]

def place(board: Board, x:int,y:int,z:int, player:int) -> None:
    board[z][y][x] = player

def find_immediate_win(board: Board, player:int) -> Optional[Tuple[int,int]]:
    for x,y,z in list_moves(board):
        if check_win_after(board, x,y,z, player):
            return (x,y)
    return None

def gives_opp_immediate_win(board: Board, move_xy:Tuple[int,int], me:int) -> bool:
    """自分が move_xy を打った直後に、相手に即勝ち手が生まれるか？"""
    opp = 3 - me
    x,y = move_xy
    z = next_z(board, x, y)
    if z is None:  # そもそも置けない
        return True
    b2 = copy_board(board)
    place(b2, x,y,z, me)
    # 相手の即勝ち探索
    for ox,oy,oz in list_moves(b2):
        if check_win_after(b2, ox,oy,oz, opp):
            return True
    return False

def line_potential_score(board: Board, x:int,y:int,z:int, me:int) -> int:
    """簡易評価: 自分のライン伸長 + フォーク気味（3並び未満も加点） - 相手に与える利"""
    opp = 3 - me
    score = 0
    # 置いたと仮定
    b2 = copy_board(board)
    place(b2, x,y,z, me)

    # ライン評価（自分のみ・相手石が混ざるラインは無効）
    for dx,dy,dz in DIRS:
        stones_me = 1  # 今置いた1を含む
        stones_opp = 0
        # 集計（両方向）
        for sign in (1,-1):
            nx,ny,nz = x+dx*sign, y+dy*sign, z+dz*sign
            while in_bounds(nx,ny,nz):
                v = b2[nz][ny][nx]
                if v == me:
                    stones_me += 1
                elif v == opp:
                    stones_opp += 1
                    break
                nx += dx*sign; ny += dy*sign; nz += dz*sign
        if stones_opp == 0:
            # 自分専有ライン：個数に応じて重み
            if stones_me >= 3:  # 3並びは強い
                score += 5
            elif stones_me == 2:
                score += 2
            else:
                score += 1

    # 中央寄りボーナス（1.5,1.5 に近いほど加点）
    cx, cy = 1.5, 1.5
    dist = abs(x - cx) + abs(y - cy)
    score += int(4 - dist)  # だいたい 1〜4 程度

    # “高さzを揃えやすい横ライン”の監視（同一zでの x/y ライン）
    # 水平(x) と縦(y) は少し加点
    if z is not None:
        # 横
        me_on_row = sum(1 for xx in range(SIZE) if b2[z][y][xx] == me)
        opp_on_row = sum(1 for xx in range(SIZE) if b2[z][y][xx] == opp)
        if opp_on_row == 0 and me_on_row >= 2:
            score += 2
        # 縦
        me_on_col = sum(1 for yy in range(SIZE) if b2[z][yy][x] == me)
        opp_on_col = sum(1 for yy in range(SIZE) if b2[z][yy][x] == opp)
        if opp_on_col == 0 and me_on_col >= 2:
            score += 2

    return score

class MyAI(Alg3D):
    def get_move(
        self,
        board: Board,
        player: int,
        last_move: Tuple[int, int, int]
    ) -> Tuple[int, int]:

        # 1) 自分の即勝ち
        win_xy = find_immediate_win(board, player)
        if win_xy is not None:
            return win_xy

        # 2) 相手の即勝ちブロック
        opp = 3 - player
        opp_win_xy = find_immediate_win(board, opp)
        if opp_win_xy is not None:
            return opp_win_xy

        # 3) 候補列挙
        cand: List[Tuple[int,int,int]] = list_moves(board)
        if not cand:
            # 置けないことは基本ないが安全策
            return (0,0)

        # 3.5) 同じ柱への連打は原則避ける（例外：上の即勝/即ブロック）
        avoid_xy = (last_move[0], last_move[1]) if last_move is not None else None
        filtered: List[Tuple[int,int,int]] = []
        for x,y,z in cand:
            if avoid_xy is not None and (x,y) == avoid_xy:
                continue
            filtered.append((x,y,z))
        if not filtered:
            filtered = cand[:]  # すべて避けると空になる場合は許容

        # 4) 「相手の即勝を与える手」を除外
        safe: List[Tuple[int,int,int]] = []
        for x,y,z in filtered:
            if not gives_opp_immediate_win(board, (x,y), player):
                safe.append((x,y,z))
        if not safe:
            safe = filtered[:]  # どうしても危険しかないときは許容

        # 5) 簡易スコアで選ぶ
        best = None
        best_score = -10**9
        for x,y,z in safe:
            s = line_potential_score(board, x,y,z, player)
            if s > best_score:
                best_score = s
                best = (x,y)
        if best is not None:
            return best

        # フォールバック
        x,y,_ = safe[0]
        return (x,y)
