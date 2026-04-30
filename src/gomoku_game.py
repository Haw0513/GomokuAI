import pygame
import numpy as np
import sys
import math

# ================================================= =
# 配置参数：控制棋盘外观与基础设定
# ================================================= =
SIZE = 15               # 棋盘规格 (标准五子棋为 15x15)
GRID_SIZE = 40          # 绘图时每个方格的像素宽度
MARGIN = 40             # 棋盘边缘留白
WINDOW_SIZE = GRID_SIZE * (SIZE - 1) + MARGIN * 2

# 颜色常量 (RGB 格式)
BOARD_COLOR = (235, 184, 123)  # 经典的木质棋盘底色
BLACK = (0, 0, 0)              # 玩家棋子颜色
WHITE = (255, 255, 255)        # AI 棋子颜色

class Gomoku:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Gomoku AI - Alpha-Beta Pruning")
        # 初始化棋盘矩阵：0-空位, 1-玩家(黑), 2-AI(白)
        self.board = np.zeros((SIZE, SIZE), dtype=int)  
        self.game_over = False
        self.winner = None

    def draw_board(self):
        """渲染棋盘网格与所有已落下的棋子"""
        self.screen.fill(BOARD_COLOR)
        for i in range(SIZE):
            # 绘制水平线与垂直线
            pygame.draw.line(self.screen, BLACK, (MARGIN, MARGIN + i * GRID_SIZE), (WINDOW_SIZE - MARGIN, MARGIN + i * GRID_SIZE), 1)
            pygame.draw.line(self.screen, BLACK, (MARGIN + i * GRID_SIZE, MARGIN), (MARGIN + i * GRID_SIZE, WINDOW_SIZE - MARGIN), 1)
        
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] != 0:
                    color = BLACK if self.board[r][c] == 1 else WHITE
                    pos = (MARGIN + c * GRID_SIZE, MARGIN + r * GRID_SIZE)
                    # 绘制棋子，加上 2 像素的间距使画面更精致
                    pygame.draw.circle(self.screen, color, pos, GRID_SIZE // 2 - 2)

    def check_win(self, r, c, p):
        """
        判断在 (r, c) 处落下 p 棋子后，是否产生了五连珠。
        逻辑：检查横、竖、左斜、右斜四个方向。
        """
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            # 分别向该方向的正向和反向探测连续棋子
            for i in range(1, 5):
                nr, nc = r + dr*i, c + dc*i
                if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr][nc] == p: count += 1
                else: break
            for i in range(1, 5):
                nr, nc = r - dr*i, c - dc*i
                if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr][nc] == p: count += 1
                else: break
            if count >= 5: return True
        return False

    # --------------------------------------------------
    # 核心算法部分：启发式评估函数
    # --------------------------------------------------
    def evaluate_board(self):
        """
        对当前局势进行打分。
        AI 的目标是最大化 (AI得分 - 玩家得分 * 权重)。
        """
        ai_score = self.get_player_score(2)
        player_score = self.get_player_score(1)
        # 1.2 的系数是为了让 AI 稍微偏向防守，优先封堵玩家的活三/活四
        return ai_score - player_score * 1.2

    def get_player_score(self, p):
        """遍历棋盘，计算特定玩家的总分"""
        score = 0
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == p:
                    score += self.count_score_at(r, c, p)
        return score

    def count_score_at(self, r, c, p):
        """评估单个位置在所有方向上的棋型潜力"""
        total = 0
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dr, dc in directions:
            line = []
            # 获取当前位置前后 4 格构成的 9 格长序列进行模式匹配
            for i in range(-4, 5):
                nr, nc = r + i*dr, c + i*dc
                if 0 <= nr < SIZE and 0 <= nc < SIZE:
                    line.append(self.board[nr][nc])
            total += self.analyze_line(line, p)
        return total

    def analyze_line(self, line, p):
        """棋型识别：为识别出的不同组合分配权重分值"""
        line_str = "".join(map(str, line))
        p_str = str(p)
        
        # 评分模型：分值差距要拉开，确保 AI 知道五连珠比什么都重要
        if p_str * 5 in line_str: return 100000        # 五连：必胜
        if "0" + p_str * 4 + "0" in line_str: return 10000  # 活四：极高分
        if "0" + p_str * 3 + "0" in line_str: return 1000   # 活三：进攻核心
        if p_str * 4 in line_str: return 500          # 死四/冲四
        return 0

    # --------------------------------------------------
    # 算法优化：减少搜索广度
    # --------------------------------------------------
    def get_search_range(self):
        """
        局部化搜索：只在已有棋子周围 2 格的空位内进行搜索。
        这是性能优化的核心，避免了遍历 15x15 产生的算力浪费。
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
        return list(potential_moves) if has_chess else []

    # --------------------------------------------------
    # 核心算法：带剪枝的 Minimax 搜索
    # --------------------------------------------------
    def alpha_beta(self, depth, alpha, beta, maximizing_player):
        """
        Alpha-Beta 剪枝递归函数
        alpha: 当前搜索分支能保证的最小得分
        beta: 对手能保证的最高得分（对当前玩家来说是最坏情况）
        """
        if depth == 0:
            return self.evaluate_board()

        search_range = self.get_search_range()
        if not search_range: return 0

        if maximizing_player:
            max_eval = -math.inf
            # 为防止分支过多，只选取前 15 个高价值候选点（启发式截断）
            for r, c in search_range[:15]:
                self.board[r][c] = 2
                eval = self.alpha_beta(depth - 1, alpha, beta, False)
                self.board[r][c] = 0  # 状态回溯
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:  # 发现此分支不会有更好结果，直接剪枝
                    break
            return max_eval
        else:
            min_eval = math.inf
            for r, c in search_range[:15]:
                self.board[r][c] = 1
                eval = self.alpha_beta(depth - 1, alpha, beta, True)
                self.board[r][c] = 0
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:  # 剪枝
                    break
            return min_eval

    def ai_move(self):
        """AI 决策主逻辑：选择分值最高的走法"""
        search_range = self.get_search_range()
        if not search_range:
            best_move = (SIZE // 2, SIZE // 2)  # 第一步下中心
        else:
            best_score = -math.inf
            best_move = search_range[0]
            for r, c in search_range[:20]:  # 第一层可以搜索稍广一点
                self.board[r][c] = 2
                # 深度设为 2 可以在秒出结果的情况下提供不错的智商
                score = self.alpha_beta(2, -math.inf, math.inf, False)
                self.board[r][c] = 0
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
        
        self.board[best_move[0]][best_move[1]] = 2
        if self.check_win(best_move[0], best_move[1], 2):
            self.game_over = True
            self.winner = "AI (White)"

    def run(self):
        """游戏循环引擎"""
        while True:
            self.draw_board()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                # 监听鼠标点击落子
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    x, y = event.pos
                    # 计算逻辑坐标：像素转网格索引
                    c = round((x - MARGIN) / GRID_SIZE)
                    r = round((y - MARGIN) / GRID_SIZE)
                    
                    if 0 <= r < SIZE and 0 <= c < SIZE and self.board[r][c] == 0:
                        self.board[r][c] = 1
                        if self.check_win(r, c, 1):
                            self.game_over = True
                            self.winner = "Player (Black)"
                        else:
                            # 玩家落子后，立即触发 AI 计算
                            self.ai_move()

            if self.game_over:
                self.draw_board()
                pygame.display.flip()
                print(f"游戏结束！获胜者: {self.winner}")
                pygame.time.wait(3000) # 停留 3 秒展示获胜场景
                self.__init__()        # 自动重置开始新对局

if __name__ == "__main__":
    game = Gomoku()
    game.run()
