from psychopass.parser import parser
from psychopass.schemas import Message, Chat, Media
from tqdm import tqdm
from typing import List, Tuple
from psychopass.utils import find_files, get_data

def get_type(type: str) -> str:
    # print(f"[DEBUG]: given str: {type}")

    if "image" in type:
        return "photo"
    elif "video" in type:
        return "video"
    else:
        return "file"

def get_media(data: list[dict]) -> List[Media]:
    media_list: List[Media] = []

    # print(f"[DEBUG] data - {data}")
    for attachment in data:
        thumbnail = attachment.get('thumbnail')
        if thumbnail is not None:
            thumbnail = thumbnail.get("url")
        url = attachment.get('proxy_url')
        media_type = get_type(attachment.get('content_type', ""))

        if not url or not media_type:
            continue

        media_list.append(Media(
            type=media_type,
            path=url,
            thumbnail=thumbnail
        ))

    return media_list

@parser.register("discord")
def parse_discord(path: str) -> Tuple[List[Message], List[Chat]]:
    data_to_parse = [get_data(f) for f in find_files(path)]

    if not data_to_parse:
        raise ValueError("nun here")

    messages: List[Message] = []
    chats: List[Chat] = []
    reply_map: dict[int,Message] = {}

    BASE_URL = "https://cdn.discordapp.com/avatars"

    for data in tqdm(data_to_parse, desc="Reading files"):
        chat = Chat(
            id=0,
            name=data[0].get("name","uknown"),
            type="channel"
        )

        chats.append(chat)

        for message in tqdm(data, desc="Reading data"):
            media, text, reply = None, None, None

            text = message.get("content")

            author = message.get('author')
            if not author or not author.get('global_name'):
                continue

            avatar = (
                f"{BASE_URL}/{author['id']}/{author['avatar']}"
                if author.get("avatar") else None
            )

            reply_id = message.get("message_reference")
            reply_id = reply_id.get("message_id") if reply_id else None
            reply = reply_map.get(reply_id, None) if reply_id else None

            attachments = message.get('attachments')
            media = get_media(attachments) if attachments else None

            if not text and not media:
                continue

            new_message = Message(
                author_id=author['id'],
                author_name=author['username'],
                avatar=avatar,
                timestamp=message['timestamp'],
                text=text,
                reply=reply,
                media=media,
                chat=chat
            )

            messages.append(new_message)
            reply_map[author['id']] = new_message

    return messages, chats