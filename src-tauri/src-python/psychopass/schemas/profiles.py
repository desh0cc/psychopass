from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PlatformUser:
    id: int
    platform: str
    platform_user_id: str
    username: str

@dataclass
class Profile:
    id: int
    avatar: str
    canonical_id: str
    global_name: str
    platform_users: List[PlatformUser]
    chats: Optional[List] = field(default_factory=list)
    added_at: Optional[str] = None

@dataclass
class UserProfile:
    user_id: int