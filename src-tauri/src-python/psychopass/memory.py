import chromadb, uuid
import numpy as np
from psychopass.embedder import Embedder
from psychopass.schemas import Message

class Memory:
    def __init__(self, embedder: Embedder, persist_path: str):
        self.embedder = embedder

        self.client = chromadb.PersistentClient(path=persist_path)

        self.collection = self.client.get_or_create_collection(
            name="messages",
            metadata={"hnsw:space": "cosine"}
        )

    def add_batch(self, items):
        ids = [str(x["id"]) for x in items]
        embeddings = [x["embedding"] for x in items]
        documents = [x["document"] for x in items]
        metadatas = [x["metadata"] for x in items]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def add_text(self, messages: list[Message], texts: list[str]):
        embeddings = self.embedder.embed_texts(texts)

        items = []
        for msg, emb, text in zip(messages, embeddings, texts):
            uniq_id = uuid.uuid4().int

            items.append({
                "id": uniq_id,
                "embedding": emb,
                "document": text,
                "metadata": {
                    "type": "text",
                    "original_id": msg.id,
                    "chat_id": msg.chat_id if msg.chat_id else "",
                    "user_id": msg.platform_id if msg.platform_id else ""
                }
            })

        self.add_batch(items)
        return embeddings


    def add_images(self, messages: list[Message], images: list[str]):
        embeddings = self.embedder.embed_images(images)

        items = []
        for msg, emb in zip(messages, embeddings):
            uniq_id = uuid.uuid4().int

            items.append({
                "id": uniq_id,
                "embedding": emb,
                "document": "<image>",
                "metadata": {
                    "type": "image",
                    "original_id": msg.id,
                    "chat_id": msg.chat_id if msg.chat_id else "",
                    "user_id": msg.platform_id if msg.platform_id else ""
                }
            })

        self.add_batch(items)
        return embeddings

    def search_embedding(self, emb, top_k):
        result = self.collection.query(
            query_embeddings=[emb],
            n_results=top_k
        )

        hits = []

        ids = result["ids"][0] if result["ids"] else []
        docs = result["documents"][0] if result["documents"] else []
        metas = result["metadatas"][0] if result["metadatas"] else []
        dists = result["distances"][0] if result["distances"] else []

        for i in range(len(ids)):
            hits.append({
                "id": metas[i]["original_id"],
                "text": docs[i],
                "chat_id": metas[i]["chat_id"],
                "user_id": metas[i]["user_id"],
                "type": metas[i]["type"],
                "score": 1 - float(dists[i]),
            })

        return hits