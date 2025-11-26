import sqlite3
from typing import List, Optional, Dict, Tuple, Any, DefaultDict
from psychopass.schemas import Message, Media, EmotionStats, Emotion, EmotionStatsByYear
from psychopass.cache import Cache
from collections import defaultdict

class MessageManager:
    def __init__(self, user_db):
        self.user_db = user_db
        self.cache: Cache = user_db.cache

    async def add_batch(self, platform: str, messages: List[Message], chats: List):
        with self.user_db.get_connection() as db:
            cursor = db.cursor()

            chat_ids = {}
            for chat in chats:
                canon_id = self.user_db.chats.get_canon_id(chat)
                cursor.execute("""
                    INSERT OR IGNORE INTO chat (canon_id, name, type)
                    VALUES (?, ?, ?)
                """, (canon_id, chat.name, chat.type))
                cursor.execute("SELECT id FROM chat WHERE canon_id = ?", (canon_id,))
                chat_row_id = cursor.fetchone()[0]
                chat_ids[canon_id] = chat_row_id

            platform_to_db_id: Dict[Tuple[str, str], int] = {}
            for canon_id, chat_row_id in chat_ids.items():
                cursor.execute("""
                    SELECT id, platform_id FROM message
                    WHERE chat_id = ? AND platform_id IS NOT NULL
                """, (chat_row_id,))
                for db_id, plat_id in cursor.fetchall():
                    if plat_id is not None:
                        platform_to_db_id[(canon_id, str(plat_id))] = db_id

            media_to_cache = []
            media_paths = []
            
            for msg in messages:
                chat = getattr(msg, 'chat', None)
                if chat is None:
                    raise RuntimeError("Message does not have chat reference")
                canon_id = self.user_db.chats.get_canon_id(chat)
                chat_row_id = chat_ids[canon_id]

                profile_id = self.user_db.profiles.add_get_profile(
                    platform, msg.author_id, msg.author_name, db=db
                )

                reply_to_id = None
                reply = getattr(msg, 'reply', None)
                if reply is not None and getattr(reply, 'platform_id', None) is not None:
                    pid = str(reply.platform_id)
                    reply_to_id = platform_to_db_id.get((canon_id, pid))
                    if reply_to_id is None:
                        cursor.execute("""
                            SELECT id FROM message
                            WHERE platform_id = ? AND chat_id = ?
                        """, (pid, chat_row_id))
                        row = cursor.fetchone()
                        if row:
                            reply_to_id = row[0]

                cursor.execute("""
                    INSERT OR IGNORE INTO message (user_id, text, emotion, chat_id, timestamp, platform_id, reply_to)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile_id,
                    msg.text,
                    getattr(msg, 'emotion', None),
                    chat_row_id,
                    msg.timestamp,
                    str(msg.platform_id) if msg.platform_id is not None else None,
                    reply_to_id
                ))

                message_id = cursor.lastrowid
                
                if message_id == 0 and msg.platform_id is not None:
                    cursor.execute("""
                        SELECT id FROM message
                        WHERE platform_id = ? AND chat_id = ?
                    """, (str(msg.platform_id), chat_row_id))
                    row = cursor.fetchone()
                    if row:
                        message_id = row[0]
                
                msg.id = message_id
                
                if msg.platform_id is not None:
                    platform_to_db_id[(canon_id, str(msg.platform_id))] = message_id

                medias = getattr(msg, 'media', None)
                if medias is not None:
                    for media in medias:
                        media_to_cache.append((message_id, media))
                        media_paths.append(media.path)

        if media_to_cache:
            print(f"[INFO] Caching {len(media_to_cache)} media files...")

            media_paths = [media.path for _, media in media_to_cache]

            cached_paths = await self.cache.cache_media_batch(media_paths)

            with self.user_db.get_connection() as db:
                cursor = db.cursor()
                for (message_id, media), cached_path in zip(media_to_cache, cached_paths):
                    if cached_path:
                        cursor.execute("""
                            INSERT OR IGNORE INTO media (message_id, type, path)
                            VALUES (?, ?, ?)
                        """, (message_id, getattr(media, 'type', None), cached_path))
                    else:
                        print(f"[ERROR] Failed to cache media for message {message_id}")

            
    def get(self, message_id: int) -> Optional[Message]:
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            cursor.row_factory = sqlite3.Row
            
            cursor.execute("""
                SELECT 
                    m.id, m.platform_id, m.user_id, m.text, m.timestamp, 
                    m.emotion, m.reply_to, m.chat_id,
                    p.global_name, p.avatar
                FROM message m
                LEFT JOIN profile p ON m.user_id = p.id
                WHERE m.id = ?
            """, (message_id,))
            
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return Message(
                id=row['id'],
                author_id=str(row['platform_id']),
                author_name=row['global_name'],
                text=row['text'],
                timestamp=row['timestamp'],
                emotion=row['emotion'],
                chat_id=row['chat_id'],
            )


    def get_by_chat(self, chat_id: int) -> List[Message]:
        messages: dict[int, Message] = {}
        reply_map: dict[int, int] = {}

        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT 
                    m.id, m.platform_id, m.user_id, m.text, m.timestamp, 
                    m.emotion, m.reply_to, p.global_name, p.avatar
                FROM message m
                LEFT JOIN profile p ON m.user_id = p.id
                WHERE m.chat_id = ?
                ORDER BY m.timestamp ASC
            """, (chat_id,))

            rows = cursor.fetchall()
            for row in rows:
                db_id, platform_id, user_id, text, timestamp, emotion, reply_to, author_name, avatar = row
                msg = Message(
                    id=db_id,
                    chat_id=chat_id,
                    author_id=str(user_id),
                    author_name=author_name or "Unknown",
                    timestamp=timestamp,
                    text=text or "",
                    emotion=emotion,
                    avatar=avatar,
                    media=None,
                    reply=None
                )
                messages[db_id] = msg
                if reply_to:
                    reply_map[db_id] = reply_to

            cursor.execute("""
                SELECT message_id, type, path 
                FROM media 
                WHERE message_id IN (
                    SELECT id FROM message WHERE chat_id = ?
                )
            """, (chat_id,))
            for msg_id, mtype, path in cursor.fetchall():
                media = [Media(type=mtype, path=path)]
                messages[msg_id].media = media

            for msg_id, reply_to_id in reply_map.items():
                if reply_to_id in messages:
                    messages[msg_id].reply = messages[reply_to_id]

        return list(messages.values())

    def get_all(self, profile_id: Optional[int] = None):
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            if profile_id is None:
                cursor.execute("SELECT * FROM message")
            else:
                cursor.execute("SELECT * FROM message WHERE user_id = ?", (profile_id,))
            return cursor.fetchall()

    def get_by_emotion(self, user_id: int, emotion: str) -> List[Message]:
        messages: List[Message] = []
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT 
                    m.id,
                    m.chat_id,
                    m.user_id,
                    m.text,
                    m.timestamp,
                    m.emotion,
                    p.global_name,
                    p.avatar
                FROM message m
                LEFT JOIN profile p ON m.user_id = p.id
                WHERE p.id = ?
                AND m.emotion = ?
                ORDER BY m.timestamp ASC
            """, (user_id, emotion))
            rows = cursor.fetchall()
            for id, chat_canon_id, user_id, text, timestamp, emotion, author_name, avatar in rows:
                messages.append(Message(
                    id=id,
                    chat_id=chat_canon_id,
                    author_id=str(user_id),
                    author_name=author_name,
                    timestamp=timestamp,
                    avatar=avatar,
                    text=text,
                    emotion=emotion
                ))
        return messages

    def get_emotion_stats(self, profile_id: Optional[int] = None) -> EmotionStats:
        with self.user_db.get_connection() as db:
            cursor = db.cursor()

            if profile_id is not None:
                cursor.execute("""
                    SELECT emotion, COUNT(*)
                    FROM message
                    WHERE user_id = ? AND emotion IS NOT NULL AND emotion != ''
                    GROUP BY emotion
                """, (profile_id,))
                rows = cursor.fetchall()

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM message
                    WHERE user_id = ? AND emotion IS NOT NULL AND emotion != ''
                """, (profile_id,))
                total = cursor.fetchone()[0]
            else:
                cursor.execute("""
                    SELECT emotion, COUNT(*)
                    FROM message
                    WHERE emotion IS NOT NULL AND emotion != ''
                    GROUP BY emotion
                """)
                rows = cursor.fetchall()

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM message
                    WHERE emotion IS NOT NULL AND emotion != ''
                """)
                total = cursor.fetchone()[0]

            if total == 0:
                return EmotionStats(emotions=[], total_messages=0)

            emotions = [
                Emotion(name=emotion, percent=round((count / total) * 100, 2))
                for emotion, count in rows
            ]
            return EmotionStats(emotions=emotions, total_messages=total)
        
    def search_messages(self, query: str, limit: int = 10) -> List:
        """Search messages by content using SQL LIKE"""
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            
            cursor.execute("""
                SELECT id FROM message
                WHERE text LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{query}%", limit))
            
            message_ids = [row['id'] for row in cursor.fetchall()]
            
            messages = []
            for msg_id in message_ids:
                message = self.get(msg_id)
                if message:
                    messages.append(message)
            
            return messages
        
    def get_emotion_stats_by_year(self, profile_id: Optional[int] = None) -> EmotionStatsByYear:
        """Get emotion statistics grouped by year"""
        with self.user_db.get_connection() as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            
            base_query = """
                SELECT 
                    strftime('%Y', timestamp) as year,
                    emotion,
                    COUNT(*) as count
                FROM message
                WHERE emotion IS NOT NULL
            """
            
            if profile_id:
                base_query += " AND user_id = ?"
                cursor.execute(base_query + " GROUP BY year, emotion ORDER BY year DESC", (profile_id,))
            else:
                cursor.execute(base_query + " GROUP BY year, emotion ORDER BY year DESC")
            
            results = cursor.fetchall()
        
            year_data: DefaultDict[str, Dict[str, Any]] = defaultdict(lambda: {'emotions': defaultdict(int), 'total': 0})
            all_emotions = defaultdict(int)
            all_total = 0
            all_total = 0
            
            for row in results:
                year = row['year']
                emotion = row['emotion']
                count = row['count']
                
                year_data[year]['emotions'][emotion] += count
                year_data[year]['total'] += count
                
                all_emotions[emotion] += count
                all_total += count
            
            all_years_emotions = [
                Emotion(name=emotion, percent=round((count / all_total) * 100, 2), count=count)
                for emotion, count in sorted(all_emotions.items(), key=lambda x: x[1], reverse=True)
            ]
            
            all_years_stats = EmotionStats(
                emotions=all_years_emotions,
                total_messages=all_total,
                year="all"
            )
            
            by_year = {}
            for year, data in sorted(year_data.items(), reverse=True):
                emotions_list = [
                    Emotion(
                        name=emotion,
                        percent=round((count / data['total']) * 100, 2),
                        count=count
                    )
                    for emotion, count in sorted(data['emotions'].items(), key=lambda x: x[1], reverse=True)
                ]
                
                by_year[year] = EmotionStats(
                    emotions=emotions_list,
                    total_messages=data['total'],
                    year=year
                )
            
            return EmotionStatsByYear(
                all_years=all_years_stats,
                by_year=by_year
            )