import os
from psychopass.parser import parser
from psychopass.schemas import Message, Chat, Media
from tqdm import tqdm
from typing import List, Tuple
from psychopass.utils import find_files, get_data, get_chat_type, process_text_list, get_media_type

@parser.register("telegram")
def parse_telegram(dir_path: str) -> Tuple[List[Message], List[Chat]]:
    data_to_parse: list[dict] = [get_data(f) for f in find_files(dir_path)]

    chats: List[Chat] = []
    messages: List[Message] = []
    reply_map: dict[int,Message] = {}

    for data in tqdm(data_to_parse, desc="Reading data"):
        chat = Chat(
            id=0,
            name=data.get("name","uknown"),
            type=get_chat_type(data['type'])
        )

        chats.append(chat)

        for message in tqdm(data['messages'], desc="Reading messages"):
            media, text, reply = None, None, None

            if message['type'] != "message": continue

            # get text
            text = message['text']
            if isinstance(text, list):
                text = process_text_list(text)
            
            # get media
            photo: str = message.get('photo', None)
            # if photo: print(f"[DEBUG] Yo! there's photo: {photo}")
            if photo and "file not included" not in photo.lower():
                media = Media(
                    type="photo",
                    path=os.path.join(dir_path,photo)
                )
            
            file: str = message.get('file', None)
            # if file: print(f"[DEBUG] Yo! there's file: {file}")
            if file and ("file not included" not in file.lower() and "file exceeds maximum size" not in file.lower()):
                media_type = get_media_type(message.get('media_type', ""))
                thumbnail = message.get('thumbnail')
                media = Media(
                    type=media_type,
                    path=os.path.join(dir_path,file),
                    thumbnail=os.path.join(dir_path,thumbnail) if thumbnail else None
                )

            if not text and not media: continue

            # get reply 
            reply_id = message.get("reply_to_message_id")
            reply = reply_map.get(reply_id, None) if reply_id else None # considering it was already mapped

            # if reply: print(f"Yo! There's reply: {reply}")
            if media: print(f"Media: {media}")

            # message build
            mssg = Message(
                author_id=message['from_id'],
                author_name=message['from'],
                timestamp=message['date'],
                text=text,
                platform_id=message['id'],
                media=[media] if media is not None else None,
                reply=reply,
                chat=chat
            )

            messages.append(mssg)
            reply_map[message['id']] = mssg 

    return messages,chats