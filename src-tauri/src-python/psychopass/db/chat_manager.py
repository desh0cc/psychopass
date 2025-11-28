import uuid
from typing import Optional, List
from psychopass.schemas import Chat, Profile, PlatformUser

class ChatManager:    
    def __init__(self, user_db):
        self.db = user_db
    
    def get_canon_id(self, chat: Chat) -> str:
        canon_str = f"{chat.id or ''}:{chat.name or ''}:{chat.type or ''}"
        return str(uuid.uuid5(uuid.NAMESPACE_OID, canon_str))
    
    def get_or_create(self, chat: Chat) -> int:
        canon_id = self.get_canon_id(chat)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO chat (canon_id, name, type)
                VALUES (?, ?, ?)
            """, (canon_id, chat.name, chat.type))
            
            cursor.execute("SELECT id FROM chat WHERE canon_id = ?", (canon_id,))
            return cursor.fetchone()[0]
    
    def get(self, chat_id: int) -> Optional[Chat]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, avatar, type 
                FROM chat WHERE id = ?
            """, (chat_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            participants = self._get_participants(cursor, row["id"])
            
            return Chat(
                id=chat_id,
                name=row["name"],
                avatar=row["avatar"],
                type=row["type"],
                participants=participants
            )
    
    def get_all(self) -> List[Chat]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, canon_id, name, avatar, type FROM chat")
            
            chats = []
            for row in cursor.fetchall():
                participants = self._get_participants(cursor, row["id"])
                
                chats.append(Chat(
                    id=row["id"],
                    name=row["name"],
                    type=row["type"],
                    participants=participants,
                    avatar=row["avatar"]
                ))
            
            return chats
    
    async def update(self, chat_id: int, name=None, avatar=None, chat_type=None) -> bool:
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if avatar is not None:
            avatar = await self.db.cache.cache_media(avatar)
            updates.append("avatar = ?")
            params.append(avatar)
        
        if chat_type is not None:
            updates.append("type = ?")
            params.append(chat_type)
        
        if not updates:
            return False
        
        params.append(chat_id)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE chat SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def _get_participants(self, cursor, chat_db_id: int) -> List[Profile]:
        cursor.execute("""
            SELECT DISTINCT p.id, p.avatar, p.canonical_id, p.global_name
            FROM profile p
            JOIN message m ON m.user_id = p.id
            WHERE m.chat_id = ?
        """, (chat_db_id,))
        
        participants = []
        for row in cursor.fetchall():
            cursor.execute("""
                SELECT id, platform, platform_user_id, username
                FROM platform_user
                WHERE profile_id = ?
            """, (row["id"],))
            
            platform_users = [
                PlatformUser(
                    id=pu["id"],
                    platform=pu["platform"],
                    platform_user_id=pu["platform_user_id"],
                    username=pu["username"]
                )
                for pu in cursor.fetchall()
            ]
            
            participants.append(Profile(
                id=row["id"],
                avatar=row["avatar"],
                canonical_id=row["canonical_id"],
                global_name=row["global_name"],
                platform_users=platform_users
            ))
        
        return participants
    
    def delete(self, chat_id: int):
        """Delete chat and all messages in it"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # chat validation
            cursor.execute("SELECT id FROM chat WHERE id = ?", (chat_id,))
            if not cursor.fetchone():
                return {"success": False, "error": "Chat not found"}
            
            cursor.execute("""
                DELETE FROM media 
                WHERE message_id IN (SELECT id FROM message WHERE chat_id = ?)
            """, (chat_id,))
            
            # Delete chat messages
            cursor.execute("DELETE FROM message WHERE chat_id = ?", (chat_id,))
            deleted_messages = cursor.rowcount
            
            # Delete chat
            cursor.execute("DELETE FROM chat WHERE id = ?", (chat_id,))
            
            return {
                "success": True, 
                "deleted_chat_id": chat_id,
                "deleted_messages": deleted_messages
            }
