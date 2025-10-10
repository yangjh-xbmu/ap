"""
ConceptMap 多主题数据结构管理类

支持多主题学习系统的核心数据管理，包含数据迁移和向后兼容功能。
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import typer


class ConceptMap:
    """多主题概念地图管理类"""
    
    def __init__(self, file_path: Optional[str] = None):
        """
        初始化概念地图管理器
        
        Args:
            file_path: 概念地图文件路径，默认为 workspace/concept_map.json
        """
        if file_path is None:
            file_path = Path("workspace") / "concept_map.json"
        self.file_path = Path(file_path)
        self.data = self._load_or_migrate()
    
    def _load_or_migrate(self) -> Dict[str, Any]:
        """加载数据或执行迁移"""
        if not self.file_path.exists():
            return self._create_empty_structure()
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否为旧格式
            if self._is_old_format(data):
                typer.echo("检测到旧格式数据，正在自动迁移...")
                data = self._migrate_from_old_format(data)
                self._backup_old_data()
                typer.echo("✅ 数据迁移完成")
            
            return data
            
        except (json.JSONDecodeError, IOError) as e:
            typer.echo(f"警告：无法读取概念地图文件 {self.file_path}: {e}", err=True)
            return self._create_empty_structure()
    
    def _create_empty_structure(self) -> Dict[str, Any]:
        """创建空的多主题数据结构"""
        return {
            "topics": {},
            "metadata": {
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "active_topics": []
            }
        }
    
    def _is_old_format(self, data: Dict[str, Any]) -> bool:
        """检测是否为旧格式数据"""
        # 新格式必须包含 topics 和 metadata
        if "topics" in data and "metadata" in data:
            return False
    
        # 旧格式：直接包含概念数据，没有 topics 层级
        return any(
            isinstance(v, dict) and "name" in v for v in data.values()
        )
    
    def _migrate_from_old_format(
        self, old_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """从旧格式迁移到新格式"""
        new_data = self._create_empty_structure()
    
        # 将所有旧数据迁移到 "default" 主题下
        if old_data:
            new_data["topics"]["default"] = {
                "name": "Default Topic",
                "created_at": datetime.now().isoformat(),
                "concepts": old_data
            }
            new_data["metadata"]["active_topics"] = ["default"]
        
        return new_data
    
    def _backup_old_data(self) -> None:
        """备份旧数据"""
        backup_path = self.file_path.with_suffix('.json.backup')
        if self.file_path.exists():
            import shutil
            shutil.copy2(self.file_path, backup_path)
            typer.echo(f"📦 旧数据已备份到: {backup_path}")
    
    def save(self) -> None:
        """保存概念地图到文件"""
        # 更新时间戳
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # 确保目录存在
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            typer.echo(f"错误：无法保存概念地图文件 {self.file_path}: {e}", err=True)
            raise typer.Exit(1)
    
    # 主题管理方法
    def add_topic(self, topic_id: str, topic_name: str) -> None:
        """
        添加新主题
        
        Args:
            topic_id: 主题ID（slugified）
            topic_name: 主题显示名称
        """
        if topic_id not in self.data["topics"]:
            self.data["topics"][topic_id] = {
                "name": topic_name,
                "created_at": datetime.now().isoformat(),
                "concepts": {}
            }
    
            # 更新活跃主题列表
            if topic_id not in self.data["metadata"]["active_topics"]:
                self.data["metadata"]["active_topics"].append(topic_id)
    
    def get_topic(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """
        获取主题信息
        
        Args:
            topic_id: 主题ID
            
        Returns:
            主题数据字典，如果不存在返回 None
        """
        return self.data["topics"].get(topic_id)
    
    def list_topics(self) -> List[str]:
        """
        列出所有主题ID
        
        Returns:
            主题ID列表
        """
        return list(self.data["topics"].keys())
    
    def topic_exists(self, topic_id: str) -> bool:
        """
        检查主题是否存在
        
        Args:
            topic_id: 主题ID
            
        Returns:
            是否存在
        """
        return topic_id in self.data["topics"]
    
    def remove_topic(self, topic_id: str) -> bool:
        """
        删除主题
        
        Args:
            topic_id: 主题ID
            
        Returns:
            是否成功删除
        """
        if topic_id in self.data["topics"]:
            del self.data["topics"][topic_id]
            if topic_id in self.data["metadata"]["active_topics"]:
                self.data["metadata"]["active_topics"].remove(topic_id)
            return True
        return False

    # 概念管理方法
    def add_concept(
        self, topic_id: str, concept_id: str, concept_data: Dict[str, Any]
    ) -> None:
        """
        添加概念到指定主题
        
        Args:
            topic_id: 主题ID
            concept_id: 概念ID
            concept_data: 概念数据
        """
        if topic_id not in self.data["topics"]:
            raise ValueError(f"主题 '{topic_id}' 不存在")

        self.data["topics"][topic_id]["concepts"][concept_id] = concept_data

    def get_concept(
        self, topic_id: str, concept_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取指定概念
        
        Args:
            topic_id: 主题ID
            concept_id: 概念ID
            
        Returns:
            概念数据，如果不存在返回 None
        """
        topic = self.get_topic(topic_id)
        if topic:
            return topic["concepts"].get(concept_id)
        return None
    
    def update_status(self, topic_id: str, concept_id: str, status_key: str, value: Any) -> None:
        """
        更新概念状态
        
        Args:
            topic_id: 主题ID
            concept_id: 概念ID
            status_key: 状态键名
            value: 状态值
        """
        concept = self.get_concept(topic_id, concept_id)
        if concept:
            if 'status' not in concept:
                concept['status'] = {}
            concept['status'][status_key] = value

    def update_mastery(
        self, topic_id: str, concept_id: str, score_percent: float
    ) -> None:
        """
        更新概念掌握程度
        
        Args:
            topic_id: 主题ID
            concept_id: 概念ID
            score_percent: 得分百分比
        """
        concept = self.get_concept(topic_id, concept_id)
        if concept:
            if 'mastery' not in concept:
                concept['mastery'] = {}
            current_best = concept['mastery'].get(
                'best_score_percent', -1
            )
            if score_percent > current_best:
                concept['mastery']['best_score_percent'] = score_percent

    # 兼容性方法（用于向后兼容）
    def get_default_topic_id(self) -> Optional[str]:
        """
        获取默认主题ID（用于单主题兼容）
        
        Returns:
            默认主题ID，如果有多个主题则返回第一个
        """
        topics = self.list_topics()
        if not topics:
            return None
        
        # 优先返回 "default" 主题
        if "default" in topics:
            return "default"
        
        # 否则返回第一个主题
        return topics[0]
    
    def get_all_concepts_flat(self) -> Dict[str, Any]:
        """
        获取所有概念的扁平化视图（用于向后兼容）
        
        Returns:
            扁平化的概念字典
        """
        flat_concepts = {}
        for topic_id, topic_data in self.data["topics"].items():
            flat_concepts.update(topic_data["concepts"])
        return flat_concepts

    def get_topic_by_concept(self, concept_id: str) -> Optional[str]:
        """
        根据概念ID查找其所属的主题ID

        Args:
            concept_id: 概念ID

        Returns:
            主题ID，如果未找到则返回 None
        """
        for topic_id, topic_data in self.data["topics"].items():
            if concept_id in topic_data["concepts"]:
                return topic_id
        return None


def slugify(text: str) -> str:
    """
    将文本转换为适合作为文件名或ID的格式
    
    Args:
        text: 要转换的文本
        
    Returns:
        转换后的ID格式字符串
    """
    if not text:
        return ""
    
    # 移除或替换特殊字符
    text = re.sub(r'[^\w\s-]', '', text.strip())
    # 将空格替换为连字符
    text = re.sub(r'[-\s]+', '-', text)
    return text.lower()
