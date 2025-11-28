import uuid, json
from typing import Optional, List
from psychopass.cache import Cache
from psychopass.schemas import Profile, PlatformUser, Chat

class ProfileManager:
    def __init__(self, user_db):
        self.user_db = user_db
        self.cache: Cache = user_db.cache

    def add_get_profile(self, 
        platform: str, platform_user_id: str, username: str,
        profile_id: Optional[int] = None,db=None
        ):
        """adds AND gets your profile"""

        if db is None:
            db = self.user_db.get_connection()
    
        cursor = db.cursor()
        cursor.execute("""
            SELECT profile_id FROM platform_user
            WHERE platform = ? AND platform_user_id = ?
        """, (platform, platform_user_id))
        row = cursor.fetchone()
        if row:
            return row[0]

        if profile_id is None:
            canonical_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO profile (canonical_id, global_name)
                VALUES (?, ?)
            """, (canonical_id, username))

            profile_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO platform_user (profile_id, platform, platform_user_id, username)
            VALUES (?, ?, ?, ?)
        """, (profile_id, platform, platform_user_id, username))

        db.commit()
        return profile_id

    async def update(
        self,
        profile_id: int,
        global_name: Optional[str] = None,
        avatar: Optional[str] = None,
        canonical_id: Optional[str] = None
    ) -> str:
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            fields, values = [], []

            if global_name is not None:
                fields.append("global_name = ?")
                values.append(global_name)
            if avatar is not None:
                avatar = await self.cache.cache_media(avatar)
                fields.append("avatar = ?")
                values.append(avatar)
            if canonical_id is not None:
                fields.append("canonical_id = ?")
                values.append(canonical_id)

            if not fields:
                return "No fields to update."

            query = f"UPDATE profile SET {', '.join(fields)} WHERE id = ?"
            values.append(profile_id)
            cursor.execute(query, values)

            if cursor.rowcount == 0:
                return f"No profile found with id {profile_id}."
            return f"Profile {profile_id} successfully updated."

    def delete(self, profile_id: int):
        """Delete profiles and all its data"""
        with self.user_db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Profile validation
            cursor.execute("SELECT id FROM profile WHERE id = ?", (profile_id,))
            if not cursor.fetchone():
                return {"success": False, "error": "Profile not found"}
            
            cursor.execute("""
                DELETE FROM media 
                WHERE message_id IN (SELECT id FROM message WHERE user_id = ?)
            """, (profile_id,))
            
            cursor.execute("DELETE FROM message WHERE user_id = ?", (profile_id,))
            deleted_messages = cursor.rowcount
            
            cursor.execute("DELETE FROM platform_user WHERE profile_id = ?", (profile_id,))
            deleted_platforms = cursor.rowcount
            
            cursor.execute("""
                DELETE FROM merge_history 
                WHERE primary_id = ? OR secondary_id = ?
            """, (profile_id, profile_id))
            
            cursor.execute("DELETE FROM profile WHERE id = ?", (profile_id,))
            
            return {
                "success": True,
                "deleted_profile_id": profile_id,
                "deleted_messages": deleted_messages,
                "deleted_platforms": deleted_platforms
            }

    def merge(self, primary_id: int, secondary_ids: List[int]) -> str:
        """merge list of profiles together"""
        if not secondary_ids:
            return "No secondary profiles provided."

        with self.user_db.get_connection() as db:
            cursor = db.cursor()

            cursor.execute(
                "SELECT global_name, avatar, canonical_id FROM profile WHERE id = ?",
                (primary_id,)
            )
            primary = cursor.fetchone()
            if not primary:
                raise ValueError(f"Primary profile {primary_id} not found")

            primary_name, primary_avatar, primary_canon = primary

            for sec_id in secondary_ids:
                cursor.execute(
                    "SELECT global_name, avatar, canonical_id FROM profile WHERE id = ?",
                    (sec_id,)
                )
                secondary = cursor.fetchone()
                if not secondary:
                    continue
                sec_name, sec_avatar, sec_canon = secondary

                if not primary_name and sec_name:
                    primary_name = sec_name
                if not primary_avatar and sec_avatar:
                    primary_avatar = sec_avatar
                if not primary_canon and sec_canon:
                    primary_canon = sec_canon

                cursor.execute("SELECT id FROM platform_user WHERE profile_id = ?", (sec_id,))
                platform_user_ids = [r[0] for r in cursor.fetchall()]

                cursor.execute("SELECT id FROM message WHERE user_id = ?", (sec_id,))
                msg_ids = [r[0] for r in cursor.fetchall()]

                cursor.execute("""
                    INSERT INTO merge_history (
                        primary_id, secondary_id, platform_ids, old_name, old_avatar, old_canon, msg_ids
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    primary_id, sec_id, json.dumps(platform_user_ids),
                    sec_name, sec_avatar, sec_canon, json.dumps(msg_ids)
                ))

                cursor.execute("UPDATE platform_user SET profile_id = ? WHERE profile_id = ?", (primary_id, sec_id))
                cursor.execute("UPDATE message SET user_id = ? WHERE user_id = ?", (primary_id, sec_id))
                cursor.execute("DELETE FROM profile WHERE id = ?", (sec_id,))

            cursor.execute("""
                UPDATE profile SET global_name = ?, avatar = ?, canonical_id = ?
                WHERE id = ?
            """, (primary_name, primary_avatar, primary_canon, primary_id))

            return f"Profiles {secondary_ids} merged into {primary_id}"

    def unmerge(self, primary_id: int, secondary_platform_user_ids: list[int]) -> str:
        """unmerge profiles"""
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            results = []

            for platform_user_id in secondary_platform_user_ids:
                cursor.execute("SELECT profile_id FROM platform_user WHERE id = ?", (platform_user_id,))
                row = cursor.fetchone()
                if not row:
                    results.append(f"No platform_user found with id {platform_user_id}")
                    continue

                profile_id_for_user = row[0]
                secondary_profile_id = None
                old_name = old_avatar = old_canon = None
                platform_ids = []
                msg_ids = []
                
                cursor.execute("""
                    SELECT secondary_id, old_name, old_avatar, old_canon, platform_ids, msg_ids
                    FROM merge_history
                    WHERE primary_id = ?
                    ORDER BY id DESC
                """, (primary_id,))
                history_records = cursor.fetchall()
                found = False

                for record in history_records:
                    sec_id, rec_name, rec_avatar, rec_canon, platform_ids_json, msg_ids_json = record
                    try:
                        platform_ids = json.loads(platform_ids_json) if platform_ids_json else []
                        msg_ids = json.loads(msg_ids_json) if msg_ids_json else []
                    except (TypeError, json.JSONDecodeError):
                        platform_ids = []
                        msg_ids = []

                    if platform_user_id in platform_ids:
                        secondary_profile_id = sec_id
                        old_name = rec_name
                        old_avatar = rec_avatar
                        old_canon = rec_canon
                        found = True
                        break


                if not found or secondary_profile_id is None:
                    results.append(f"No merge history found for platform_user {platform_user_id}")
                    continue

                cursor.execute("""
                    INSERT INTO profile (id, global_name, avatar, canonical_id)
                    VALUES (?, ?, ?, ?)
                """, (secondary_profile_id, old_name, old_avatar, old_canon))

                if platform_ids:
                    placeholders = ",".join("?" for _ in platform_ids)
                    cursor.execute(
                        f"UPDATE platform_user SET profile_id = ? WHERE id IN ({placeholders})",
                        [secondary_profile_id] + platform_ids
                    )

                if msg_ids:
                    placeholders = ",".join("?" for _ in msg_ids)
                    cursor.execute(
                        f"UPDATE message SET user_id = ? WHERE id IN ({placeholders})",
                        [secondary_profile_id] + msg_ids
                    )

                cursor.execute("""
                    DELETE FROM merge_history
                    WHERE primary_id = ? AND secondary_id = ?
                """, (primary_id, secondary_profile_id))

                results.append(f"Restored profile {secondary_profile_id} from platform_user {platform_user_id}")

            db.commit()
            return "\n".join(results)

    def get(self, profile_id: int) -> Optional[Profile]:
        """get profile"""
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT id, global_name, avatar, canonical_id, created_at
                FROM profile
                WHERE id = ?
            """, (profile_id,))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("SELECT id, platform, platform_user_id, username FROM platform_user WHERE profile_id = ?", (profile_id,))
            platform_users = [PlatformUser(*r) for r in cursor.fetchall()]

            cursor.execute("""
                SELECT DISTINCT c.id, c.name, c.avatar, c.type
                FROM chat c
                JOIN message m ON c.id = m.chat_id
                WHERE m.user_id = ?
            """, (profile_id,))
            chats = [Chat(*r) for r in cursor.fetchall()]

            return Profile(
                id=row[0],
                global_name=row[1],
                avatar=row[2],
                canonical_id=row[3],
                added_at=row[4],
                platform_users=platform_users,
                chats=chats
            )

    def get_all(self) -> List[Profile]:
        """get all profiles"""
        profiles = []
        with self.user_db.get_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT id, canonical_id, avatar, global_name FROM profile")
            for pid, canonical_id, avatar, global_name in cursor.fetchall():
                cursor.execute("SELECT id, platform, platform_user_id, username FROM platform_user WHERE profile_id = ?", (pid,))
                platform_users = [PlatformUser(*r) for r in cursor.fetchall()]
                profiles.append(Profile(id=pid, canonical_id=canonical_id, avatar=avatar, global_name=global_name, platform_users=platform_users))
        return profiles