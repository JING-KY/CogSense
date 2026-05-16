"""
CogSense - 认知健康监测系统
Streamlit主应用
"""

import streamlit as st
import time
import random
import os
from datetime import datetime

# 导入核心模块
from modules import (
    DialogueGenerator,
    LinguisticAnalyzer,
    CognitiveScorer,
    DatabaseManager,
    ReportGenerator
)

# 导入工具模块
from utils.visualization import (
    create_radar_chart,
    create_trend_chart,
    create_feature_table,
    create_risk_distribution_chart,
    create_group_distribution_chart,
    create_score_comparison_chart,
    format_dialogue_for_display
)

# 导入配置
from config import PAGE_CONFIG, DIALOGUE_CONFIG


# ==================== 页面配置 ====================
st.set_page_config(**PAGE_CONFIG)


# ==================== 初始化会话状态 ====================
def init_session_state():
    """初始化Streamlit会话状态"""
    if 'dialogue_generator' not in st.session_state:
        st.session_state.dialogue_generator = DialogueGenerator()
    
    if 'linguistic_analyzer' not in st.session_state:
        st.session_state.linguistic_analyzer = LinguisticAnalyzer()
    
    if 'cognitive_scorer' not in st.session_state:
        st.session_state.cognitive_scorer = CognitiveScorer()
    
    if 'database_manager' not in st.session_state:
        st.session_state.database_manager = DatabaseManager()
    
    if 'report_generator' not in st.session_state:
        st.session_state.report_generator = ReportGenerator()
    
    # 自动加载已存在的对话数据
    if 'dialogues' not in st.session_state:
        generator = st.session_state.dialogue_generator
        if generator.dialogues_exist():
            st.session_state.dialogues = generator.load_dialogues()
        else:
            st.session_state.dialogues = []
    
    if 'current_dialogue' not in st.session_state:
        st.session_state.current_dialogue = None
    
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    
    if 'monitoring_active' not in st.session_state:
        st.session_state.monitoring_active = False
    
    if 'monitoring_index' not in st.session_state:
        st.session_state.monitoring_index = 0
    
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None


init_session_state()


