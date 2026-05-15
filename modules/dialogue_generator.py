"""
对话生成模块
使用阿里云通义千问API生成模拟家庭对话
"""

import json
import random
import time
from typing import List, Dict
from openai import OpenAI
import streamlit as st

from config import (
    OPENAI_API_KEY, 
    OPENAI_BASE_URL, 
    MODEL_NAME,
    DIALOGUE_CONFIG,
    DIALOGUE_FILE
)
from utils.prompts import SYSTEM_PROMPT, get_prompt


class DialogueGenerator:
    """对话生成器"""
    
    def __init__(self):
        """初始化OpenAI客户端"""
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
        self.model = MODEL_NAME
        self.config = DIALOGUE_CONFIG
    
    def generate_single_dialogue(
        self, 
        dialogue_id: int, 
        group: str, 
        scenario: str,
        max_retries: int = 3
    ) -> Dict:
        """
        生成单条对话
        
        Args:
            dialogue_id: 对话ID
            group: 认知状态组别 (HC/MCI/ED)
            scenario: 对话场景
            max_retries: 最大重试次数
        
        Returns:
            对话数据字典
        """
        prompt = get_prompt(group, scenario)
        
        for attempt in range(max_retries):
            try:
                # 调用API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,  # 增加随机性，避免重复
                    max_tokens=2000
                )
                
                # 解析响应
                content = response.choices[0].message.content
                
                # 尝试提取JSON
                dialogue_data = self._extract_json(content)
                
                # 验证对话格式
                if self._validate_dialogue(dialogue_data):
                    return {
                        "id": dialogue_id,
                        "group": group,
                        "scenario": scenario,
                        "dialogue": dialogue_data["dialogue"]
                    }
                else:
                    raise ValueError("对话格式验证失败")
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)  # 等待1秒后重试
                    continue
                else:
                    # 最后一次失败，返回错误占位符
                    return self._create_fallback_dialogue(dialogue_id, group, scenario)
        
        return self._create_fallback_dialogue(dialogue_id, group, scenario)
    
    def _extract_json(self, content: str) -> Dict:
        """
        从LLM响应中提取JSON
        
        Args:
            content: LLM返回的文本
        
        Returns:
            解析后的JSON对象
        """
        # 尝试直接解析
        try:
            return json.loads(content)
        except:
            pass
        
        # 尝试提取代码块中的JSON
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            json_str = content[start:end].strip()
            return json.loads(json_str)
        
        # 尝试提取花括号内容
        if "{" in content and "}" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            return json.loads(json_str)
        
        raise ValueError("无法提取JSON")
    
    def _validate_dialogue(self, dialogue_data: Dict) -> bool:
        """
        验证对话数据格式
        
        Args:
            dialogue_data: 对话数据
        
        Returns:
            是否有效
        """
        if "dialogue" not in dialogue_data:
            return False
        
        dialogue = dialogue_data["dialogue"]
        
        # 检查是否为列表
        if not isinstance(dialogue, list):
            return False
        
        # 检查轮数（允许30-42轮的弹性，目标是36轮）
        if len(dialogue) < 30 or len(dialogue) > 42:
            return False
        
        # 检查每轮格式
        for turn in dialogue:
            if "speaker" not in turn or "text" not in turn:
                return False
            if turn["speaker"] not in ["elder", "family"]:
                return False
            if not turn["text"] or len(turn["text"]) < 3:
                return False
        
        return True
    
    def _create_fallback_dialogue(self, dialogue_id: int, group: str, scenario: str) -> Dict:
        """
        创建备用对话（当API调用失败时）
        
        Args:
            dialogue_id: 对话ID
            group: 认知状态组别
            scenario: 对话场景
        
        Returns:
            备用对话数据
        """
        fallback_dialogues = {
            "HC": [
                {"speaker": "family", "text": "妈，今天想吃什么？"},
                {"speaker": "elder", "text": "做点清淡的吧，昨天吃得有点油腻。"},
                {"speaker": "family", "text": "那我做番茄炒蛋和青菜汤？"},
                {"speaker": "elder", "text": "好啊，再蒸点米饭。对了，冰箱里还有鸡蛋吗？"},
                {"speaker": "family", "text": "有的，昨天刚买的。"},
                {"speaker": "elder", "text": "那就好。你爸最近血压怎么样？"},
                {"speaker": "family", "text": "挺稳定的，一直在按时吃药。"},
                {"speaker": "elder", "text": "那就好，要记得提醒他别忘了。"},
                {"speaker": "family", "text": "放心吧，我每天都盯着呢。"},
                {"speaker": "elder", "text": "你们工作都忙，我自己能照顾好自己。"},
                {"speaker": "family", "text": "我知道，但还是要注意身体。"},
                {"speaker": "elder", "text": "好好好，我会的。"}
            ],
            "MCI": [
                {"speaker": "family", "text": "妈，您的药吃了吗？"},
                {"speaker": "elder", "text": "药？哦...我刚才好像吃了，还是没吃来着？"},
                {"speaker": "family", "text": "药盒里还有，应该是还没吃。"},
                {"speaker": "elder", "text": "是吗？那我现在吃。那个...白色的小药片是什么来着？"},
                {"speaker": "family", "text": "那是降压药，每天早上吃一片。"},
                {"speaker": "elder", "text": "哦对对，我记起来了。"},
                {"speaker": "family", "text": "您最近记性好像有点..."},
                {"speaker": "elder", "text": "人老了嘛，记性不好很正常。"},
                {"speaker": "family", "text": "也是，不过还是要注意。"},
                {"speaker": "elder", "text": "我知道。对了，今天是星期几来着？"},
                {"speaker": "family", "text": "星期三。"},
                {"speaker": "elder", "text": "哦，星期三...那明天是星期四了。"}
            ],
            "ED": [
                {"speaker": "family", "text": "妈，今天天气不错，我们出去走走吧。"},
                {"speaker": "elder", "text": "出去？去哪儿？"},
                {"speaker": "family", "text": "就在小区里转转，晒晒太阳。"},
                {"speaker": "elder", "text": "哦...那个...我的那个...外套在哪儿？"},
                {"speaker": "family", "text": "在衣柜里，我帮您拿。"},
                {"speaker": "elder", "text": "我们要去哪儿来着？"},
                {"speaker": "family", "text": "小区里散步，刚才说过的。"},
                {"speaker": "elder", "text": "哦对...小区...那个谁也在那儿吗？"},
                {"speaker": "family", "text": "您说的是王阿姨吗？"},
                {"speaker": "elder", "text": "对对，就是她。她...她住哪儿来着？"},
                {"speaker": "family", "text": "就在我们楼上，3楼。"},
                {"speaker": "elder", "text": "3楼...我们是几楼？"}
            ]
        }
        
        return {
            "id": dialogue_id,
            "group": group,
            "scenario": scenario,
            "dialogue": fallback_dialogues.get(group, fallback_dialogues["HC"])
        }
    
    def generate_all_dialogues(self, progress_callback=None) -> List[Dict]:
        """
        生成所有对话数据
        
        Args:
            progress_callback: 进度回调函数
        
        Returns:
            对话数据列表
        """
        all_dialogues = []
        total = self.config["total_samples"]
        
        dialogue_id = 1
        
        for group in self.config["groups"]:
            for i in range(self.config["samples_per_group"]):
                # 随机选择场景
                scenario = random.choice(self.config["scenarios"])
                
                # 生成对话
                dialogue = self.generate_single_dialogue(dialogue_id, group, scenario)
                all_dialogues.append(dialogue)
                
                # 更新进度
                if progress_callback:
                    progress_callback(dialogue_id, total, group, scenario)
                
                dialogue_id += 1
                
                # 避免API限流
                time.sleep(0.5)
        
        return all_dialogues
    
    def save_dialogues(self, dialogues: List[Dict]):
        """
        保存对话数据到JSON文件
        
        Args:
            dialogues: 对话数据列表
        """
        with open(DIALOGUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(dialogues, f, ensure_ascii=False, indent=2)
    
    def load_dialogues(self) -> List[Dict]:
        """
        从JSON文件加载对话数据
        
        Returns:
            对话数据列表
        """
        try:
            with open(DIALOGUE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def dialogues_exist(self) -> bool:
        """
        检查对话数据是否已存在
        
        Returns:
            是否存在
        """
        try:
            dialogues = self.load_dialogues()
            return len(dialogues) >= self.config["total_samples"]
        except:
            return False