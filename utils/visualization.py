"""
可视化工具模块
使用Plotly生成交互式图表
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List


def create_radar_chart(scores: Dict) -> go.Figure:
    """
    创建五维认知评分雷达图
    
    Args:
        scores: 认知评分字典
    
    Returns:
        Plotly图表对象
    """
    # 维度标签（中文）
    categories = [
        '记忆力<br>Memory',
        '计划能力<br>Planning',
        '回忆能力<br>Recall',
        '连贯性<br>Coherence',
        '时间定向<br>Temporal'
    ]
    
    # 提取分数
    values = [
        scores.get('memory', 0),
        scores.get('planning', 0),
        scores.get('recall', 0),
        scores.get('coherence', 0),
        scores.get('temporal_orientation', 0)
    ]
    
    # 创建雷达图
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='认知评分',
        line=dict(color='rgb(99, 110, 250)', width=2),
        fillcolor='rgba(99, 110, 250, 0.3)'
    ))
    
    # 添加参考线（正常水平：80分）
    fig.add_trace(go.Scatterpolar(
        r=[80, 80, 80, 80, 80],
        theta=categories,
        fill='toself',
        name='正常参考线',
        line=dict(color='rgba(0, 200, 0, 0.5)', width=1, dash='dash'),
        fillcolor='rgba(0, 200, 0, 0.1)'
    ))
    
    # 布局设置
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=12),
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color='#333')
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=500,
        margin=dict(l=80, r=80, t=40, b=80)
    )
    
    return fig


def create_trend_chart(sessions: List[Dict]) -> go.Figure:
    """
    创建历史趋势折线图
    
    Args:
        sessions: 会话列表
    
    Returns:
        Plotly图表对象
    """
    if not sessions:
        # 返回空图表
        fig = go.Figure()
        fig.add_annotation(
            text="暂无历史数据",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=400)
        return fig
    
    # 准备数据
    df = pd.DataFrame(sessions)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at')
    
    # 创建折线图
    fig = go.Figure()
    
    # 总分趋势线
    fig.add_trace(go.Scatter(
        x=df['created_at'],
        y=df['total_score'],
        mode='lines+markers',
        name='总分',
        line=dict(color='rgb(99, 110, 250)', width=3),
        marker=dict(size=8, symbol='circle'),
        hovertemplate='<b>时间</b>: %{x}<br><b>总分</b>: %{y:.1f}<extra></extra>'
    ))
    
    # 添加风险等级参考线
    fig.add_hline(
        y=80, 
        line_dash="dash", 
        line_color="green",
        annotation_text="低风险阈值 (80分)",
        annotation_position="right"
    )
    
    fig.add_hline(
        y=60, 
        line_dash="dash", 
        line_color="orange",
        annotation_text="中风险阈值 (60分)",
        annotation_position="right"
    )
    
    # 布局设置
    fig.update_layout(
        title="认知评分历史趋势",
        xaxis_title="时间",
        yaxis_title="总分",
        yaxis=dict(range=[0, 105]),
        hovermode='x unified',
        height=400,
        margin=dict(l=60, r=60, t=60, b=60)
    )
    
    return fig


def create_feature_table(features: Dict, feature_explanations: List[Dict]) -> pd.DataFrame:
    """
    创建语言特征表格
    
    Args:
        features: 语言特征字典
        feature_explanations: 特征解释列表
    
    Returns:
        Pandas DataFrame
    """
    # 构建表格数据
    table_data = []
    
    for explanation in feature_explanations:
        table_data.append({
            "特征名称": explanation["feature"],
            "数值": explanation["value"],
            "解释": explanation["interpretation"],
            "临床意义": explanation["importance"]
        })
    
    df = pd.DataFrame(table_data)
    
    return df


def create_risk_distribution_chart(statistics: Dict) -> go.Figure:
    """
    创建风险等级分布饼图
    
    Args:
        statistics: 统计数据
    
    Returns:
        Plotly图表对象
    """
    risk_dist = statistics.get("risk_distribution", {})
    
    if not risk_dist:
        # 返回空图表
        fig = go.Figure()
        fig.add_annotation(
            text="暂无数据",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=400)
        return fig
    
    # 准备数据
    labels_map = {
        "low": "低风险",
        "medium": "中风险",
        "high": "高风险"
    }
    
    colors_map = {
        "low": "#10b981",
        "medium": "#f59e0b",
        "high": "#ef4444"
    }
    
    labels = [labels_map.get(k, k) for k in risk_dist.keys()]
    values = list(risk_dist.values())
    colors = [colors_map.get(k, "#6b7280") for k in risk_dist.keys()]
    
    # 创建饼图
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.4,
        textinfo='label+percent',
        textfont=dict(size=14),
        hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="风险等级分布",
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


def create_group_distribution_chart(statistics: Dict) -> go.Figure:
    """
    创建认知组别分布柱状图
    
    Args:
        statistics: 统计数据
    
    Returns:
        Plotly图表对象
    """
    group_dist = statistics.get("group_distribution", {})
    
    if not group_dist:
        # 返回空图表
        fig = go.Figure()
        fig.add_annotation(
            text="暂无数据",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=400)
        return fig
    
    # 准备数据
    labels_map = {
        "HC": "认知健康 (HC)",
        "MCI": "轻度认知障碍 (MCI)",
        "ED": "早期痴呆 (ED)"
    }
    
    colors_map = {
        "HC": "#10b981",
        "MCI": "#f59e0b",
        "ED": "#ef4444"
    }
    
    groups = list(group_dist.keys())
    labels = [labels_map.get(g, g) for g in groups]
    values = list(group_dist.values())
    colors = [colors_map.get(g, "#6b7280") for g in groups]
    
    # 创建柱状图
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker=dict(color=colors),
        text=values,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>数量: %{y}<extra></extra>'
    )])
    
    fig.update_layout(
        title="认知组别分布",
        xaxis_title="组别",
        yaxis_title="数量",
        height=400,
        margin=dict(l=60, r=60, t=60, b=60)
    )
    
    return fig


def create_score_comparison_chart(scores: Dict) -> go.Figure:
    """
    创建五维评分对比柱状图
    
    Args:
        scores: 认知评分字典
    
    Returns:
        Plotly图表对象
    """
    # 维度标签
    dimensions = ['记忆力', '计划能力', '回忆能力', '连贯性', '时间定向']
    
    # 提取分数
    values = [
        scores.get('memory', 0),
        scores.get('planning', 0),
        scores.get('recall', 0),
        scores.get('coherence', 0),
        scores.get('temporal_orientation', 0)
    ]
    
    # 根据分数设置颜色
    colors = []
    for v in values:
        if v >= 80:
            colors.append('#10b981')  # 绿色
        elif v >= 60:
            colors.append('#f59e0b')  # 橙色
        else:
            colors.append('#ef4444')  # 红色
    
    # 创建柱状图
    fig = go.Figure(data=[go.Bar(
        x=dimensions,
        y=values,
        marker=dict(color=colors),
        text=[f'{v:.1f}' for v in values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>得分: %{y:.1f}<extra></extra>'
    )])
    
    # 添加参考线
    fig.add_hline(
        y=80, 
        line_dash="dash", 
        line_color="rgba(0, 200, 0, 0.5)",
        annotation_text="正常水平",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="五维认知评分对比",
        xaxis_title="认知维度",
        yaxis_title="得分",
        yaxis=dict(range=[0, 105]),
        height=400,
        margin=dict(l=60, r=60, t=60, b=60)
    )
    
    return fig


def format_dialogue_for_display(dialogue: List[Dict]) -> str:
    """
    格式化对话用于显示
    
    Args:
        dialogue: 对话列表
    
    Returns:
        格式化的HTML字符串
    """
    html_parts = []
    
    for i, turn in enumerate(dialogue, 1):
        speaker = turn["speaker"]
        text = turn["text"]
        
        if speaker == "elder":
            speaker_label = "👴 老人"
            color = "#3b82f6"
        else:
            speaker_label = "👨‍👩‍👧 家人"
            color = "#8b5cf6"
        
        html_parts.append(f"""
        <div style="margin-bottom: 15px; padding: 10px; border-left: 3px solid {color}; background-color: rgba(0,0,0,0.02); border-radius: 5px;">
            <div style="font-weight: bold; color: {color}; margin-bottom: 5px;">
                {speaker_label}
            </div>
            <div style="color: #333; line-height: 1.6;">
                {text}
            </div>
        </div>
        """)
    
    return "".join(html_parts)


def create_feature_heatmap(features_list: List[Dict]) -> go.Figure:
    """
    创建多个会话的特征热力图
    
    Args:
        features_list: 特征列表
    
    Returns:
        Plotly图表对象
    """
    if not features_list:
        fig = go.Figure()
        fig.add_annotation(
            text="暂无数据",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=400)
        return fig
    
    # 准备数据
    feature_names = [
        "词汇丰富度",
        "模糊代词率",
        "修复频率",
        "重复率",
        "连贯性",
        "时间混淆",
        "平均句长",
        "填充词率"
    ]
    
    feature_keys = [
        "vocabulary_richness",
        "vague_pronoun_ratio",
        "repair_frequency",
        "repetition_rate",
        "coherence_score",
        "temporal_confusion",
        "avg_utterance_length",
        "filler_word_ratio"
    ]
    
    # 构建矩阵
    data_matrix = []
    for features in features_list:
        row = [features.get(key, 0) for key in feature_keys]
        data_matrix.append(row)
    
    # 创建热力图
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=feature_names,
        y=[f"会话 {i+1}" for i in range(len(features_list))],
        colorscale='RdYlGn',
       hovertemplate='<b>%{y}</b><br>%{x}: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="语言特征热力图",
        height=max(400, len(features_list) * 40),
        margin=dict(l=100, r=60, t=60, b=100)
    )
    
    return fig