# ==================== 全局 UI 样式注入 ====================
st.markdown("""
<style>
/* ── 字体与基础变量 ── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    /* ── Scientific Modern / Gemini-inspired 主题 ── */
    --clr-primary:      #4F46E5;   /* 现代靛蓝·主色调 */
    --clr-primary-lt:   #EEF2FF;   /* 极浅靛蓝 */
    --clr-primary-dk:   #3730A3;   /* 深靛蓝 */
    --clr-teal:         #0EA5E9;   /* 科技天蓝 (替代原青绿，与靛蓝更搭配) */
    --clr-teal-lt:      #F0F9FF;   
    --clr-coral:        #F43F5E;   /* 现代玫瑰红 */
    --clr-bg:           #FAFAFA;   /* 极净清透灰白底色，比纯白更有质感 */
    --clr-card:         #FFFFFF;
    --clr-border:       #E5E7EB;   /* 柔和科技感边框 */
    --clr-text:         #111827;   /* 深石板灰文字，高级感强于纯黑 */
    --clr-text-muted:   #6B7280;   /* 柔和中灰 */
    --clr-success:      #10B981;   /* 健康翠绿 */
    --clr-success-lt:   #ECFDF5;
    --clr-warn:         #F59E0B;   /* 琥珀黄警告 */
    --clr-warn-lt:      #FFFBEB;
    --clr-error:        #EF4444;   /* 鲜明红色 */
    --clr-error-lt:     #FEF2F2;
    --radius-sm:        8px;
    --radius-md:        12px;
    --radius-lg:        16px;
    --shadow-sm:        0 1px 3px rgba(17,24,39,0.06);
    --shadow-md:        0 4px 12px rgba(17,24,39,0.08);
    --shadow-lg:        0 10px 25px rgba(79,70,229,0.12);
    --transition:       all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── 全局字体 ── */
html, body, [class*="css"] {
    font-family: 'Noto Sans SC', 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--clr-text);
}

/* ── 主内容区背景 ── */
.stApp {
    background-color: var(--clr-bg);
}

/* ── 主标题样式 ── */
h1 {
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    color: var(--clr-text) !important;
}
h2, h3 {
    font-weight: 600 !important;
    color: var(--clr-text) !important;
}

/* ── 按钮全局增强 ── */
div.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: var(--transition) !important;
    border: 1.5px solid var(--clr-border) !important;
    background: var(--clr-card) !important;
    color: var(--clr-text) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 0.45rem 1rem !important;
}
div.stButton > button:hover {
    background: var(--clr-primary-lt) !important;
    border-color: var(--clr-primary) !important;
    color: var(--clr-primary) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}
div.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: var(--shadow-sm) !important;
}
/* primary 类型按钮 */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid*="primary"] {
    background: var(--clr-primary) !important;
    color: #fff !important;
    border-color: var(--clr-primary) !important;
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid*="primary"]:hover {
    background: var(--clr-primary-dk) !important;
    border-color: var(--clr-primary-dk) !important;
    color: #fff !important;
    box-shadow: 0 4px 12px rgba(79,70,229,0.3) !important;
}

/* ── 输入框聚焦效果 ── */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stTextInput"] > div > div > input {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--clr-border) !important;
    transition: var(--transition) !important;
    background: var(--clr-card) !important;
}
div[data-testid="stSelectbox"] > div > div:focus-within,
div[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--clr-primary) !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
}

/* ── Metric 卡片 ── */
div[data-testid="stMetric"] {
    background: var(--clr-card);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-md);
    padding: 16px 18px !important;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}
div[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
    border-color: var(--clr-primary-lt);
}
div[data-testid="stMetricLabel"] > div {
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--clr-text-muted) !important;
}
div[data-testid="stMetricValue"] > div {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: var(--clr-primary) !important;
}

/* ── 侧边栏 ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A0F24 0%, #161B33 100%) !important;
    border-right: none !important;
    padding-top: 0rem !important;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1rem !important;
}            
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.95) !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li {
    color: rgba(255,255,255,0.75) !important;
    font-size: 13px;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
    margin: 12px 0 !important;
}
/* 侧边栏 radio 导航 */
section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
    border-radius: var(--radius-sm) !important;
    padding: 8px 12px !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
    transition: var(--transition) !important;
    color: rgba(255,255,255,0.75) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.95) !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] [aria-checked="true"] + label,
section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {
    background: rgba(79, 70, 229, 0.25) !important;
    border-left: 3px solid var(--clr-primary) !important;
    font-weight: 600 !important;
    color: #fff !important;
}
/* 侧边栏按钮 */
section[data-testid="stSidebar"] div.stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: rgba(255,255,255,0.9) !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.3) !important;
    color: #fff !important;
    transform: translateY(-1px) !important;
}
/* 侧边栏 metric */
section[data-testid="stSidebar"] div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
section[data-testid="stSidebar"] div[data-testid="stMetricValue"] > div {
    color: #fff !important;
}
section[data-testid="stSidebar"] div[data-testid="stMetricLabel"] > div {
    color: rgba(255,255,255,0.65) !important;
}
/* 侧边栏 expander */
section[data-testid="stSidebar"] div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-sm) !important;
}
/* 侧边栏 success/warning 提示 */
section[data-testid="stSidebar"] div[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-size: 13px !important;
    background: rgba(255,255,255,0.08) !important;
    border: none !important;
}

/* ── Tabs ── */
div[data-testid="stTabs"] > div > div > button {
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    font-weight: 500 !important;
    transition: var(--transition) !important;
}

/* ── Expander ── */
div[data-testid="stExpander"] {
    border: 1px solid var(--clr-border) !important;
    border-radius: var(--radius-md) !important;
    background: var(--clr-card) !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden;
}
div[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    padding: 12px 16px !important;
}

/* ── Alert 框 ── */
div[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border-left-width: 4px !important;
    font-size: 14px !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    border: 1px solid var(--clr-border) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── 分隔线 ── */
hr {
    border: none !important;
    border-top: 1px solid var(--clr-border) !important;
    margin: 24px 0 !important;
}

/* ── 自定义卡片工具类 ── */
.cs-card {
    background: var(--clr-card);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-md);
    padding: 20px 24px;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    margin-bottom: 12px;
}
.cs-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
.cs-feature-card {
    background: var(--clr-card);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-md);
    padding: 24px 20px;
    box-shadow: var(--shadow-sm);
    text-align: center;
    height: 100%;
    transition: var(--transition);
}
.cs-feature-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--clr-primary);
    transform: translateY(-3px);
}
.cs-feature-icon {
    width: 56px; height: 56px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    margin: 0 auto 14px;
}
.cs-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.cs-badge-blue  { background: var(--clr-primary-lt); color: var(--clr-primary); }
.cs-badge-teal  { background: var(--clr-teal-lt);    color: var(--clr-teal); }
.cs-badge-green { background: var(--clr-success-lt); color: var(--clr-success); }
.cs-badge-warn  { background: var(--clr-warn-lt);    color: var(--clr-warn); }
.cs-badge-red   { background: var(--clr-error-lt);   color: var(--clr-error); }

/* ── 时间轴步骤 ── */
.cs-step {
    display: flex;
    gap: 16px;
    align-items: flex-start;
    margin-bottom: 18px;
    padding: 16px;
    background: var(--clr-card);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}
.cs-step:hover { box-shadow: var(--shadow-md); border-color: var(--clr-primary); }
.cs-step-num {
    width: 36px; height: 36px; min-width: 36px;
    border-radius: 50%;
    background: var(--clr-primary);
    color: #fff;
    font-weight: 700;
    font-size: 15px;
    display: flex; align-items: center; justify-content: center;
}
.cs-step-body strong { color: var(--clr-text); font-size: 14px; }
.cs-step-body p { color: var(--clr-text-muted); font-size: 13px; margin: 2px 0 0; }

/* ── 对话气泡 ── */
.cs-bubble-elder {
    margin-bottom: 14px;
    padding: 14px 16px;
    border-left: 4px solid var(--clr-primary);
    background: var(--clr-primary-lt);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    transition: var(--transition);
}
.cs-bubble-elder:hover { box-shadow: var(--shadow-sm); }
.cs-bubble-family {
    margin-bottom: 14px;
    padding: 14px 16px;
    border-left: 4px solid var(--clr-teal);
    background: var(--clr-teal-lt);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    transition: var(--transition);
}
.cs-bubble-family:hover { box-shadow: var(--shadow-sm); }
.cs-bubble-speaker {
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.cs-bubble-text {
    line-height: 1.7;
    font-size: 14.5px;
}

/* ── 事件警报 ── */
.cs-event {
    margin-bottom: 12px;
    padding: 12px 14px;
    border-radius: var(--radius-md);
    border-left: 4px solid;
    background: #fafafa;
    transition: var(--transition);
}
.cs-event:hover { box-shadow: var(--shadow-sm); }
.cs-event-title { font-weight: 600; font-size: 13px; margin-bottom: 5px; }
.cs-event-hint  { font-size: 12.5px; color: var(--clr-text-muted); }
.cs-event-high   { border-color: var(--clr-error);   background: var(--clr-error-lt); }
.cs-event-medium { border-color: var(--clr-warn);    background: var(--clr-warn-lt); }
.cs-event-low    { border-color: var(--clr-success);  background: var(--clr-success-lt); }

/* ── 报告封面 ── */
.cs-report-header {
    background: linear-gradient(135deg, var(--clr-primary) 0%, #8B5CF6 100%);
    border-radius: var(--radius-lg);
    padding: 32px 36px;
    color: #fff;
    margin-bottom: 28px;
    box-shadow: var(--shadow-lg);
}
.cs-report-header h2 { color: #fff !important; margin: 0 0 8px; font-size: 22px; }
.cs-report-header .subtitle { opacity: 0.9; font-size: 13px; }

/* ── 风险卡片 ── */
.cs-risk-card {
    border-radius: var(--radius-md);
    padding: 18px 22px;
    margin-bottom: 16px;
    border-left: 5px solid;
    box-shadow: var(--shadow-sm);
}
.cs-risk-card.low    { background: var(--clr-success-lt); border-color: var(--clr-success); }
.cs-risk-card.medium { background: var(--clr-warn-lt);    border-color: var(--clr-warn); }
.cs-risk-card.high   { background: var(--clr-error-lt);   border-color: var(--clr-error); }
.cs-risk-level {
    font-size: 16px; font-weight: 700; margin-bottom: 6px;
}
.cs-risk-desc { font-size: 14px; line-height: 1.6; }

/* ── 建议列表 ── */
.cs-rec-item {
    display: flex;
    gap: 14px;
    align-items: flex-start;
    padding: 14px 18px;
    background: var(--clr-card);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-md);
    margin-bottom: 10px;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}
.cs-rec-item:hover { box-shadow: var(--shadow-md); border-color: var(--clr-teal); }
.cs-rec-num {
    width: 28px; height: 28px; min-width: 28px;
    border-radius: 50%;
    background: var(--clr-teal);
    color: #fff;
    font-weight: 700;
    font-size: 13px;
    display: flex; align-items: center; justify-content: center;
}
.cs-rec-text { font-size: 14px; line-height: 1.65; color: var(--clr-text); padding-top: 3px; }

/* ── Hero 横幅 ── */
.cs-hero {
    background: linear-gradient(135deg, var(--clr-primary-lt) 0%, #FFFFFF 100%);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    margin-bottom: 8px;
    box-shadow: var(--shadow-sm);
}
.cs-hero h3 { margin: 0 0 10px; color: var(--clr-primary) !important; font-size: 18px; }
.cs-hero p  { color: var(--clr-text-muted); font-size: 14.5px; line-height: 1.7; margin: 0; }

/* ── 统计大卡片 ── */
.cs-stat-card {
    background: var(--clr-card);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-md);
    padding: 20px;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}
.cs-stat-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.cs-stat-value { font-size: 32px; font-weight: 700; color: var(--clr-primary); line-height: 1.1; }
.cs-stat-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; color: var(--clr-text-muted); margin-top: 6px; }

/* ── 作者信息卡片 ── */
.cs-author-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: var(--radius-md);
    padding: 14px 16px;
    margin-top: 4px;
}
.cs-author-card .name  { font-weight: 700; font-size: 14px; color: #fff; margin-bottom: 4px; }
.cs-author-card .email { font-size: 12px; color: rgba(255,255,255,0.72); margin-bottom: 4px; }
.cs-author-card .link  { font-size: 12px; }
.cs-author-card .inst  { font-size: 11px; color: rgba(255,255,255,0.55); margin-top: 6px; }

/* ── 快速开始步骤 ── */
.cs-quickstart {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    padding: 12px 16px;
    background: var(--clr-card);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-md);
    margin-bottom: 8px;
    transition: var(--transition);
}
.cs-quickstart:hover { border-color: var(--clr-primary); box-shadow: var(--shadow-sm); }
.cs-quickstart-num {
    background: var(--clr-primary-lt);
    color: var(--clr-primary);
    font-weight: 700;
    font-size: 13px;
    width: 26px; height: 26px; min-width: 26px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
}
.cs-quickstart-text { font-size: 14px; color: var(--clr-text); line-height: 1.5; padding-top: 2px; }

/* ── 监测信息徽章行 ── */
.cs-info-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: var(--clr-card);
    border: 1px solid var(--clr-border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    font-size: 14px;
}
.cs-info-badge .label {
    font-weight: 600;
    color: var(--clr-text-muted);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.cs-info-badge .value {
    font-weight: 600;
    color: var(--clr-text);
}

/* ── 分析完成提示区 ── */
.cs-completion-card {
    background: linear-gradient(135deg, #EEF2FF 0%, #F0F9FF 100%);
    border: 1px solid #C7D2FE;
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-top: 8px;
    box-shadow: var(--shadow-sm);
}

/* ── 五维体系信息卡 ── */
.cs-dim-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    background: var(--clr-card);
    border-radius: var(--radius-sm);
    margin-bottom: 8px;
    border: 1px solid var(--clr-border);
    transition: var(--transition);
}
.cs-dim-item:hover { border-color: var(--clr-primary); }
.cs-dim-dot {
    width: 10px; height: 10px; min-width: 10px;
    border-radius: 50%;
    background: var(--clr-primary);
}
.cs-dim-name { font-weight: 600; font-size: 13.5px; flex: 1; color: var(--clr-text); }
.cs-dim-pct  { font-size: 12px; font-weight: 600; color: var(--clr-text-muted); white-space: nowrap; }
.cs-dim-desc { font-size: 12px; color: var(--clr-text-muted); }
</style>
""", unsafe_allow_html=True)


