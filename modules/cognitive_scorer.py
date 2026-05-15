"""
认知评分模块
基于语言特征生成五维认知评分
"""

from typing import Dict
from config import SCORING_THRESHOLDS


class CognitiveScorer:
    """认知评分器"""
    
    def __init__(self):
        """初始化评分器"""
        self.thresholds = SCORING_THRESHOLDS
    
    def calculate_scores(self, features: Dict) -> Dict:
        """
        基于语言特征计算五维认知评分
        
        Args:
            features: 语言特征字典
        
        Returns:
            评分结果字典
        """
        # 计算五个维度的得分
        memory_score = self._calculate_memory_score(features)
        planning_score = self._calculate_planning_score(features)
        recall_score = self._calculate_recall_score(features)
        coherence_score = self._calculate_coherence_score(features)
        temporal_score = self._calculate_temporal_score(features)
        
        # 计算总分
        weights = self.thresholds["weights"]
        total_score = (
            memory_score * weights["memory"] +
            planning_score * weights["planning"] +
            recall_score * weights["recall"] +
            coherence_score * weights["coherence"] +
            temporal_score * weights["temporal_orientation"]
        )
        
        # 确定风险等级
        risk_level = self._determine_risk_level(total_score)
        
        return {
            "memory": round(memory_score, 1),
            "planning": round(planning_score, 1),
            "recall": round(recall_score, 1),
            "coherence": round(coherence_score, 1),
            "temporal_orientation": round(temporal_score, 1),
            "total_score": round(total_score, 1),
            "risk_level": risk_level
        }
    
    def _calculate_memory_score(self, features: Dict) -> float:
        """
        计算记忆力得分
        
        主要依据：
        - 重复率（越高越差）
        - 模糊代词使用率（越高越差）
        
        Args:
            features: 语言特征
        
        Returns:
            记忆力得分 (0-100)
        """
        base_score = 100.0
        
        # 重复率惩罚
        repetition_rate = features.get("repetition_rate", 0)
        if repetition_rate > 0.3:
            base_score -= 30
        elif repetition_rate > 0.2:
            base_score -= 20
        elif repetition_rate > 0.1:
            base_score -= 10
        
        # 模糊代词惩罚
        vague_ratio = features.get("vague_pronoun_ratio", 0)
        if vague_ratio > 0.15:
            base_score -= 25
        elif vague_ratio > 0.10:
            base_score -= 15
        elif vague_ratio > 0.05:
            base_score -= 8
        
        # 修复频率惩罚（轻微）
        repair_freq = features.get("repair_frequency", 0)
        if repair_freq > 0.5:
            base_score -= 10
        elif repair_freq > 0.3:
            base_score -= 5
        
        return max(0, min(100, base_score))
    
    def _calculate_planning_score(self, features: Dict) -> float:
        """
        计算计划能力得分
        
        主要依据：
        - 句子长度（过短可能表示表达困难）
        - 连贯性（逻辑能力）
        
        Args:
            features: 语言特征
        
        Returns:
            计划能力得分 (0-100)
        """
        base_score = 100.0
        
        # 句子长度评估
        avg_length = features.get("avg_utterance_length", 0)
        if avg_length < 10:
            base_score -= 25
        elif avg_length < 15:
            base_score -= 15
        elif avg_length < 20:
            base_score -= 5
        
        # 连贯性评估
        coherence = features.get("coherence_score", 0)
        if coherence < 0.3:
            base_score -= 30
        elif coherence < 0.5:
            base_score -= 20
        elif coherence < 0.7:
            base_score -= 10
        
        # 词汇丰富度（间接反映思维复杂度）
        vocab_richness = features.get("vocabulary_richness", 0)
        if vocab_richness < 0.3:
            base_score -= 15
        elif vocab_richness < 0.5:
            base_score -= 8
        
        return max(0, min(100, base_score))
    
    def _calculate_recall_score(self, features: Dict) -> float:
        """
        计算回忆能力得分
        
        主要依据：
        - 词汇丰富度（能否准确提取词汇）
        - 修复频率（是否需要频繁纠正）
        
        Args:
            features: 语言特征
        
        Returns:
            回忆能力得分 (0-100)
        """
        base_score = 100.0
        
        # 词汇丰富度
        vocab_richness = features.get("vocabulary_richness", 0)
        if vocab_richness < 0.3:
            base_score -= 30
        elif vocab_richness < 0.5:
            base_score -= 20
        elif vocab_richness < 0.6:
            base_score -= 10
        
        # 修复频率
        repair_freq = features.get("repair_frequency", 0)
        if repair_freq > 0.6:
            base_score -= 25
        elif repair_freq > 0.4:
            base_score -= 15
        elif repair_freq > 0.2:
            base_score -= 8
        
        # 模糊代词（词汇提取困难）
        vague_ratio = features.get("vague_pronoun_ratio", 0)
        if vague_ratio > 0.15:
            base_score -= 20
        elif vague_ratio > 0.10:
            base_score -= 10
        
        return max(0, min(100, base_score))
    
    def _calculate_coherence_score(self, features: Dict) -> float:
        """
        计算连贯性得分
        
        主要依据：
        - 语义连贯性
        - 重复率（过高表示思维卡顿）
        
        Args:
            features: 语言特征
        
        Returns:
            连贯性得分 (0-100)
        """
        base_score = 100.0
        
        # 连贯性直接映射
        coherence = features.get("coherence_score", 0)
        if coherence < 0.3:
            base_score -= 40
        elif coherence < 0.5:
            base_score -= 25
        elif coherence < 0.7:
            base_score -= 15
        
        # 重复率惩罚
        repetition_rate = features.get("repetition_rate", 0)
        if repetition_rate > 0.3:
            base_score -= 25
        elif repetition_rate > 0.2:
            base_score -= 15
        elif repetition_rate > 0.1:
            base_score -= 8
        
        # 填充词过多表示思维不流畅
        filler_ratio = features.get("filler_word_ratio", 0)
        if filler_ratio > 0.1:
            base_score -= 15
        elif filler_ratio > 0.05:
            base_score -= 8
        
        return max(0, min(100, base_score))
    
    def _calculate_temporal_score(self, features: Dict) -> float:
        """
        计算时间定向能力得分
        
        主要依据：
        - 时间混淆程度
        
        Args:
            features: 语言特征
        
        Returns:
            时间定向得分 (0-100)
        """
        base_score = 100.0
        
        # 时间混淆直接惩罚
        temporal_confusion = features.get("temporal_confusion", 0)
        if temporal_confusion > 0.5:
            base_score -= 50
        elif temporal_confusion > 0.3:
            base_score -= 35
        elif temporal_confusion > 0.1:
            base_score -= 20
        elif temporal_confusion > 0:
            base_score -= 10
        
        return max(0, min(100, base_score))
    
    def _determine_risk_level(self, total_score: float) -> str:
        """
        根据总分确定风险等级
        
        Args:
            total_score: 总分
        
        Returns:
            风险等级 (low/medium/high)
        """
        thresholds = self.thresholds["risk_levels"]
        
        if total_score >= thresholds["low"]:
            return "low"
        elif total_score >= thresholds["medium"]:
            return "medium"
        else:
            return "high"
    
    def get_risk_level_description(self, risk_level: str) -> Dict:
        """
        获取风险等级的详细描述
        
        Args:
            risk_level: 风险等级
        
        Returns:
            描述字典
        """
        descriptions = {
            "low": {
                "label": "低风险",
                "color": "green",
                "description": "认知功能正常，表现出与年龄相符的认知水平。",
                "recommendation": "保持健康的生活方式，定期进行认知活动。"
            },
            "medium": {
                "label": "中风险",
                "color": "orange",
                "description": "存在轻度认知下降迹象，建议进一步评估。",
                "recommendation": "建议进行专业认知评估（如MoCA测试），增加认知训练活动。"
            },
            "high": {
                "label": "高风险",
                "color": "red",
                "description": "认知功能明显下降，强烈建议就医。",
                "recommendation": "请尽快前往医院神经内科或记忆门诊进行全面评估。"
            }
        }
        
        return descriptions.get(risk_level, descriptions["medium"])