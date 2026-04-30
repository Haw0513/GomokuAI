import pygame
import numpy as np
import sys
import math

# --- 棋盘配置参数 ---
SIZE = 15               # 棋盘大小 15x15
GRID_SIZE = 40          # 格子大小
MARGIN = 40             # 边距
WINDOW_SIZE = GRID_SIZE * (SIZE - 1) + MARGIN * 2

# 颜色定义
BOARD_COLOR = (235, 184, 123)  # 经典木质棋盘色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Gomoku:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Gomoku AI - Alpha-Beta Pruning")
        self.board = np.zeros((SIZE, SIZE), dtype=int)  # 0:空, 1:玩家(黑), 2:AI(白)
        self.game_over = False
        self.winner = None

    def draw_board(self):
        """绘制棋盘与棋子"""
        self.screen.fill(BOARD_COLOR)
        for i in range(SIZE):
            # 画横线
            pygame.draw.line(self.screen, BLACK, (MARGIN, MARGIN + i * GRID_SIZE), (WINDOW_SIZE - MARGIN, MARGIN + i * GRID_SIZE), 1)
            # 画纵线
            pygame.draw.line(self.screen, BLACK, (MARGIN + i * GRID_SIZE, MARGIN), (MARGIN + i * GRID_SIZE, WINDOW_SIZE - MARGIN), 1)
        
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] != 0:
                    color = BLACK if self.board[r][c] == 1 else WHITE
                    pos = (MARGIN + c * GRID_SIZE, MARGIN + r * GRID_SIZE)
                    pygame.draw.circle(self.screen, color, pos, GRID_SIZE // 2 - 2)

    def check_win(self, r, c, p):
        """判断当前落子位置是否达成五连"""
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            # 正向探测
            for i in range(1, 5):
                nr, nc = r + dr*i, c + dc*i
                if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr][nc] == p: count += 1
                else: break
            # 反向探测
            for i in range(1, 5):
                nr, nc = r - dr*i, c - dc*i
                if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr][nc] == p: count += 1
                else: break
            if count >= 5: return True
        return False

    # --- 核心算法：启发式评估 ---
    def evaluate_board(self):
        """对整个棋盘状态进行评分，分值 = AI得分 - 玩家得分 * 惩罚系数"""
        ai_score = self.get_player_score(2)
        player_score = self.get_player_score(1)
        # 1.2 的系数是为了让 AI 更加注重防守，防止玩家轻易达成活四
        return ai_score - player_score * 1.2

    def get_player_score(self, p):
        """计算指定玩家在全盘的棋型总分"""
        score = 0
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == p:
                    score += self.count_score_at(r, c, p)
        return score

    def count_score_at(self, r, c, p):
        """针对单一棋子，评估其在四个方向上的潜力"""
        total = 0
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dr, dc in directions:
            line = []
            # 获取当前位置前后各 4 格的棋子序列
            for i in range(-4, 5):
                nr, nc = r + i*dr, c + i*dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE:
                    line.append(self.board[nr][nc])
            total += self.analyze_line(line, p)
        return total

    def analyze_line(self, line, p):
        """棋型识别矩阵：根据连续棋子数和空间返回评分"""
        line_str = "".join(map(str, line))
        p_str = str(p)
        
        # 棋型评分标准（可根据作业需求调整权重）
        if p_str * 5 in line_str: return 100000        # 五连
        if "0" + p_str * 4 + "0" in line_str: return 10000  # 活四
        if "0" + p_str * 3 + "0" in line_str: return 1000   # 活三
        if p_str * 4 in line_str: return 500          # 冲四/死四
        return 0

    # --- 搜索优化：局部搜索范围 ---
    def get_search_range(self):
        """
        局部搜索策略：
        只搜索已有棋子周围 2 格内的空位，大幅减少博弈树的分支因子（从 225 降至约 20-40）。
        """
        potential_moves = set()
        has_chess = False
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] != 0:
                    has_chess = True
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr][nc] == 0:
                                potential_moves.add((nr, nc))
        # 如果棋盘是空的（开局第一步），返回中心区域
        return list(potential_moves) if has_chess else []

    # --- 核心算法：Alpha-Beta 剪枝 ---
    def alpha_beta(self, depth, alpha, beta, maximizing_player):
        """递归搜索博弈树"""
        # 递归终点：达到预设深度
        if depth == 0:
            return self.evaluate_board()

        search_range = self.get_search_range()
        if not search_range: return 0

        if maximizing_player:
            max_eval = -math.inf
            # 按评分潜力排序可进一步提升剪枝效率，此处简单截取前 15 个点
            for r, c in search_range[:15]:
                self.board[r][c] = 2 # 模拟 AI 落子
                eval = self.alpha_beta(depth - 1, alpha, beta, False)
                self.board[r][c] = 0 # 撤销落子（回溯）
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:  # Beta 剪枝
                    break
            return max_eval
        else:
            min_eval = math.inf
            for r, c in search_range[:15]:
                self.board[r][c] = 1 # 模拟玩家落子
                eval = self.alpha_beta(depth - 1, alpha, beta, True)
                self.board[r][c] = 0 # 撤销落子
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:  # Alpha 剪枝
                    break
            return min_eval

    def ai_move(self):
        """AI 落子逻辑入口"""
        search_range = self.get_search_range()
        if not search_range:
            # 第一步直接下中心
            best_move = (SIZE // 2, SIZE // 2)
        else:
            best_score = -math.inf
            best_move = search_range[0]
            # 遍历当前可落子点，寻找最优解
            for r, c in search_range[:20]:
                self.board[r][c] = 2
                score = self.alpha_beta(2, -math.inf, math.inf, False)
                self.board[r][c] = 0
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
        
        self.board[best_move[0]][best_move[1]] = 2
        # 落子后检查是否获胜
        if self.check_win(best_move[0], best_move[1], 2):
            self.game_over = True
            self.winner = "AI (White)"

    def run(self):
        """游戏主循环"""
        while True:
            self.draw_board()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    # 获取鼠标点击位置并转化为棋盘坐标
                    x, y = event.pos
                    c = round((x - MARGIN) / GRID_SIZE)
                    r = round((y - MARGIN) / GRID_SIZE)
                    
                    if 0 <= r < SIZE and 0 <= c < SIZE and self.board[r][c] == 0:
                        # 玩家落子（黑棋）
                        self.board[r][c] = 1
                        if self.check_win(r, c, 1):
                            self.game_over = True
                            self.winner = "Player (Black)"
                        else:
                            # 玩家走完，AI 立即走棋
                            self.ai_move()

            if self.game_over:
                self.draw_board()
                pygame.display.flip()
                print(f"Game Over! Winner: {self.winner}")
                pygame.time.wait(3000) # 停留3秒显示结果
                self.__init__()        # 重置游戏

if __name__ == "__main__":
    game = Gomoku()
    game.run()