# ==================== 侧边栏导航 ====================
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        # 将标题替换为自定义字号的 HTML
        st.markdown(
            """
            <div style="padding: 0px 0 8px;">
                <h1 style='font-size: 36px; margin: 6; color: #fff !important; font-weight: 600; letter-spacing: -1px;'>
                    🧠 CogSense
                </h1>
                <div style="font-size: 12px; color: rgba(255,255,255,0.62); margin-top: 4px; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 400;">
                                 ________认知健康 · 无感监测________
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        # 页面选择
        page = st.radio(
            "导航",
            ["📊 系统概览", "🎙️ 实时监测", "📈 分析仪表板", "📄 评估报告"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 数据管理
        st.markdown(
            "<p style='font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1.2px; color:rgba(255,255,255,0.55); margin-bottom:8px;'>数据管理</p>",
            unsafe_allow_html=True
        )
        
        # 检查对话数据是否存在
        dialogues_exist = st.session_state.dialogue_generator.dialogues_exist()
        
        if dialogues_exist:
            st.success(f"✅ 已加载 {len(st.session_state.dialogues)} 条对话")
            
            if st.button("🔄 重新生成数据", use_container_width=True):
                if st.session_state.get('confirm_regenerate', False):
                    with st.spinner("正在生成对话数据..."):
                        generate_dialogues()
                    st.session_state.confirm_regenerate = False
                    st.rerun()
                else:
                    st.session_state.confirm_regenerate = True
                    st.warning("⚠️ 再次点击确认重新生成")
        else:
            st.warning("⚠️ 未找到对话数据")
            
            if st.button("🚀 生成对话数据", use_container_width=True):
                with st.spinner("正在生成对话数据，请稍候..."):
                    generate_dialogues()
                st.rerun()
        
        st.markdown("---")
        
        # 统计信息
        st.markdown(
            "<p style='font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1.2px; color:rgba(255,255,255,0.55); margin-bottom:8px;'>系统统计</p>",
            unsafe_allow_html=True
        )
        stats = st.session_state.database_manager.get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("总会话数", stats.get("total_sessions", 0))
        with col2:
            st.metric("平均得分", f"{stats.get('avg_score', 0):.1f}")
        
        st.markdown("---")
        
        # 关于
        with st.expander("ℹ️ 关于系统"):
            st.markdown("""
            **CogSense** 是一个基于自然对话的认知健康被动监测系统原型。
            
            **版本**: 0.0.0  
            **发布日期**: 2026-05-15
            """)
        
        # 作者信息
        st.markdown("---")
        st.markdown("""
        <div class="cs-author-card">
            <div class="name">👤 JING_KY</div>
            <div class="email">📧 jingky@life.hkbu.edu.hk</div>
            <div class="link">
                <a href="https://github.com/JING-KY?tab=repositories"
                   style="color:rgba(255,255,255,0.80); text-decoration:none;">
                    🔗 GitHub Repository
                </a>
            </div>
            <div class="inst">🏫 HKBU | SHS</div>
        </div>
        """, unsafe_allow_html=True)
        
        return page


def generate_dialogues():
    """生成对话数据"""
    generator = st.session_state.dialogue_generator
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current, total, group, scenario):
        progress = current / total
        progress_bar.progress(progress)
        status_text.text(f"正在生成: {group} 组 - {scenario} ({current}/{total})")
    
    # 生成对话
    dialogues = generator.generate_all_dialogues(progress_callback=update_progress)
    
    # 保存到文件
    generator.save_dialogues(dialogues)
    
    # 更新会话状态
    st.session_state.dialogues = dialogues
    
    # 清除进度显示
    progress_bar.empty()
    status_text.empty()
    
    st.success(f"✅ 成功生成 {len(dialogues)} 条对话！")


# ==================== 页面1: 系统概览 ====================
def render_overview_page():
    """渲染系统概览页面"""
    st.title("📊 CogSense - 认知健康监测系统")
    st.markdown("---")
    
    # 系统介绍 —— Hero 横幅
    st.markdown("""
    <div class="cs-hero">
        <h3>🔬 系统简介</h3>
        <p>
            <strong>CogSense</strong> 是一个创新的认知健康被动监测系统，通过分析家庭自然对话中的语言特征，
            识别老年人的认知下降风险。<br><br>
            与传统的主动认知测评（如 MoCA、MMSE）不同，本系统采用 <strong>被动式监测</strong> 方式，
            在不打扰用户日常生活的情况下，持续评估认知健康状态。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 核心功能 —— 卡片式布局
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="cs-feature-card">
            <div class="cs-feature-icon" style="background:#EEF2FF; color:#4F46E5;">🎙️</div>
            <div style="font-weight:700; font-size:15px; margin-bottom:10px; color:#111827;">对话生成</div>
            <div style="font-size:13px; color:#6B7280; line-height:1.8;">
                ✦ 模拟真实家庭场景<br>
                ✦ 三类不同认知状态<br>
                ✦ 多样化的对话场景
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="cs-feature-card">
            <div class="cs-feature-icon" style="background:#F0F9FF; color:#0EA5E9;">🔍</div>
            <div style="font-weight:700; font-size:15px; margin-bottom:10px; color:#111827;">语言分析</div>
            <div style="font-size:13px; color:#6B7280; line-height:1.8;">
                ✦ 词汇丰富度分析<br>
                ✦ 语义连贯性评估<br>
                ✦ 时间定向性检测
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="cs-feature-card">
            <div class="cs-feature-icon" style="background:#F5F3FF; color:#8B5CF6;">📊</div>
            <div style="font-weight:700; font-size:15px; margin-bottom:10px; color:#111827;">认知评分</div>
            <div style="font-size:13px; color:#6B7280; line-height:1.8;">
                ✦ 五维评分体系<br>
                ✦ 风险等级评定<br>
                ✦ 专业报告生成
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    

    # 系统架构
    st.subheader("🏗️ 系统架构")

    st.markdown("""
    <style>
        div[data-testid="stMarkdownContainer"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        .layer {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 0px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            overflow: hidden;
            border: 1px solid #E5E7EB;
        }
        .layer-title {
            font-size: clamp(14px, 2vw, 20px);
            font-weight: bold;
            color: #111827;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }
        .layer-title .icon {
            font-size: clamp(16px, 2.5vw, 24px);
            margin-right: 10px;
        }
        .modules {
            display: flex;
            flex-wrap: nowrap;
            gap: clamp(6px, 1vw, 15px);
            margin-top: 8px;
            width: 100%;
            box-sizing: border-box;
        }
        .module-card {
            flex: 1 1 0;
            min-width: 0;
            background: #FAFAFA;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: clamp(6px, 1.5vw, 15px);
            text-align: center;
            transition: all 0.3s;
            box-sizing: border-box;
        }
        .module-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(79,70,229,0.15);
            border-color: #4F46E5;
        }
        .module-icon {
            font-size: clamp(18px, 3vw, 32px);
            margin-bottom: 8px;
            line-height: 1.2;
        }
        .module-name {
            font-weight: 600;
            color: #111827;
            margin-bottom: 5px;
            font-size: clamp(10px, 1.2vw, 14px);
            word-break: break-word;
        }
        .module-desc {
            font-size: clamp(9px, 1vw, 12px);
            color: #6B7280;
            word-break: break-word;
        }
        .arrow {
            text-align: center;
            font-size: 30px;
            color: white;
            margin: 10px 0;
        }
    </style>
    <div class="architecture-container">
    """, unsafe_allow_html=True)

    # 第一层：用户界面层
    st.markdown("""
        <div class="layer" style="border-left: 5px solid #4F46E5;">
            <div class="layer-title">
                <span class="icon">🖥️</span>
                用户界面层 (Streamlit Web Application)
            </div>
            <div class="modules">
                <div class="module-card">
                    <div class="module-icon">📊</div>
                    <div class="module-name">系统概览</div>
                    <div class="module-desc">Overview</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">🎙️</div>
                    <div class="module-name">实时监测</div>
                    <div class="module-desc">Monitoring</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">📈</div>
                    <div class="module-name">分析仪表板</div>
                    <div class="module-desc">Analytics</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">📄</div>
                    <div class="module-name">评估报告</div>
                    <div class="module-desc">Report</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 第二层：核心模块层
    st.markdown("""
        <div class="layer" style="border-left: 5px solid #0EA5E9; margin-top: 15px;">
            <div class="layer-title">
                <span class="icon">⚙️</span>
                核心模块层 (Business Logic & Processing)
            </div>
            <div class="modules">
                <div class="module-card">
                    <div class="module-icon">💬</div>
                    <div class="module-name">对话生成</div>
                    <div class="module-desc">Dialogue Generator</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">🔍</div>
                    <div class="module-name">语言分析</div>
                    <div class="module-desc">Linguistic Analyzer</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">🧠</div>
                    <div class="module-name">认知评分</div>
                    <div class="module-desc">Cognitive Scorer</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">💾</div>
                    <div class="module-name">数据管理</div>
                    <div class="module-desc">Database Manager</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">📋</div>
                    <div class="module-name">报告生成</div>
                    <div class="module-desc">Report Generator</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 第三层：数据层
    st.markdown("""
        <div class="layer" style="border-left: 5px solid #8B5CF6; margin-top: 15px;">
            <div class="layer-title">
                <span class="icon">💿</span>
                数据层 (Storage & External Services)
            </div>
            <div class="modules">
                <div class="module-card">
                    <div class="module-icon">🤖</div>
                    <div class="module-name">通义千问API</div>
                    <div class="module-desc">Qwen LLM Service</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">🗄️</div>
                    <div class="module-name">SQLite数据库</div>
                    <div class="module-desc">Local Database</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">📁</div>
                    <div class="module-name">JSON文件</div>
                    <div class="module-desc">Data Cache</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

        
    # 工作流程 —— 时间轴 + 五维体系
    st.subheader("🔄 工作流程")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div class="cs-step">
            <div class="cs-step-num">1</div>
            <div class="cs-step-body">
                <strong>对话生成</strong>
                <p>使用 LLM 生成模拟对话</p>
            </div>
        </div>
        <div class="cs-step">
            <div class="cs-step-num">2</div>
            <div class="cs-step-body">
                <strong>语言分析</strong>
                <p>提取 8 项语言特征</p>
            </div>
        </div>
        <div class="cs-step">
            <div class="cs-step-num">3</div>
            <div class="cs-step-body">
                <strong>认知评分</strong>
                <p>计算五维认知得分</p>
            </div>
        </div>
        <div class="cs-step">
            <div class="cs-step-num">4</div>
            <div class="cs-step-body">
                <strong>风险评估</strong>
                <p>确定风险等级</p>
            </div>
        </div>
        <div class="cs-step">
            <div class="cs-step-num">5</div>
            <div class="cs-step-body">
                <strong>报告生成</strong>
                <p>输出专业评估报告</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="cs-card" style="border-top: 3px solid #4F46E5;">
            <div style="font-weight:700; font-size:15px; margin-bottom:14px; color:#4F46E5;">
                📐 五维认知评分体系
            </div>
            <div class="cs-dim-item">
                <div class="cs-dim-dot" style="background:#4F46E5;"></div>
                <div class="cs-dim-name">记忆力 <span style="font-size:11px;color:#6B7280;">(Memory)</span></div>
                <div class="cs-dim-pct">25%</div>
            </div>
            <div style="font-size:12px;color:#6B7280;padding: 2px 0 10px 22px;">评估短期记忆和信息保持能力</div>
            <div class="cs-dim-item">
                <div class="cs-dim-dot" style="background:#0EA5E9;"></div>
                <div class="cs-dim-name">计划能力 <span style="font-size:11px;color:#6B7280;">(Planning)</span></div>
                <div class="cs-dim-pct">20%</div>
            </div>
            <div style="font-size:12px;color:#6B7280;padding: 2px 0 10px 22px;">评估执行功能和逻辑思维能力</div>
            <div class="cs-dim-item">
                <div class="cs-dim-dot" style="background:#8B5CF6;"></div>
                <div class="cs-dim-name">回忆能力 <span style="font-size:11px;color:#6B7280;">(Recall)</span></div>
                <div class="cs-dim-pct">20%</div>
            </div>
            <div style="font-size:12px;color:#6B7280;padding: 2px 0 10px 22px;">评估长期记忆和信息提取能力</div>
            <div class="cs-dim-item">
                <div class="cs-dim-dot" style="background:#F59E0B;"></div>
                <div class="cs-dim-name">连贯性 <span style="font-size:11px;color:#6B7280;">(Coherence)</span></div>
                <div class="cs-dim-pct">20%</div>
            </div>
            <div style="font-size:12px;color:#6B7280;padding: 2px 0 10px 22px;">评估语言组织和逻辑连贯性</div>
            <div class="cs-dim-item">
                <div class="cs-dim-dot" style="background:#F43F5E;"></div>
                <div class="cs-dim-name">时间定向 <span style="font-size:11px;color:#6B7280;">(Temporal Orientation)</span></div>
                <div class="cs-dim-pct">15%</div>
            </div>
            <div style="font-size:12px;color:#6B7280;padding: 2px 0 4px 22px;">评估时间感知和定向能力</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 快速开始 —— 卡片式步骤
    st.subheader("🚀 快速开始")
    
    st.markdown("""
    <div class="cs-quickstart">
        <div class="cs-quickstart-num">1</div>
        <div class="cs-quickstart-text"><strong>生成数据</strong>：在侧边栏点击"生成对话数据"按钮（此版本已预加载，无需操作）</div>
    </div>
    <div class="cs-quickstart">
        <div class="cs-quickstart-num">2</div>
        <div class="cs-quickstart-text"><strong>实时监测</strong>：前往"实时监测"页面，模拟对话流，完成后点击"查看完整分析"</div>
    </div>
    <div class="cs-quickstart">
        <div class="cs-quickstart-num">3</div>
        <div class="cs-quickstart-text"><strong>查看分析</strong>：在"分析仪表板"查看详细指标</div>
    </div>
    <div class="cs-quickstart">
        <div class="cs-quickstart-num">4</div>
        <div class="cs-quickstart-text"><strong>生成报告</strong>：在"评估报告"页面查看完整报告</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 数据统计卡片
    st.markdown("---")
    st.subheader("📈 当前数据统计")
    
    stats = st.session_state.database_manager.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="总会话数",
            value=stats.get("total_sessions", 0)
        )
    
    with col2:
        st.metric(
            label="平均得分",
            value=f"{stats.get('avg_score', 0):.1f}"
        )
    
    with col3:
        risk_dist = stats.get("risk_distribution", {})
        high_risk_count = risk_dist.get("high", 0)
        st.metric(
            label="高风险会话",
            value=high_risk_count
        )
    
    with col4:
        dialogues_count = len(st.session_state.dialogues)
        st.metric(
            label="对话数据",
            value=dialogues_count
        )
    
    # 风险分布图
    if stats.get("total_sessions", 0) > 0:
        st.markdown("---")
        st.subheader("风险等级分布")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_risk = create_risk_distribution_chart(stats)
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            if stats.get("group_distribution"):
                fig_group = create_group_distribution_chart(stats)
                st.plotly_chart(fig_group, use_container_width=True)


# ==================== 页面2: 实时监测 ====================
def render_monitoring_page():
    """渲染实时监测页面"""
    st.title("🎙️ 实时监测")
    
    st.markdown("""
    模拟智能家居环境中的实时对话监测。系统会逐句显示对话内容，
    并实时检测可能的认知风险信号。
    """)
    
    st.markdown("---")
    
    # 检查是否有对话数据
    if not st.session_state.dialogues:
        st.warning("⚠️ 请先在侧边栏生成对话数据")
        return
    
    # 对话选择
    col1, col2 = st.columns(2)
    
    with col1:
        # 按组别筛选
        group_filter = st.selectbox(
            "选择认知组别",
            ["全部", "HC (认知健康)", "MCI (轻度认知障碍)", "ED (早期痴呆)"]
        )
    
    with col2:
        # 按场景筛选
        scenario_filter = st.selectbox(
            "选择对话场景",
            ["全部"] + DIALOGUE_CONFIG["scenarios"]
        )
    
    
    # 筛选对话
    filtered_dialogues = filter_dialogues(group_filter, scenario_filter)
    
    if not filtered_dialogues:
        st.warning("没有符合条件的对话")
        return
    
    # 对话ID选择
    dialogue_ids = [d["id"] for d in filtered_dialogues]
    selected_id = st.selectbox(
        "选择对话ID",
        dialogue_ids,
        format_func=lambda x: f"对话 #{x}"
    )
    
    # 获取选中的对话
    selected_dialogue_data = next(d for d in filtered_dialogues if d["id"] == selected_id)
    
    if st.session_state.current_dialogue is None or st.session_state.current_dialogue["id"] != selected_id:
        st.session_state.current_dialogue = selected_dialogue_data
        st.session_state.monitoring_index = 0
        st.session_state.monitoring_active = False
        st.session_state.analysis_result = None
    
    st.markdown("---")
    
    # 显示对话信息 —— 徽章行
    col1, col2, col3 = st.columns(3)
    
    with col1:
        group_labels = {"HC": "认知健康", "MCI": "轻度认知障碍", "ED": "早期痴呆"}
        group_val = group_labels.get(selected_dialogue_data['group'], '未知')
        group_color = {"HC": "#10B981", "MCI": "#F59E0B", "ED": "#EF4444"}.get(selected_dialogue_data['group'], "#6B7280")
        st.markdown(f"""
        <div class="cs-info-badge">
            <div class="label">认知组别</div>
            <div class="value" style="color:{group_color};">● {group_val}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="cs-info-badge">
            <div class="label">对话场景</div>
            <div class="value">🏠 {selected_dialogue_data['scenario']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="cs-info-badge">
            <div class="label">对话轮数</div>
            <div class="value">💬 {len(selected_dialogue_data['dialogue'])} 轮</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 布局：左侧对话流，右侧事件检测
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("💬 对话流")
        
        # 对话显示区域
        dialogue_container = st.container()
        
        with dialogue_container:
            dialogue = selected_dialogue_data["dialogue"]
            display_index = st.session_state.monitoring_index
            
            # 显示已经播放的对话
            for i in range(min(display_index, len(dialogue))):
                turn = dialogue[i]
                render_dialogue_turn(turn, i)
        
        # 控制按钮
        st.markdown("---")
        
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
        
        with btn_col1:
            if st.button("▶️ 开始监测", use_container_width=True, disabled=st.session_state.monitoring_active):
                st.session_state.monitoring_active = True
                st.session_state.monitoring_index = 0
                st.session_state.analysis_result = None
                st.rerun()
        
        with btn_col2:
            if st.button("⏸️ 暂停", use_container_width=True, disabled=not st.session_state.monitoring_active):
                st.session_state.monitoring_active = False
                st.rerun()
        
        with btn_col3:
            if st.button("⏭️ 下一句", use_container_width=True):
                if st.session_state.monitoring_index < len(dialogue):
                    st.session_state.monitoring_index += 1
                    st.rerun()
        
        with btn_col4:
            if st.button("🔄 重置", use_container_width=True):
                st.session_state.monitoring_index = 0
                st.session_state.monitoring_active = False
                st.session_state.analysis_result = None
                st.rerun()
    
    with col_right:
        st.subheader("⚠️ 实时事件检测")
        
        # 事件检测区域
        events_container = st.container()
        
        with events_container:
            if st.session_state.monitoring_index > 0:
                # 分析当前对话片段
                current_dialogue = dialogue[:st.session_state.monitoring_index]
                events = detect_cognitive_events(current_dialogue)
                
                if events:
                    for event in events:
                        render_event_alert(event)
                else:
                    st.success("✅ 暂未检测到异常")
            else:
                st.info("等待开始监测...")
    
    # 自动播放逻辑
    if st.session_state.monitoring_active:
        if st.session_state.monitoring_index < len(dialogue):
            time.sleep(1.5)  # 每1.5秒播放一句
            st.session_state.monitoring_index += 1
            st.rerun()
        else:
            st.session_state.monitoring_active = False
            st.rerun()
    
    # 监测完成后的分析部分
    if st.session_state.monitoring_index >= len(dialogue) and not st.session_state.monitoring_active:
        st.markdown("""
        <div class="cs-completion-card">
            <div style="font-size:18px; font-weight:700; color:#4F46E5; margin-bottom:6px;">
                ✅ 对话监测完成！
            </div>
            <div style="font-size:13.5px; color:#111827;">
                所有对话轮次已播放完毕，可点击下方按钮进行完整分析。
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 分析按钮
        if st.button("📊 查看完整分析", use_container_width=True, type="primary"):
            with st.spinner("正在分析对话..."):
                try:
                    session_id = analyze_and_save_dialogue(selected_dialogue_data)
                    
                    # 保存分析结果到会话状态
                    st.session_state.analysis_result = {
                        "session_id": session_id,
                        "scores": st.session_state.current_analysis["scores"],
                        "success": True
                    }
                    
                    st.rerun()
                    
                except Exception as e:
                    st.session_state.analysis_result = {
                        "success": False,
                        "error": str(e)
                    }
                    st.rerun()
        
        # 显示分析结果
        if st.session_state.analysis_result:
            if st.session_state.analysis_result["success"]:
                st.success("✅ 分析完成！")
                
                result = st.session_state.analysis_result
                st.info(f"**会话ID**: {result['session_id']}")
                
                # 显示评分
                scores = result["scores"]
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("总分", f"{scores['total_score']:.1f}")
                with col_b:
                    risk_labels = {"low": "低风险", "medium": "中风险", "high": "高风险"}
                    st.metric("风险等级", risk_labels.get(scores['risk_level'], '未知'))
                with col_c:
                    st.metric("记忆力", f"{scores['memory']:.1f}")
                
                st.success("💡 请点击左侧导航切换到'分析仪表板'或'评估报告'页面查看详细结果")
                
                # 清除结果按钮
                if st.button("🔄 开始新的监测"):
                    st.session_state.analysis_result = None
                    st.session_state.monitoring_index = 0
                    st.rerun()
            else:
                st.error(f"❌ 分析失败: {st.session_state.analysis_result['error']}")
        
        # 调试信息
        with st.expander("🔍 数据库状态"):
            db = st.session_state.database_manager
            stats = db.get_statistics()
            st.json(stats)


def filter_dialogues(group_filter: str, scenario_filter: str):
    """筛选对话"""
    dialogues = st.session_state.dialogues
    
    # 按组别筛选
    if group_filter != "全部":
        group_code = group_filter.split()[0]  # 提取 HC/MCI/ED
        dialogues = [d for d in dialogues if d["group"] == group_code]
    
    # 按场景筛选
    if scenario_filter != "全部":
        dialogues = [d for d in dialogues if d["scenario"] == scenario_filter]
    
    return dialogues


def render_dialogue_turn(turn: dict, index: int):
    """渲染单轮对话"""
    speaker = turn["speaker"]
    text = turn["text"]
    
    if speaker == "elder":
        st.markdown(f"""
        <div class="cs-bubble-elder">
            <div class="cs-bubble-speaker" style="color:#4F46E5;">
                <span style="background:#4F46E5;color:#fff;border-radius:50%;width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-size:13px;">👴</span>
                老人
                <span style="font-size:11px;color:#6B7280;font-weight:400;margin-left:4px;">#{index+1}</span>
            </div>
            <div class="cs-bubble-text" style="color:#111827;">
                {text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="cs-bubble-family">
            <div class="cs-bubble-speaker" style="color:#0EA5E9;">
                <span style="background:#0EA5E9;color:#fff;border-radius:50%;width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-size:13px;">👨‍👩‍👧</span>
                家人
                <span style="font-size:11px;color:#6B7280;font-weight:400;margin-left:4px;">#{index+1}</span>
            </div>
            <div class="cs-bubble-text" style="color:#111827;">
                {text}
            </div>
        </div>
        """, unsafe_allow_html=True)


def detect_cognitive_events(dialogue: list) -> list:
    """检测认知事件"""
    events = []
    
    # 提取老人的发言
    elder_utterances = [turn["text"] for turn in dialogue if turn["speaker"] == "elder"]
    
    if not elder_utterances:
        return events
    
    # 合并所有发言
    full_text = " ".join(elder_utterances)
    
    # 1. 检测模糊代词使用
    vague_pronouns = ["那个", "这个", "那", "这", "它", "他", "她"]
    vague_count = sum(full_text.count(p) for p in vague_pronouns)
    if vague_count > 5:
        events.append({
            "type": "vague_reference",
            "severity": "high" if vague_count > 10 else "medium",
            "description": f"频繁使用模糊代词 ({vague_count}次)",
            "suggestion": "可能存在词汇提取困难或命名障碍"
        })
    
    # 2. 检测话语重复
    if len(elder_utterances) >= 3:
        repeated_count = 0
        for i in range(len(elder_utterances) - 1):
            for j in range(i + 1, len(elder_utterances)):
                # 计算相似度
                words_i = set(elder_utterances[i].split())
                words_j = set(elder_utterances[j].split())
                if len(words_i & words_j) / max(len(words_i), len(words_j)) > 0.7:
                    repeated_count += 1
                    break
        
        if repeated_count > 0:
            events.append({
                "type": "repetition",
                "severity": "high" if repeated_count > 2 else "medium",
                "description": f"检测到话语重复 ({repeated_count}次)",
                "suggestion": "可能存在短期记忆问题或思维固着"
            })
    
    # 3. 检测时间定向混淆
    time_words = ["昨天", "今天", "明天", "前天", "后天", "早上", "中午", "下午", "晚上"]
    time_mentions = [w for w in time_words if w in full_text]
    
    # 检测矛盾的时间表达
    contradictions = [
        ("昨天", "明天"),
        ("早上", "晚上"),
        ("今天", "昨天")
    ]
    
    has_contradiction = False
    for word1, word2 in contradictions:
        if word1 in full_text and word2 in full_text:
            # 检查是否在同一句话中
            for utterance in elder_utterances:
                if word1 in utterance and word2 in utterance:
                    has_contradiction = True
                    break
    
    if has_contradiction or len(time_mentions) > 4:
        events.append({
            "type": "temporal_confusion",
            "severity": "high" if has_contradiction else "medium",
            "description": "检测到时间定向混淆",
            "suggestion": "需要关注时间感知和定向能力"
        })
    
    # 4. 检测句子长度异常（过短可能表示表达困难）
    avg_length = sum(len(u) for u in elder_utterances) / len(elder_utterances)
    if avg_length < 10:
        events.append({
            "type": "short_utterance",
            "severity": "medium",
            "description": f"句子平均长度过短 ({avg_length:.1f}字)",
            "suggestion": "可能存在语言表达困难或词汇贫乏"
        })
    
    # 5. 检测填充词过度使用
    filler_words = ["嗯", "啊", "呃", "哦", "唉", "哎", "那个", "这个"]
    filler_count = sum(full_text.count(w) for w in filler_words)
    total_chars = len(full_text)
    
    if total_chars > 0 and filler_count / total_chars > 0.1:
        events.append({
            "type": "excessive_fillers",
            "severity": "medium",
            "description": f"填充词使用频繁 ({filler_count}次)",
            "suggestion": "可能存在词语提取困难或思维不流畅"
        })
    
    # 6. 检测问题重复询问
    question_marks = full_text.count("？") + full_text.count("?")
    if question_marks > 3:
        # 检查是否有相似的问题
        questions = [u for u in elder_utterances if "？" in u or "?" in u]
        if len(questions) >= 2:
            for i in range(len(questions) - 1):
                for j in range(i + 1, len(questions)):
                    if questions[i][:5] == questions[j][:5]:  # 简单的相似度检测
                        events.append({
                            "type": "repeated_questions",
                            "severity": "high",
                            "description": "检测到重复提问",
                            "suggestion": "可能存在记忆保持困难"
                        })
                        break
    
    # 7. 检测话题偏离
    if len(elder_utterances) >= 5:
        # 简单检测：检查前后句子的词汇重叠
        coherence_scores = []
        for i in range(len(elder_utterances) - 1):
            words_current = set(elder_utterances[i].split())
            words_next = set(elder_utterances[i + 1].split())
            overlap = len(words_current & words_next)
            total = len(words_current | words_next)
            if total > 0:
                coherence_scores.append(overlap / total)
        
        if coherence_scores:
            avg_coherence = sum(coherence_scores) / len(coherence_scores)
            if avg_coherence < 0.2:
                events.append({
                    "type": "topic_drift",
                    "severity": "medium",
                    "description": "检测到话题连贯性较差",
                    "suggestion": "可能存在注意力分散或逻辑思维困难"
                })
    
    # 8. 检测否定词过度使用（可能表示困惑或不确定）
    negative_words = ["不", "没", "不是", "不对", "不知道", "忘了"]
    negative_count = sum(full_text.count(w) for w in negative_words)
    if negative_count > 5:
        events.append({
            "type": "excessive_negation",
            "severity": "low",
            "description": f"频繁使用否定词 ({negative_count}次)",
            "suggestion": "可能表示不确定或记忆困难"
        })
    
    return events


def render_event_alert(event: dict):
    """渲染事件警报"""
    severity_colors = {
        "low": "#10B981",
        "medium": "#F59E0B",
        "high": "#EF4444"
    }
    
    severity_labels = {
        "low": "低",
        "medium": "中",
        "high": "高"
    }
    
    color = severity_colors.get(event["severity"], "#6b7280")
    label = severity_labels.get(event["severity"], "未知")
    sev_class = f"cs-event-{event['severity']}"
    
    sev_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(event["severity"], "⚪")
    
    st.markdown(f"""
    <div class="cs-event {sev_class}">
        <div class="cs-event-title" style="color:{color};">
            {sev_icon} {event['description']}
            <span style="font-size:11px; font-weight:500; background:{color}22; color:{color};
                         padding:2px 7px; border-radius:999px; margin-left:6px;">
                风险：{label}
            </span>
        </div>
        <div class="cs-event-hint">💡 {event['suggestion']}</div>
    </div>
    """, unsafe_allow_html=True)


def analyze_and_save_dialogue(dialogue_data: dict) -> int:
    """分析并保存对话"""
    try:
        # 执行语言分析
        analyzer = st.session_state.linguistic_analyzer
        features = analyzer.analyze_dialogue(dialogue_data["dialogue"])
        
        # 计算认知评分
        scorer = st.session_state.cognitive_scorer
        scores = scorer.calculate_scores(features)
        
        # 保存到数据库
        db = st.session_state.database_manager
        session_name = f"监测_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_id = db.save_session(
            session_name=session_name,
            dialogue=dialogue_data["dialogue"],
            features=features,
            scores=scores,
            dialogue_id=dialogue_data.get("id"),
            group_type=dialogue_data.get("group"),
            scenario=dialogue_data.get("scenario")
        )
        
        # 验证保存
        saved_data = db.load_session(session_id)
        if not saved_data:
            raise Exception(f"数据保存验证失败：无法读取会话 {session_id}")
        
        # 保存到会话状态
        st.session_state.current_analysis = {
            "session_id": session_id,
            "features": features,
            "scores": scores,
            "dialogue": dialogue_data
        }
        
        return session_id
    
    except Exception as e:
        import traceback
        error_msg = f"保存失败: {str(e)}\n{traceback.format_exc()}"
        raise Exception(error_msg)


# ==================== 页面3: 分析仪表板 ====================
def render_analytics_page():
    """渲染分析仪表板页面"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("📈 分析仪表板")
    
    with col2:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    st.markdown("查看详细的认知评分和语言特征分析。")
    
    # 调试信息
    with st.expander("🔍 调试信息", expanded=False):
        db = st.session_state.database_manager
        stats = db.get_statistics()
        
        st.write("**数据库状态**")
        st.json({
            "数据库路径": db.db_path,
            "总会话数": stats.get("total_sessions", 0),
            "平均得分": stats.get("avg_score", 0),
            "风险分布": stats.get("risk_distribution", {}),
            "组别分布": stats.get("group_distribution", {})
        })
        
        # 显示最近的会话
        recent = db.get_recent_sessions(limit=5)
        if recent:
            st.write("**最近5次会话**")
            import pandas as pd
            df = pd.DataFrame(recent)
            st.dataframe(df[['id', 'session_name', 'risk_level', 'total_score']])
    
    st.markdown("---")
    
    # 获取所有会话
    db = st.session_state.database_manager
    sessions = db.get_all_sessions()
    
    if not sessions:
        st.warning("⚠️ 暂无分析数据")
        st.info("""
        **如何生成分析数据？**
        
        1. 前往 **🎙️ 实时监测** 页面
        2. 选择一个对话
        3. 点击 **▶️ 开始监测**
        4. 监测完成后，点击 **📊 查看完整分析**
        5. 等待分析完成（会显示会话ID）
        6. 返回本页面点击刷新按钮
        """)
        return
    
    # 会话选择
    session_options = {
        s["id"]: f"#{s['id']} - {s['session_name']} ({s['created_at']})"
        for s in sessions
    }

    selected_session_id = st.selectbox(
        "选择会话",
        options=list(session_options.keys()),
        format_func=lambda x: session_options[x]
    )
    
    # 加载会话数据
    session_data = db.load_session(selected_session_id)
    
    if not session_data:
        st.error("无法加载会话数据")
        return
    
    scores = session_data["scores"]
    features = session_data["features"]
    
    # 显示基本信息 —— 四格 metric
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总分", f"{scores.get('total_score', 0):.1f} 分")
    
    with col2:
        risk_level = scores.get('risk_level', 'unknown')
        risk_labels = {"low": "低风险", "medium": "中风险", "high": "高风险"}
        risk_colors = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        st.metric("风险等级", f"{risk_colors.get(risk_level, '⚪')} {risk_labels.get(risk_level, '未知')}")
    
    with col3:
        if session_data.get("group_type"):
            group_labels = {"HC": "认知健康", "MCI": "轻度认知障碍", "ED": "早期痴呆"}
            st.metric("认知组别", group_labels.get(session_data["group_type"], "未知"))
    
    with col4:
        if session_data.get("scenario"):
            st.metric("对话场景", session_data["scenario"])
    
    st.markdown("---")
    
    # 五维评分可视化
    st.subheader("🎯 五维认知评分")
    
    tab1, tab2 = st.tabs(["雷达图", "柱状图"])
    
    with tab1:
        fig_radar = create_radar_chart(scores)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with tab2:
        fig_bar = create_score_comparison_chart(scores)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # 语言特征分析
    st.subheader("🔍 语言特征分析")
    
    # 生成特征解释
    report_gen = st.session_state.report_generator
    feature_explanations = report_gen._generate_feature_explanations(features)
    
    # 创建特征表格
    feature_df = create_feature_table(features, feature_explanations)
    
    st.dataframe(
        feature_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "特征名称": st.column_config.TextColumn("特征名称", width="medium"),
            "数值": st.column_config.TextColumn("数值", width="small"),
            "解释": st.column_config.TextColumn("解释", width="medium"),
            "临床意义": st.column_config.TextColumn("临床意义", width="large")
        }
    )
    
    st.markdown("---")
    
    # 历史趋势
    st.subheader("📊 历史趋势")
    
    recent_sessions = db.get_recent_sessions(limit=20)
    
    if len(recent_sessions) > 1:
        fig_trend = create_trend_chart(recent_sessions)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("需要至少2次会话才能显示趋势图")
    
    st.markdown("---")
    
    # 对话内容
    with st.expander("💬 查看对话内容"):
        dialogue = session_data.get("dialogue", [])
        dialogue_html = format_dialogue_for_display(dialogue)
        st.markdown(dialogue_html, unsafe_allow_html=True)


# ==================== 页面4: 评估报告 ====================
def render_report_page():
    """渲染评估报告页面"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("📄 认知健康评估报告")
    
    with col2:
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    st.markdown("生成专业的认知评估报告。")
    
    st.markdown("---")
    
    # 获取所有会话
    db = st.session_state.database_manager
    sessions = db.get_all_sessions()
    
    if not sessions:
        st.warning("⚠️ 暂无评估数据")
        st.info("""
        **如何生成评估数据？**
        
        1. 前往 **🎙️ 实时监测** 页面
        2. 选择一个对话
        3. 点击 **▶️ 开始监测**
        4. 监测完成后，点击 **📊 查看完整分析**
        5. 返回本页面点击刷新按钮
        """)
        return
    
    # 会话选择
    session_options = {s["id"]: f"#{s['id']} - {s['session_name']}" for s in sessions}
    selected_session_id = st.selectbox(
        "选择会话",
        options=list(session_options.keys()),
        format_func=lambda x: session_options[x]
    )
    
    # 加载会话数据
    session_data = db.load_session(selected_session_id)
    
    if not session_data:
        st.error("无法加载会话数据")
        return
    
    # 生成报告
    report_gen = st.session_state.report_generator
    report = report_gen.generate_report(
        session_name=session_data["session_name"],
        dialogue=session_data["dialogue"],
        features=session_data["features"],
        scores=session_data["scores"],
        group_type=session_data.get("group_type"),
        scenario=session_data.get("scenario")
    )
    
    # 显示报告
    st.markdown("---")
    
    # 报告标题 —— 封面卡片
    st.markdown(f"""
    <div class="cs-report-header">
        <div style="font-size:11px; text-transform:uppercase; letter-spacing:2px;
                    opacity:0.8; margin-bottom:10px; font-weight:600;">
            📄 COGNITIVE HEALTH ASSESSMENT REPORT
        </div>
        <h2>{report['title']}</h2>
        <div class="subtitle">
            🕐 生成时间：{report['generated_at']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 执行摘要
    st.subheader("📋 执行摘要")
    st.markdown(f"""
    <div class="cs-card" style="border-left: 4px solid #4F46E5;">
        <div style="font-size:14.5px; line-height:1.8; color:#111827;">
            {report["summary"]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 认知评分
    st.subheader("🎯 认知评分结果")
    
    scores = report["scores"]
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("记忆力", f"{scores['memory']:.1f}")
    
    with col2:
        st.metric("计划能力", f"{scores['planning']:.1f}")
    
    with col3:
        st.metric("回忆能力", f"{scores['recall']:.1f}")
    
    with col4:
        st.metric("连贯性", f"{scores['coherence']:.1f}")
    
    with col5:
        st.metric("时间定向", f"{scores['temporal_orientation']:.1f}")
    
    with col6:
        st.metric("**总分**", f"**{scores['total_score']:.1f}**")
    
    # 雷达图
    fig_radar = create_radar_chart(scores)
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("---")
    
    # 风险评估
    st.subheader("⚠️ 风险评估")
    
    risk_assessment = report["risk_assessment"]
    
    risk_colors = {
        "低风险": "success",
        "中风险": "warning",
        "高风险": "error"
    }
    
    risk_level_label = risk_assessment["level"]
    message_type = risk_colors.get(risk_level_label, "info")
    
    # 风险等级图标与颜色
    risk_icon_map = {"低风险": "🟢", "中风险": "🟡", "高风险": "🔴"}
    risk_css_map  = {"低风险": "low", "中风险": "medium", "高风险": "high"}
    r_icon = risk_icon_map.get(risk_level_label, "⚪")
    r_css  = risk_css_map.get(risk_level_label, "low")
    
    st.markdown(f"""
    <div class="cs-risk-card {r_css}">
        <div class="cs-risk-level">{r_icon} {risk_level_label}</div>
        <div class="cs-risk-desc">{risk_assessment['description']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if message_type == "success":
        st.success(f"**{risk_level_label}**: {risk_assessment['description']}")
    elif message_type == "warning":
        st.warning(f"**{risk_level_label}**: {risk_assessment['description']}")
    else:
        st.error(f"**{risk_level_label}**: {risk_assessment['description']}")
    
    st.markdown("**详细说明:**")
    for detail in risk_assessment["details"]:
        st.markdown(f"- {detail}")
    
    st.markdown("---")
    
    # 语言特征解释
    st.subheader("🔍 语言特征解释")
    
    for explanation in report["feature_explanations"]:
        with st.expander(f"**{explanation['feature']}**: {explanation['value']}"):
            st.markdown(f"**解释**: {explanation['interpretation']}")
            st.markdown(f"**临床意义**: {explanation['importance']}")
    
    st.markdown("---")
    
    # 建议 —— 视觉化列表
    st.subheader("💡 专业建议")
    
    rec_items_html = ""
    for i, recommendation in enumerate(report["recommendations"], 1):
        rec_items_html += f"""
        <div class="cs-rec-item">
            <div class="cs-rec-num">{i}</div>
            <div class="cs-rec-text">{recommendation}</div>
        </div>
        """
    st.markdown(rec_items_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 对话摘录
    st.subheader("💬 对话摘录")
    
    dialogue_excerpt = report["dialogue_excerpt"]
    dialogue_html = format_dialogue_for_display(dialogue_excerpt)
    st.markdown(dialogue_html, unsafe_allow_html=True)
    
    # 修复：dialogue_turns 是整数，不需要 len()
    total_turns = report["metadata"]["dialogue_turns"]
    if total_turns > len(dialogue_excerpt):
        st.caption(f"（显示前{len(dialogue_excerpt)}轮，共{total_turns}轮）")
    
    st.markdown("---")
    
    # 报告元数据
    with st.expander("ℹ️ 报告元数据"):
        st.json(report["metadata"])


# ==================== 主函数 ====================
def main():
    """主函数"""
    # 渲染侧边栏并获取当前页面
    current_page = render_sidebar()
    
    # 根据选择渲染对应页面
    if current_page == "📊 系统概览":
        render_overview_page()
    elif current_page == "🎙️ 实时监测":
        render_monitoring_page()
    elif current_page == "📈 分析仪表板":
        render_analytics_page()
    elif current_page == "📄 评估报告":
        render_report_page()


if __name__ == "__main__":
    main()
