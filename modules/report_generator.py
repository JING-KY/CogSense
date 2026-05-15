"""
报告生成模块
生成专业的认知评估报告
"""

from datetime import datetime
from typing import Dict, List


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        """初始化报告生成器"""
        pass
    
    def generate_report(
        self,
        session_name: str,
        dialogue: List[Dict],
        features: Dict,
        scores: Dict,
        group_type: str = None,
        scenario: str = None
    ) -> Dict:
        """
        生成完整的评估报告
        
        Args:
            session_name: 会话名称
            dialogue: 对话数据
            features: 语言特征
            scores: 认知评分
            group_type: 认知组别（可选）
            scenario: 场景（可选）
        
        Returns:
            报告数据字典
        """
        report = {
            "title": "CogSense 认知健康评估报告",
            "session_name": session_name,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": self._generate_summary(dialogue, scores),
            "scores": scores,
            "features": features,
            "feature_explanations": self._generate_feature_explanations(features),
            "risk_assessment": self._generate_risk_assessment(scores),
            "recommendations": self._generate_recommendations(scores),
            "dialogue_excerpt": self._extract_dialogue_excerpt(dialogue),
            "metadata": {
                "group_type": group_type,
                "scenario": scenario,
                "dialogue_turns": len(dialogue)
            }
        }
        
        return report
    
    def _generate_summary(self, dialogue: List[Dict], scores: Dict) -> str:
        """
        生成对话摘要
        
        Args:
            dialogue: 对话数据
            scores: 认知评分
        
        Returns:
            摘要文本
        """
        total_turns = len(dialogue)
        elder_turns = len([t for t in dialogue if t["speaker"] == "elder"])
        total_score = scores.get("total_score", 0)
        risk_level = scores.get("risk_level", "unknown")
        
        risk_labels = {
            "low": "低风险",
            "medium": "中风险",
            "high": "高风险"
        }
        
        summary = f"""
本次评估基于一段包含{total_turns}轮对话的家庭交流场景，其中被评估者发言{elder_turns}次。
通过对语言特征的多维度分析，系统计算出综合认知得分为{total_score:.1f}分（满分100分），
风险等级评定为：**{risk_labels.get(risk_level, '未知')}**。
        """.strip()
        
        return summary
    
    def _generate_feature_explanations(self, features: Dict) -> List[Dict]:
        """
        生成特征解释
        
        Args:
            features: 语言特征
        
        Returns:
            特征解释列表
        """
        explanations = []
        
        # 词汇丰富度
        vocab_richness = features.get("vocabulary_richness", 0)
        explanations.append({
            "feature": "词汇丰富度",
            "value": f"{vocab_richness:.3f}",
            "interpretation": self._interpret_vocab_richness(vocab_richness),
            "importance": "反映词汇提取能力和语言表达多样性"
        })
        
        # 模糊代词使用率
        vague_ratio = features.get("vague_pronoun_ratio", 0)
        explanations.append({
            "feature": "模糊代词使用率",
            "value": f"{vague_ratio:.3f}",
            "interpretation": self._interpret_vague_ratio(vague_ratio),
            "importance": "过度使用可能表示词汇提取困难或记忆问题"
        })
        
        # 话语重复率
        repetition_rate = features.get("repetition_rate", 0)
        explanations.append({
            "feature": "话语重复率",
            "value": f"{repetition_rate:.3f}",
            "interpretation": self._interpret_repetition(repetition_rate),
            "importance": "反映短期记忆和思维流畅性"
        })
        
        # 语义连贯性
        coherence = features.get("coherence_score", 0)
        explanations.append({
            "feature": "语义连贯性",
            "value": f"{coherence:.3f}",
            "interpretation": self._interpret_coherence(coherence),
            "importance": "反映逻辑思维和话题维持能力"
        })
        
        # 时间混淆程度
        temporal_confusion = features.get("temporal_confusion", 0)
        explanations.append({
            "feature": "时间混淆程度",
            "value": f"{temporal_confusion:.3f}",
            "interpretation": self._interpret_temporal(temporal_confusion),
            "importance": "时间定向障碍是认知下降的重要指标"
        })
        
        return explanations
    
    def _interpret_vocab_richness(self, value: float) -> str:
        """解释词汇丰富度"""
        if value >= 0.6:
            return "优秀 - 词汇使用丰富多样"
        elif value >= 0.5:
            return "良好 - 词汇使用较为丰富"
        elif value >= 0.4:
            return "一般 - 词汇使用有一定重复"
        else:
            return "较低 - 词汇使用单一，可能存在提取困难"
    
    def _interpret_vague_ratio(self, value: float) -> str:
        """解释模糊代词使用率"""
        if value <= 0.05:
            return "正常 - 指代清晰明确"
        elif value <= 0.10:
            return "轻微 - 偶有模糊指代"
        elif value <= 0.15:
            return "中度 - 较频繁使用模糊代词"
        else:
            return "较高 - 频繁使用模糊代词，指代不清"
    
    def _interpret_repetition(self, value: float) -> str:
        """解释重复率"""
        if value <= 0.1:
            return "正常 - 话语基本不重复"
        elif value <= 0.2:
            return "轻微 - 偶有重复表达"
        elif value <= 0.3:
            return "中度 - 较明显的重复现象"
        else:
            return "较高 - 频繁重复，可能存在记忆问题"
    
    def _interpret_coherence(self, value: float) -> str:
        """解释连贯性"""
        if value >= 0.7:
            return "优秀 - 逻辑清晰，前后连贯"
        elif value >= 0.5:
            return "良好 - 基本连贯，偶有跳跃"
        elif value >= 0.3:
            return "一般 - 连贯性较差，话题易偏离"
        else:
            return "较差 - 逻辑混乱，难以维持话题"
    
    def _interpret_temporal(self, value: float) -> str:
        """解释时间混淆"""
        if value == 0:
            return "正常 - 时间定向清晰"
        elif value <= 0.1:
            return "轻微 - 偶有时间表达不准确"
        elif value <= 0.3:
            return "中度 - 存在时间混淆现象"
        else:
            return "较严重 - 明显的时间定向障碍"
    
    def _generate_risk_assessment(self, scores: Dict) -> Dict:
        """
        生成风险评估
        
        Args:
            scores: 认知评分
        
        Returns:
            风险评估字典
        """
        risk_level = scores.get("risk_level", "unknown")
        total_score = scores.get("total_score", 0)
        
        assessments = {
            "low": {
                "level": "低风险",
                "description": "认知功能处于正常范围，表现出与年龄相符的认知水平。",
                "details": [
                    "各项认知指标均在正常范围内",
                    "语言表达流畅，逻辑清晰",
                    "记忆力和定向力良好",
                    "无明显认知下降迹象"
                ]
            },
            "medium": {
                "level": "中风险",
                "description": "存在轻度认知下降迹象，部分指标低于正常水平，建议进一步评估。",
                "details": [
                    "部分认知指标出现下降",
                    "可能存在轻微的记忆或语言问题",
                    "建议进行专业认知评估",
                    "需要关注认知功能变化"
                ]
            },
            "high": {
                "level": "高风险",
                "description": "认知功能明显下降，多项指标显著低于正常水平，强烈建议就医。",
                "details": [
                    "多项认知指标明显异常",
                    "存在明显的记忆、语言或定向障碍",
                    "强烈建议尽快就医",
                    "需要进行全面的神经心理评估"
                ]
            }
        }
        
        assessment = assessments.get(risk_level, assessments["medium"])
        assessment["total_score"] = total_score
        
        return assessment
    
    def _generate_recommendations(self, scores: Dict) -> List[str]:
        """
        生成建议
        
        Args:
            scores: 认知评分
        
        Returns:
            建议列表
        """
        risk_level = scores.get("risk_level", "unknown")
        
        recommendations = {
            "low": [
                "保持健康的生活方式，包括规律作息、均衡饮食和适度运动",
                "定期进行认知活动，如阅读、下棋、学习新技能等",
                "保持社交活动，与家人朋友多交流",
                "每年进行一次认知健康筛查",
                "如有任何认知变化，及时咨询医生"
            ],
            "medium": [
                "建议前往医院进行专业认知评估（如MoCA、MMSE测试）",
                "增加认知训练活动的频率和强度",
                "保持规律的生活作息，确保充足睡眠",
                "控制慢性疾病（如高血压、糖尿病）",
                "每3-6个月进行一次认知功能复查",
                "家人应多关注并记录认知变化情况"
            ],
            "high": [
                "**请尽快前往医院神经内科或记忆门诊就诊**",
                "进行全面的神经心理评估和影像学检查",
                "在医生指导下制定个性化的干预方案",
                "家人应提供更多的日常生活支持和监护",
                "考虑参加认知康复训练项目",
                "定期随访，密切监测认知功能变化"
            ]
        }
        
        return recommendations.get(risk_level, recommendations["medium"])
    
    def _extract_dialogue_excerpt(self, dialogue: List[Dict], max_turns: int = 6) -> List[Dict]:
        """
        提取对话片段用于报告展示
        
        Args:
            dialogue: 完整对话
            max_turns: 最大展示轮数
        
        Returns:
            对话片段
        """
        if len(dialogue) <= max_turns:
            return dialogue
        
        # 取前几轮对话
        return dialogue[:max_turns]
    
    def format_report_html(self, report: Dict) -> str:
        """
        将报告格式化为HTML（用于网页显示）
        
        Args:
            report: 报告数据
        
        Returns:
            HTML字符串
        """
        # 这个方法在Streamlit中不需要，因为我们会直接使用Streamlit组件
        # 但保留接口以便未来扩展
        pass