"""
配置文件
存储API密钥和系统参数
"""

import os

# ==================== API配置 ====================
# 优先使用环境变量，本地开发时使用默认值
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-55095a34f24143668f49ffd9d020fd33")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen-max")

# ==================== 数据生成配置 ====================
DIALOGUE_CONFIG = {
    "total_samples": 150,  # 总对话数
    "samples_per_group": 50,  # 每组对话数
    "turns_per_dialogue": 36,  # 每段对话轮数
    "groups": ["HC", "MCI", "ED"],  # 认知状态分组
    "scenarios": [
        "找东西",
        "做饭",
        "日程安排",
        "回忆往事",
        "提醒吃药",
        "日常闲聊",
        "看电视讨论",
        "准备外出"
    ]
}

# ==================== 路径配置 ====================
DATA_DIR = "data"
DB_DIR = "database"
DIALOGUE_FILE = os.path.join(DATA_DIR, "dialogues.json")
DB_FILE = os.path.join(DB_DIR, "cogsense.db")

# ==================== 评分阈值配置 ====================
SCORING_THRESHOLDS = {
    "risk_levels": {
        "low": 80,      # >= 80分为低风险
        "medium": 60,   # 60-79分为中风险
        "high": 0       # < 60分为高风险
    },
    "weights": {
        "memory": 0.25,
        "planning": 0.20,
        "recall": 0.20,
        "coherence": 0.20,
        "temporal_orientation": 0.15
    }
}

# ==================== UI配置 ====================
PAGE_CONFIG = {
    "page_title": "CogSense - 认知健康监测系统",
    "page_icon": "🧠",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)
