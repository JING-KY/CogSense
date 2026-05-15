"""
语言分析模块
分析对话中的语言特征，提取认知相关指标
"""

import re
import jieba
from typing import Dict, List
from collections import Counter


class LinguisticAnalyzer:
    """语言特征分析器"""
    
    def __init__(self):
        """初始化分词器"""
        jieba.setLogLevel(jieba.logging.INFO)  # 减少jieba日志输出
        
        # 模糊代词列表
        self.vague_pronouns = [
            "那个", "这个", "那", "这", "它", "他", "她",
            "那边", "这边", "那里", "这里", "那儿", "这儿",
            "什么", "啥", "咋", "怎么"
        ]
        
        # 时间相关词汇
        self.temporal_words = [
            "今天", "明天", "昨天", "前天", "后天",
            "早上", "中午", "下午", "晚上", "夜里",
            "星期", "周", "月", "年", "季节",
            "春天", "夏天", "秋天", "冬天"
        ]
        
        # 修复标记词（表示自我纠正）
        self.repair_markers = [
            "不对", "不是", "我是说", "应该是", "哦对",
            "等等", "让我想想", "我记得", "好像", "可能"
        ]
    
    def analyze_dialogue(self, dialogue: List[Dict]) -> Dict:
        """
        分析单段对话的语言特征
        
        Args:
            dialogue: 对话列表 [{"speaker": "elder", "text": "..."}]
        
        Returns:
            特征字典
        """
        # 提取老人的发言
        elder_utterances = [
            turn["text"] for turn in dialogue 
            if turn["speaker"] == "elder"
        ]
        
        if not elder_utterances:
            return self._empty_features()
        
        # 合并所有发言
        full_text = " ".join(elder_utterances)
        
        # 计算各项特征
        features = {
            "vocabulary_richness": self._calculate_vocabulary_richness(elder_utterances),
            "vague_pronoun_ratio": self._calculate_vague_pronoun_ratio(full_text),
            "repair_frequency": self._calculate_repair_frequency(elder_utterances),
            "repetition_rate": self._calculate_repetition_rate(elder_utterances),
            "coherence_score": self._calculate_coherence_score(elder_utterances),
            "temporal_confusion": self._detect_temporal_confusion(full_text),
            "avg_utterance_length": self._calculate_avg_utterance_length(elder_utterances),
            "filler_word_ratio": self._calculate_filler_word_ratio(full_text)
        }
        
        return features
    
    def _empty_features(self) -> Dict:
        """返回空特征字典"""
        return {
            "vocabulary_richness": 0,
            "vague_pronoun_ratio": 0,
            "repair_frequency": 0,
            "repetition_rate": 0,
            "coherence_score": 0,
            "temporal_confusion": 0,
            "avg_utterance_length": 0,
            "filler_word_ratio": 0
        }
    
    def _calculate_vocabulary_richness(self, utterances: List[str]) -> float:
        """
        计算词汇丰富度 (Type-Token Ratio)
        
        Args:
            utterances: 发言列表
        
        Returns:
            词汇丰富度 (0-1)
        """
        all_words = []
        for utterance in utterances:
            words = list(jieba.cut(utterance))
            # 过滤标点和单字符
            words = [w for w in words if len(w) > 1 and not re.match(r'[^\w]', w)]
            all_words.extend(words)
        
        if len(all_words) == 0:
            return 0.0
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        
        # TTR (Type-Token Ratio)
        ttr = unique_words / total_words
        
        return round(ttr, 3)
    
    def _calculate_vague_pronoun_ratio(self, text: str) -> float:
        """
        计算模糊代词使用比例
        
        Args:
            text: 文本
        
        Returns:
            模糊代词比例 (0-1)
        """
        words = list(jieba.cut(text))
        total_words = len([w for w in words if len(w) > 1])
        
        if total_words == 0:
            return 0.0
        
        vague_count = sum(1 for word in words if word in self.vague_pronouns)
        
        return round(vague_count / total_words, 3)
    
    def _calculate_repair_frequency(self, utterances: List[str]) -> float:
        """
        计算修复频率（自我纠正的次数）
        
        Args:
            utterances: 发言列表
        
        Returns:
            每句话的平均修复次数
        """
        if len(utterances) == 0:
            return 0.0
        
        total_repairs = 0
        for utterance in utterances:
            for marker in self.repair_markers:
                total_repairs += utterance.count(marker)
        
        return round(total_repairs / len(utterances), 3)
    
    def _calculate_repetition_rate(self, utterances: List[str]) -> float:
        """
        计算重复率（相似句子的比例）
        
        Args:
            utterances: 发言列表
        
        Returns:
            重复率 (0-1)
        """
        if len(utterances) <= 1:
            return 0.0
        
        # 简化：计算完全相同或高度相似的句子
        repetitions = 0
        for i in range(len(utterances)):
            for j in range(i + 1, len(utterances)):
                similarity = self._sentence_similarity(utterances[i], utterances[j])
                if similarity > 0.7:  # 相似度阈值
                    repetitions += 1
        
        max_pairs = len(utterances) * (len(utterances) - 1) / 2
        
        return round(repetitions / max_pairs, 3) if max_pairs > 0 else 0.0
    
    def _sentence_similarity(self, s1: str, s2: str) -> float:
        """
        计算两个句子的相似度（简化版）
        
        Args:
            s1: 句子1
            s2: 句子2
        
        Returns:
            相似度 (0-1)
        """
        words1 = set(jieba.cut(s1))
        words2 = set(jieba.cut(s2))
        
        if len(words1) == 0 or len(words2) == 0:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_coherence_score(self, utterances: List[str]) -> float:
        """
        计算连贯性得分（基于词汇重叠）
        
        Args:
            utterances: 发言列表
        
        Returns:
            连贯性得分 (0-1)
        """
        if len(utterances) <= 1:
            return 1.0
        
        coherence_scores = []
        
        for i in range(len(utterances) - 1):
            words_current = set(jieba.cut(utterances[i]))
            words_next = set(jieba.cut(utterances[i + 1]))
            
            # 计算相邻句子的词汇重叠
            overlap = len(words_current & words_next)
            total = len(words_current | words_next)
            
            if total > 0:
                coherence_scores.append(overlap / total)
        
        if len(coherence_scores) == 0:
            return 0.5
        
        return round(sum(coherence_scores) / len(coherence_scores), 3)
    
    def _detect_temporal_confusion(self, text: str) -> float:
        """
        检测时间混淆程度
        
        Args:
            text: 文本
        
        Returns:
            混淆程度 (0-1)，越高越混乱
        """
        # 检测时间词的使用
        temporal_count = sum(1 for word in self.temporal_words if word in text)
        
        # 检测矛盾的时间表达（简化版）
        confusion_patterns = [
            r'昨天.*明天',
            r'早上.*晚上.*早上',
            r'今天.*昨天.*今天',
            r'星期.*月.*星期'
        ]
        
        confusion_score = 0
        for pattern in confusion_patterns:
            if re.search(pattern, text):
                confusion_score += 0.2
        
        # 如果时间词很少但有混淆，说明问题更严重
        if temporal_count > 0:
            confusion_score = min(confusion_score / temporal_count, 1.0)
        
        return round(confusion_score, 3)
    
    def _calculate_avg_utterance_length(self, utterances: List[str]) -> float:
        """
        计算平均句子长度
        
        Args:
            utterances: 发言列表
        
        Returns:
            平均字数
        """
        if len(utterances) == 0:
            return 0.0
        
        total_length = sum(len(u) for u in utterances)
        
        return round(total_length / len(utterances), 1)
    
    def _calculate_filler_word_ratio(self, text: str) -> float:
        """
        计算填充词比例（"嗯"、"啊"、"呃"等）
        
        Args:
            text: 文本
        
        Returns:
            填充词比例 (0-1)
        """
        filler_words = ["嗯", "啊", "呃", "哦", "唉", "哎", "嘿"]
        
        words = list(jieba.cut(text))
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        filler_count = sum(1 for word in words if word in filler_words)
        
        return round(filler_count / total_words, 3)
    
    def get_feature_description(self, feature_name: str) -> str:
        """
        获取特征的中文描述
        
        Args:
            feature_name: 特征名称
        
        Returns:
            中文描述
        """
        descriptions = {
            "vocabulary_richness": "词汇丰富度",
            "vague_pronoun_ratio": "模糊代词使用率",
            "repair_frequency": "自我修复频率",
            "repetition_rate": "话语重复率",
            "coherence_score": "语义连贯性",
            "temporal_confusion": "时间混淆程度",
            "avg_utterance_length": "平均句子长度",
            "filler_word_ratio": "填充词使用率"
        }
        
        return descriptions.get(feature_name, feature_name)