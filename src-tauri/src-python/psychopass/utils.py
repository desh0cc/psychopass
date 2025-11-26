import os, json

def find_files(dir: str) -> list[str]:
    found_files = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".json"):
                found_files.append(os.path.join(root, file))
    return found_files

def get_data(file: str) -> dict:
    data = None
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
    
def get_chat_type(type: str) -> str:
    chat_type: str = ""

    if "group" in type:
        chat_type = "group"
    elif "personal" in type:
        chat_type = type
    else:
        chat_type = type

    return chat_type

def get_media_type(type: str) -> str:
    if "video" in type:
        return "video"
    elif "animation" in type:
        return "animation"
    else:
        return "file"

def process_text_list(text_list):
    if isinstance(text_list, str):
        return text_list

    if isinstance(text_list, dict):
        return text_list.get("text", "")

    if isinstance(text_list, list):
        result = []
        for item in text_list:
            result.append(process_text_list(item)) 
        return "".join(result)

    return str(text_list)