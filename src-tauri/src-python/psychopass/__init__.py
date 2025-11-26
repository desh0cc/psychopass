import os, random, configparser
import asyncio, math, logging
import numpy as np
import functools

from pathlib import Path
from appdirs import user_config_dir
from typing import Annotated, Union, Optional, List, Tuple, Callable, Any
from anyio.from_thread import start_blocking_portal
from pytauri.path import PathResolver
from pytauri import (
    Commands,
    builder_factory,
    context_factory,
    App,
    AppHandle,
    Manager,
    Emitter
)
from pytauri.webview import WebviewWindow
from concurrent.futures import ThreadPoolExecutor

# App dirs
APP_DIR = user_config_dir("psychopass", appauthor="desh0cc", roaming=False)
CFG_DIR = os.path.join(APP_DIR, "config.cfg")
DB_DIR = os.path.join(APP_DIR, "psychopass.db")
CACHE_DIR = os.path.join(APP_DIR, "cache")
MEM_DIR = os.path.join(APP_DIR, "memory")

# Main app func.
from psychopass.parser import parser, ChatParser
from psychopass.embedder import Embedder
from psychopass.emotions import EmotionClassifier
from psychopass.database import UserDB
from psychopass.memory import Memory
from psychopass.schemas import * # type: ignore

memory: Memory
embedder: Embedder
classifier: EmotionClassifier
parser: ChatParser = parser
database: UserDB = UserDB(DB_DIR,CACHE_DIR)

# Logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("Python backend started")

# multithreading
executor = ThreadPoolExecutor(max_workers=3)

# pyTauri commands
commands: Commands = Commands()

def handle_errors(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"[ERROR] error in {func.__name__}: {str(e)}", exc_info=True)
            
            app_handle = None
            
            if args and isinstance(args[0], dict):
                app_handle = args[0].get('app_handle')
            
            if not app_handle:
                for arg in args:
                    if isinstance(arg, AppHandle):
                        app_handle = arg
                        break
            
            if not app_handle:
                app_handle = kwargs.get('app_handle')
            
            if app_handle:
                try:
                    Emitter.emit(app_handle, "error_event", ErrorEvent(
                        func=func.__name__,
                        error=str(e)
                    ))
                    print(f"[DEBUG] Error event emitted for {func.__name__}")
                except Exception as emit_error:
                    logging.error(f"Failed to emit error event: {emit_error}")
            else:
                logging.warning("AppHandle not found, cannot emit error to frontend")
            
            return None
    return wrapper

def get_resource_path(manager: Union[App, AppHandle, WebviewWindow]) -> dict[str, Path]:
    resolver: PathResolver = Manager.path(manager)
    resource_dir = resolver.resource_dir()

    model_path = resource_dir / "psychopass.onnx"
    encoder_path = resource_dir / "label_encoder.pkl"
    img_embedder = resource_dir / "models" / "clip-ViT-B-32"
    text_embedder = resource_dir / "models" / "clip-ViT-B-32-multilingual-v1"

    return {
        "model": model_path,
        "encoder": encoder_path,
        "text_embedder": text_embedder,
        "img_embedder": img_embedder
    }

@commands.command()
@handle_errors
async def load_resources(app_handle: AppHandle) -> None:
    global embedder, classifier, memory

    parser.load_parsers()
    paths = get_resource_path(app_handle)

    classifier = EmotionClassifier(paths["model"], paths["encoder"])
    embedder = Embedder(str(paths['text_embedder']), str(paths["img_embedder"]))
    memory = Memory(embedder, MEM_DIR)

    print("[LOG] Psychopass AI loaded successfully")

@commands.command()
@handle_errors
async def get_username() -> str:
    return os.getlogin()

@commands.command()
@handle_errors
async def get_random_emoji(body: Annotated[EmojiRequest, "body"]) -> int:
    return random.randint(0, body.length - 1)

@commands.command()
@handle_errors
async def create_database() -> None:
    database._init_db()

@commands.command()
@handle_errors
async def get_profile_id(body: Annotated[UserProfile, "body"]) -> Optional[Profile]:
    return database.get_profile(body.user_id)

