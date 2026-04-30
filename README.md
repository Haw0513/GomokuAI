# GomokuAI
A Gomoku AI project using Minimax and Alpha-Beta pruning for Data Structures and Algorithms course.
GomokuAI - 基于 Alpha-Beta 剪枝的五子棋博弈系统
1. 项目背景
本项目为 2026 春季学期《数据结构与算法B》课程大作业。五子棋（Gomoku）是一个经典的博弈论问题，本项目旨在通过实现一个具备人工智能水平的五子棋程序，将课堂所学的博弈树搜索、启发式评估以及搜索剪枝等算法知识应用于实际工程中。

2. 核心算法与知识点应用
本项目深度应用了以下课程相关的算法与数据结构：
    博弈树搜索 (Minimax Algorithm)：模拟玩家与 AI 的交替落子过程，构建递归搜索树。
    Alpha-Beta 剪枝：通过动态维护搜索边界，剪去对结果无影响的分支，大幅提升搜索深度与效率。
    启发式评估函数 (Heuristic Evaluation)：针对棋盘状态进行量化评分。通过对“活四”、“冲四”、“活三”等关键棋型设定分值权重，辅助 AI 进行决策。
    二维数组数据结构：高效维护 15x15 的棋盘状态，并实现快速的胜负检测算法。

3. 运行指南
环境要求
   Python: 3.8 或以上版本
   Pygame: 2.0+（用于 GUI 交互）

安装与启动
    克隆仓库：
        Bash
        git clone https://github.com/Haw0513/GomokuAI.git
        cd GomokuAI
    安装依赖：
        Bash
        pip install -r requirements.txt
    运行程序：
        Bash
        python src/main.py
        
4. 仓库结构说明
Plaintext
├── src/            # 核心源代码
│   ├── main.py     # 程序入口与 GUI 循环
│   ├── board.py    # 棋盘数据结构与逻辑判定
│   └── ai.py       # Alpha-Beta 剪枝与评估算法
├── docs/           # 项目演示截图及说明文档
├── requirements.txt # 环境依赖清单
└── README.md       # 项目主说明文档

5. AI 工具使用声明
本项目在开发过程中使用了 AI 工具（Gemini）进行辅助：
AI 辅助部分：项目整体架构的设计规划、README 文档的初稿生成、以及基于 Pygame 的 GUI 基础样板代码。
独立实现部分：核心博弈算法逻辑（Alpha-Beta 剪枝）、启发式棋型评分函数、以及棋盘胜负判定算法均由本人独立分析并实现。

6. 学术诚信声明
本人郑重声明：本项目除上述声明的 AI 辅助内容及引用的标准库外，核心逻辑与系统架构均为本人自主完成。严禁任何形式的学术造假与抄袭。
