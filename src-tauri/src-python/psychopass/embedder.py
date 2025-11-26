import os
import numpy as np
import onnxruntime as ort
from PIL import Image
from sentence_transformers import SentenceTransformer
from typing import List

class Embedder:
    def __init__(self, textM_path: str, imgM_path: str, batch_size: int = 32):
        self.device = "cuda" if "GPUExecutionProvider" in ort.get_available_providers() else "cpu"
        self.batch_size = batch_size

        self.text_embedder = SentenceTransformer(
            textM_path,
            device=self.device,
            local_files_only=True
        )

        self.image_embedder = SentenceTransformer(
            imgM_path,
            device=self.device,
            local_files_only=True
        )

    def embed_texts(self,texts: List[str]) -> np.ndarray:
        embeddings = self.text_embedder.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=True,
            normalize_embeddings=False,
            convert_to_numpy=True
        )

        return embeddings


    def embed_images(self,image_paths: List[str]) -> np.ndarray:
        images = []

        for path in image_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image not found: {path}")

            img = Image.open(path).convert("RGB")
            images.append(img)

        embeddings = self.image_embedder.encode(
            images,
            batch_size=self.batch_size,
            show_progress_bar=True,
            normalize_embeddings=False,
            convert_to_numpy=True
        )

        return embeddings