@commands.command()
@handle_errors
async def get_emotion_messages(body: Annotated[EmotionRequest, "body"]) -> List[Message]:
    return database.get_messages_by_emotion(body.id, body.emotion)

@commands.command()
@handle_errors
async def get_emotion_percentage() -> EmotionStats:
    return database.get_emotion_percentages()

@commands.command()
@handle_errors
async def update_chat(body: Annotated[Chat,'body']) -> bool:
    return await database.update_chat(body.id,name=body.name,avatar=body.avatar)

@commands.command()
@handle_errors
async def create_cfg() -> str:
    # does cfg exists?

    os.makedirs(os.path.dirname(CFG_DIR), exist_ok=True)

    if not os.path.exists(CFG_DIR):
        config = configparser.ConfigParser()
        config.add_section("Preferences")
        config.set("Preferences", "theme", "dark")
        config.set("Preferences", "language", "en")
        config.set("Preferences", "color", "#539ae2")
        
        with open(CFG_DIR, "w", encoding='utf-8') as f:
            config.write(f)
    
        return f"Config was succesfully created at {CFG_DIR} :P"
    return f"Config already exists!"

@commands.command()
@handle_errors
async def get_config_value(body: Annotated[KeyRequest, "body"]) -> str:
    if not os.path.exists(CFG_DIR):
        await create_cfg()
        
    config = configparser.ConfigParser()
    config.read(CFG_DIR, encoding="utf-8")

    if config.has_option("Preferences", body.key):
        return config.get("Preferences", body.key)
    return f"Key {body.key} isn't there, I'm sorry bud"
    
@commands.command()
@handle_errors
async def change_config_value(body: Annotated[KeyRequest, "body"]) -> bool:
    if not os.path.exists(CFG_DIR):
        await create_cfg()

    config = configparser.ConfigParser()
    config.read(CFG_DIR, encoding='utf-8')

    if config.has_option("Preferences", body.key):
        config.set("Preferences", body.key, body.value)

        with open(CFG_DIR, 'w', encoding='utf-8') as f:
            config.write(f)

        return True
    return False

def process_batch(batch: list[Message]) -> np.ndarray:
    embeddings: list[Optional[np.ndarray]] = [None] * len(batch)
    
    text_messages, text_inputs, text_indices = [], [], []
    image_messages, image_inputs, image_indices = [], [], []

    for idx, msg in enumerate(batch):
        if msg.text and msg.text.strip():
            text_messages.append(msg)
            text_inputs.append(msg.text)
            text_indices.append(idx)
        elif msg.media:
            img = None
            for m in msg.media:
                if m.type == "photo":
                    img = m.path
                    break
                if m.thumbnail:
                    img = m.thumbnail
            if img:
                image_messages.append(msg)
                image_inputs.append(img)
                image_indices.append(idx)

    if text_messages:
        text_embeddings = embedder.embed_texts(text_inputs) 
        for emb_idx, batch_idx in enumerate(text_indices):
            embeddings[batch_idx] = text_embeddings[emb_idx]

    if image_messages:
        image_embeddings = embedder.embed_images(image_inputs)
        for emb_idx, batch_idx in enumerate(image_indices):
            if embeddings[batch_idx] is None:
                embeddings[batch_idx] = image_embeddings[emb_idx]

    embedding_dim = None
    for emb in embeddings:
        if emb is not None:
            embedding_dim = len(emb)
            break
    
    if embedding_dim is None:
        raise ValueError("No valid embeddings found in batch")
    
    for idx in range(len(embeddings)):
        if embeddings[idx] is None:
            embeddings[idx] = np.zeros(embedding_dim, dtype=float)
    
    return np.array(embeddings)
    

def add_messages_to_vector_db(messages: list[Message], batch_size: int = 100):
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        
        text_messages, text_inputs = [], []
        image_messages, image_inputs = [], []
        
        for msg in batch:
            if not msg.id:
                continue
                
            if msg.text and msg.text.strip():
                text_messages.append(msg)
                text_inputs.append(msg.text)
            elif msg.media:
                img = None
                for m in msg.media:
                    if m.type == "photo":
                        img = m.path
                        break
                    if m.thumbnail:
                        img = m.thumbnail
                if img:
                    image_messages.append(msg)
                    image_inputs.append(img)
        
        if text_messages:
            memory.add_text(text_messages, text_inputs)
        
        if image_messages:
            memory.add_images(image_messages, image_inputs)

