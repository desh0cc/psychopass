import sqlite3, os
from typing import Optional, List
from contextlib import contextmanager

from psychopass.cache import Cache
from psychopass.db import ProfileManager
from psychopass.db import ChatManager
from psychopass.db import MessageManager
from psychopass.db import StatsManager

class UserDB:
    def __init__(self, db_path: str, cache_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(cache_path, exist_ok=True)
        
        self.db_path = db_path
        self.cache_path = cache_path
        
        # Cache 
        self.cache = Cache(cache_path)

        # Managers init
        self.profiles = ProfileManager(self)
        self.chats = ChatManager(self)
        self.messages = MessageManager(self)
        self.stats = StatsManager(self)
        
        self._init_db()
        self.stats._ensure_stats_row()
    
    @contextmanager
    def get_connection(self):
        """Context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Init database"""
        with self.get_connection() as db:
            cursor = db.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profile (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    global_name TEXT,
                    avatar TEXT,
                    canonical_id TEXT UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canon_id TEXT UNIQUE,
                    name TEXT,
                    avatar TEXT,
                    type TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS platform_user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    platform TEXT NOT NULL,
                    platform_user_id TEXT NOT NULL,
                    username TEXT,
                    UNIQUE(platform, platform_user_id),
                    FOREIGN KEY(profile_id) REFERENCES profile(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform_id TEXT,
                    user_id INTEGER,
                    chat_id INTEGER,
                    text TEXT,
                    emotion TEXT,
                    timestamp TEXT,
                    reply_to INTEGER,
                    UNIQUE(chat_id, timestamp, text),
                    FOREIGN KEY(user_id) REFERENCES profile(id),
                    FOREIGN KEY(chat_id) REFERENCES chat(id),
                    FOREIGN KEY(reply_to) REFERENCES message(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    FOREIGN KEY(message_id) REFERENCES message(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS merge_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    primary_id INTEGER NOT NULL,
                    secondary_id INTEGER NOT NULL,
                    platform_ids TEXT NOT NULL,
                    msg_ids TEXT,
                    old_name TEXT,
                    old_avatar TEXT,
                    old_canon TEXT,
                    merged_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY CHECK(id = 1),
                    version TEXT DEFAULT '0.2.0',
                    messages INT DEFAULT 0,
                    uploads INT DEFAULT 0,
                    profiles INT DEFAULT 0,
                    last_upload DATETIME
                )
            """)

        return f"Succesfully created db at {self.db_path}"
    
    
    # Profile methods
    def get_profile(self, profile_id: int):
        return self.profiles.get(profile_id)
    
    def get_profiles(self):
        return self.profiles.get_all()
    
    def add_platform_user(self, platform: str, platform_user_id: str, username: str, profile_id: Optional[int] = None):
        return self.profiles.add_get_profile(platform, platform_user_id, username, profile_id)
    
    async def update_profile(self, profile_id: int, **kwargs):
        return await self.profiles.update(profile_id, **kwargs)
    
    def delete_profile(self, profile_id: int):
        return self.profiles.delete(profile_id)
    
    def merge_profiles(self, primary_id: int, secondary_ids: List[int]):
        return self.profiles.merge(primary_id, secondary_ids)
    
    def unmerge_profiles(self, primary_id: int, platform_user_ids: List[int]):
        return self.profiles.unmerge(primary_id, platform_user_ids)
    
    # Chat methods
    def get_chat(self, chat_id: int):
        return self.chats.get(chat_id)
    
    def get_chats(self):
        return self.chats.get_all()
    
    async def update_chat(self, chat_id: int, **kwargs):
        return await self.chats.update(chat_id, **kwargs)
    
    # Message methods
    def get_message(self, message_id: int):
        return self.messages.get(message_id)

    def add_messages_batch(self, platform: str, messages, chats):
        return self.messages.add_batch(platform, messages, chats)
    
    def get_chat_messages(self, chat_id: int):
        return self.messages.get_by_chat(chat_id)
    
    def get_messages(self, profile_id: Optional[int] = None):
        return self.messages.get_all(profile_id)
    
    def get_messages_by_emotion(self, user_id: int, emotion: str):
        return self.messages.get_by_emotion(user_id, emotion)
    
    def get_emotion_percentages(self, profile_id: Optional[int] = None):
        return self.messages.get_emotion_stats(profile_id)
    
    def get_yearly_emotions(self):
        return self.messages.get_emotion_stats_by_year()
    
    def search_messages(self, query: str):
        return self.messages.search_messages(query)
    
    # Stats methods
    def get_stats(self):
        return self.stats.get()
    
    def update_stats_auto(self):
        return self.stats.update_auto()