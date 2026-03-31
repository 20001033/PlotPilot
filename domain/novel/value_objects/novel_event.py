from dataclasses import dataclass
from enum import Enum
from typing import List
from domain.bible.value_objects.character_id import CharacterId


class EventType(str, Enum):
    """事件类型"""
    CHARACTER_INTRODUCTION = "character_introduction"  # 角色介绍
    RELATIONSHIP_CHANGE = "relationship_change"        # 关系变化
    CONFLICT = "conflict"                              # 冲突
    REVELATION = "revelation"                          # 揭示
    DECISION = "decision"                              # 决定


@dataclass(frozen=True)
class NovelEvent:
    """小说事件值对象"""
    chapter_number: int
    event_type: EventType
    description: str
    involved_characters: List[CharacterId]

    def __post_init__(self):
        if self.chapter_number < 1:
            raise ValueError("Chapter number must be >= 1")
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")