def get_emotion_class(app_handle: AppHandle, messages: list[Message], current_fn: str, batch_size: int = 16) -> list[str]:
    predictions = []
    num_batches = math.ceil(len(messages) / batch_size)

    for batch_idx, i in enumerate(range(0, len(messages), batch_size), start=1):
        batch = messages[i:i + batch_size]

        Emitter.emit(
            app_handle,
            "emotion_analyzing",
            Download(
                current_file=current_fn,
                progress=batch_idx,
                max_progress=num_batches
            )
        )

        batch_predictions = classifier.predict_batch(process_batch(batch))
        predictions.extend(batch_predictions)

    return predictions

async def parse_messages(app_handle: AppHandle, body: Annotated[FileDir, "body"]) -> Tuple[List[Message], List[Chat]]:
    loop = asyncio.get_running_loop()
    messages, chats = parser.parse(body.platform, body.path)

    emotions = await loop.run_in_executor(
        executor,
        get_emotion_class,
        app_handle,
        messages,
        os.path.basename(body.path)
    )

    for msg, emo in zip(messages, emotions):
        msg.emotion = emo

    return messages, chats

@commands.command()
@handle_errors
async def analyze_messages(app_handle: AppHandle, body: Annotated[FileDir, "body"]) -> None:
    batch_data = await parse_messages(app_handle, body)
    messages, chats = batch_data
    
    await database.add_messages_batch(body.platform, messages, chats)
    
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        executor,
        add_messages_to_vector_db,
        messages
    )
    database.update_stats_auto()

@commands.command()
@handle_errors
async def get_statistics() -> Optional[dict]:
    return database.get_stats()

@commands.command()
@handle_errors
async def get_profiles() -> list[Profile]:
    return database.get_profiles()

@commands.command()
@handle_errors
async def get_chats() -> List[Chat]:
    return database.get_chats()

@commands.command()
@handle_errors
async def get_chat(body: Annotated[ChatRequest,"body"]) -> Optional[Chat]:
    return database.get_chat(body.chat_id)

@commands.command()
@handle_errors
async def get_chat_messages(body: Annotated[ChatRequest, "body"]) -> List[Message]:
    return database.get_chat_messages(body.chat_id)

@commands.command()
@handle_errors
async def get_emotions(body: Annotated[UserProfile, 'body']) -> EmotionStats:
    return database.get_emotion_percentages(body.user_id)

@commands.command()
@handle_errors
async def update_profile(body: Annotated[ProfileUpdate, "body"]) -> str:
    return await database.update_profile(body.id,global_name=body.global_name,avatar=body.avatar)

@commands.command()
@handle_errors
async def merge_profiles(body: Annotated[MergeRequest, "body"]) -> str:
    return database.merge_profiles(body.primary_id, body.secondary_ids)

@commands.command()
@handle_errors
async def unmerge_profiles(body: Annotated[MergeRequest, "body"]) -> str:
    return database.unmerge_profiles(body.primary_id, body.secondary_ids)

@commands.command()
@handle_errors
async def search_messages(body: Annotated[SearchQuery, "body"]) -> Optional[List[Message]]:
    if body.engine == "vector":
        return await vector_search(body.query)
    else:
        return await linear_search(body.query)

async def vector_search(query: str) -> Optional[List[Message]]:
    messages: List[Message] = []

    embedding = embedder.embed_texts([query])[0]
    hits = memory.search_embedding(embedding, top_k=5)

    for k in hits:
        message = database.get_message(k['id'])
        if message and message not in messages:
            messages.append(message)

    return messages

async def linear_search(query: str):
    return database.search_messages(query)

@commands.command()
async def get_yearly_emotions() -> EmotionStatsByYear:
    return database.get_yearly_emotions()

def main() -> int:
    with start_blocking_portal("asyncio") as portal:  # or `trio`
        app = builder_factory().build(
            context=context_factory(),
            invoke_handler=commands.generate_handler(portal),
        )
        exit_code = app.run_return()
        return exit_code