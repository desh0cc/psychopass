import importlib, pkgutil
from typing import Callable, Dict, Tuple, List
from psychopass.schemas import Message, Chat

class ChatParser:
    def __init__(self):
        self.parsers: Dict[str, Callable[[str], Tuple[List[Message], List[Chat]]]] = {}

    def register(self, platform: str):
        def decorator(func):
            print(f"[Parser] Registered parser: {platform}")
            self.parsers[platform] = func
            return func
        return decorator

    def parse(self, platform: str, path: str):
        if platform not in self.parsers:
            raise ValueError(f"No parser for platform: {platform}")
        return self.parsers[platform](path)

    def load_parsers(self):
        from psychopass import parsers as parsers_pkg
        for loader, name, ispkg in pkgutil.iter_modules(parsers_pkg.__path__):
            print(f"[Parser] Loading parser: {name}")
            importlib.import_module(f"psychopass.parsers.{name}")

parser = ChatParser()