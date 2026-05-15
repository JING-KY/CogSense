"""
数据库管理模块
使用SQLite存储对话记录和分析结果
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from config import DB_FILE


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.db_path = DB_FILE
        self._create_tables()
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        return conn
    
    def _create_tables(self):
        """创建数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                dialogue_id INTEGER,
                group_type TEXT,
                scenario TEXT
            )
        """)
        
        # 对话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dialogues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                dialogue_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # 分析结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                features TEXT NOT NULL,
                scores TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                total_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_session(
        self, 
        session_name: str,
        dialogue: List[Dict],
        features: Dict,
        scores: Dict,
        dialogue_id: int = None,
        group_type: str = None,
        scenario: str = None
    ) -> int:
        """
        保存完整的分析会话
        
        Args:
            session_name: 会话名称
            dialogue: 对话数据
            features: 语言特征
            scores: 认知评分
            dialogue_id: 对话ID（可选）
            group_type: 认知组别（可选）
            scenario: 场景（可选）
        
        Returns:
            会话ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 插入会话记录
            cursor.execute("""
                INSERT INTO sessions (session_name, dialogue_id, group_type, scenario)
                VALUES (?, ?, ?, ?)
            """, (session_name, dialogue_id, group_type, scenario))
            
            session_id = cursor.lastrowid
            
            # 插入对话数据
            cursor.execute("""
                INSERT INTO dialogues (session_id, dialogue_data)
                VALUES (?, ?)
            """, (session_id, json.dumps(dialogue, ensure_ascii=False)))
            
            # 插入分析结果
            cursor.execute("""
                INSERT INTO analyses (session_id, features, scores, risk_level, total_score)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                json.dumps(features, ensure_ascii=False),
                json.dumps(scores, ensure_ascii=False),
                scores.get("risk_level", "unknown"),
                scores.get("total_score", 0)
            ))
            
            conn.commit()
            return session_id
        
        except Exception as e:
            conn.rollback()
            raise e
        
        finally:
            conn.close()
    
    def load_session(self, session_id: int) -> Optional[Dict]:
        """
        加载指定会话的完整数据
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话数据字典，如果不存在返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 查询会话信息
            cursor.execute("""
                SELECT * FROM sessions WHERE id = ?
            """, (session_id,))
            
            session_row = cursor.fetchone()
            if not session_row:
                return None
            
            # 查询对话数据
            cursor.execute("""
                SELECT dialogue_data FROM dialogues WHERE session_id = ?
            """, (session_id,))
            
            dialogue_row = cursor.fetchone()
            
            # 查询分析结果
            cursor.execute("""
                SELECT features, scores, risk_level, total_score 
                FROM analyses WHERE session_id = ?
            """, (session_id,))
            
            analysis_row = cursor.fetchone()
            
            # 组装结果
            return {
                "session_id": session_row["id"],
                "session_name": session_row["session_name"],
                "created_at": session_row["created_at"],
                "dialogue_id": session_row["dialogue_id"],
                "group_type": session_row["group_type"],
                "scenario": session_row["scenario"],
                "dialogue": json.loads(dialogue_row["dialogue_data"]) if dialogue_row else [],
                "features": json.loads(analysis_row["features"]) if analysis_row else {},
                "scores": json.loads(analysis_row["scores"]) if analysis_row else {},
                "risk_level": analysis_row["risk_level"] if analysis_row else "unknown",
                "total_score": analysis_row["total_score"] if analysis_row else 0
            }
        
        finally:
            conn.close()
    
    def get_all_sessions(self) -> List[Dict]:
        """
        获取所有会话的摘要信息
        
        Returns:
            会话列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    s.id,
                    s.session_name,
                    s.created_at,
                    s.group_type,
                    s.scenario,
                    a.risk_level,
                    a.total_score
                FROM sessions s
                LEFT JOIN analyses a ON s.id = a.session_id
                ORDER BY s.created_at DESC
            """)
            
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                sessions.append({
                    "id": row["id"],
                    "session_name": row["session_name"],
                    "created_at": row["created_at"],
                    "group_type": row["group_type"],
                    "scenario": row["scenario"],
                    "risk_level": row["risk_level"],
                    "total_score": row["total_score"]
                })
            
            return sessions
        
        finally:
            conn.close()
    
    def delete_session(self, session_id: int):
        """
        删除指定会话及其相关数据
        
        Args:
            session_id: 会话ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 删除分析结果
            cursor.execute("DELETE FROM analyses WHERE session_id = ?", (session_id,))
            
            # 删除对话数据
            cursor.execute("DELETE FROM dialogues WHERE session_id = ?", (session_id,))
            
            # 删除会话记录
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            
            conn.commit()
        
        except Exception as e:
            conn.rollback()
            raise e
        
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict:
        """
        获取数据库统计信息
        
        Returns:
            统计数据字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 总会话数
            cursor.execute("SELECT COUNT(*) as count FROM sessions")
            total_sessions = cursor.fetchone()["count"]
            
            # 各风险等级分布
            cursor.execute("""
                SELECT risk_level, COUNT(*) as count
                FROM analyses
                GROUP BY risk_level
            """)
            
            risk_distribution = {}
            for row in cursor.fetchall():
                risk_distribution[row["risk_level"]] = row["count"]
            
            # 平均总分
            cursor.execute("SELECT AVG(total_score) as avg_score FROM analyses")
            avg_score = cursor.fetchone()["avg_score"] or 0
            
            # 各组别分布
            cursor.execute("""
                SELECT group_type, COUNT(*) as count
                FROM sessions
                WHERE group_type IS NOT NULL
                GROUP BY group_type
            """)
            
            group_distribution = {}
            for row in cursor.fetchall():
                group_distribution[row["group_type"]] = row["count"]
            
            return {
                "total_sessions": total_sessions,
                "risk_distribution": risk_distribution,
                "avg_score": round(avg_score, 2),
                "group_distribution": group_distribution
            }
        
        finally:
            conn.close()
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """
        获取最近的会话记录
        
        Args:
            limit: 返回数量限制
        
        Returns:
            会话列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    s.id,
                    s.session_name,
                    s.created_at,
                    s.group_type,
                    a.risk_level,
                    a.total_score
                FROM sessions s
                LEFT JOIN analyses a ON s.id = a.session_id
                ORDER BY s.created_at DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                sessions.append({
                    "id": row["id"],
                    "session_name": row["session_name"],
                    "created_at": row["created_at"],
                    "group_type": row["group_type"],
                    "risk_level": row["risk_level"],
                    "total_score": row["total_score"]
                })
            
            return sessions
        
        finally:
            conn.close()