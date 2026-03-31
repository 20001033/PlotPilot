from typing import List
from domain.novel.value_objects.novel_event import NovelEvent
from domain.bible.value_objects.character_id import CharacterId


class EventTimeline:
    """事件时间线"""

    def __init__(self):
        self._events: List[NovelEvent] = []

    @property
    def events(self) -> List[NovelEvent]:
        """返回事件列表的副本"""
        return self._events.copy()

    def add_event(self, event: NovelEvent) -> None:
        """添加事件并自动按章节号排序"""
        self._events.append(event)
        self._events.sort(key=lambda e: e.chapter_number)

    def get_events_before(self, chapter_number: int) -> List[NovelEvent]:
        """获取指定章节之前的事件（不包括该章节）"""
        return [e for e in self._events if e.chapter_number < chapter_number]

    def get_events_involving(self, character_id: CharacterId) -> List[NovelEvent]:
        """获取涉及特定角色的事件"""
        return [e for e in self._events if character_id in e.involved_characters]
