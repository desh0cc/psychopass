from dataclasses import dataclass
from typing import Optional, List, Literal

@dataclass
class EmojiRequest:
    length: int

@dataclass
class KeyRequest:
    key: str
    value: Optional[str] = None

@dataclass
class ChatRequest:
    chat_id: int

@dataclass
class MergeRequest:
    primary_id: int
    secondary_ids: List[int]

@dataclass
class EmotionRequest:
    id: int
    emotion: str

@dataclass
class ProfileUpdate:
    id: int
    avatar: Optional[str] = None
    global_name: Optional[str] = None

@dataclass
class SearchQuery:
    query: str
    engine: Literal["vector", "linear"] = "vector"

@dataclass
class MessageRequest:
    message_id: int