from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List

from .profiles import Profile

@dataclass
class Media:
    type: str
    path: str
    thumbnail: Optional[str] = None

@dataclass
class Message:
    author_id: str
    author_name: str
    timestamp: str
    text: Optional[str] = None
    emotion: Optional[str] = None
    platform_id: Optional[str] = None
    avatar: Optional[str] = None
    id: Optional[int] = None
    chat_id: Optional[int] = None
    media: Optional[List[Media]] = None
    reply: Optional[Message] = None
    chat: Optional[Chat] = None
    forwarded_from: Optional[str] = None

@dataclass
class Chat:
    id: int
    name: Optional[str] = None
    avatar: Optional[str] = None
    type: Optional[str] = None
    participants: Optional[List[Profile]] = field(default_factory=list)