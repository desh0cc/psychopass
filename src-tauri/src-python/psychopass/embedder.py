import os, json
import numpy as np
import onnxruntime as ort
import albumentations as A

from PIL import Image
from tokenizers import Tokenizer
from typing import List
from tqdm import tqdm

class Embedder:
    def __init__(self, textM_path: str, imgM_path: str, batch_size: int = 32):
        """Initialize ONNX Runtime embedder for text and images"""
        self.batch_size = batch_size
        self.device = ['GPUExecutionProvider'] if "GPUExecutionProvider" in ort.get_available_providers() else ["CPUExecutionProvider"]

        # Load text model and tokenizer
        text_onnx_path = os.path.join(textM_path, "model.onnx")
        self.text_session = ort.InferenceSession(text_onnx_path, providers=self.device)
        
        tokenizer_path = os.path.join(textM_path, "tokenizer.json")
        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=128)
        self.tokenizer.enable_truncation(max_length=128)
        
        # Load image model
        img_onnx_path = os.path.join(imgM_path, "model_q4.onnx")
        self.image_session = ort.InferenceSession(img_onnx_path, providers=self.device)
        
        # Load config for image processor
        config_path = os.path.join(imgM_path, "preprocessor_config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        crop_size = config.get("crop_size")
        height = crop_size.get("height")
        width = crop_size.get("width")
        mean = config.get("image_mean")
        std = config.get("image_std")
        shortest_edge = config.get("size", {}).get("shortest_edge", 224)
        
        self.image_transform = A.Compose([
            A.SmallestMaxSize(max_size=shortest_edge, interpolation=3),
            A.CenterCrop(height=height, width=width),
            A.Normalize(mean=mean, std=std, max_pixel_value=255.0),
        ])
        
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), self.batch_size), desc="Embedding texts"):
            batch_texts = texts[i:i + self.batch_size]
            
            encodings = self.tokenizer.encode_batch(batch_texts)
            input_ids = np.array([enc.ids for enc in encodings], dtype=np.int64)
            attention_mask = np.array([enc.attention_mask for enc in encodings], dtype=np.int64)
            
            onnx_inputs = {
                "input_ids": input_ids,
                "attention_mask": attention_mask
            }
            
            outputs = self.text_session.run(None, onnx_inputs)
            embeddings = outputs[0]
            all_embeddings.append(embeddings)
        
        return np.vstack(all_embeddings)
    
    def embed_images(self, image_paths: List[str]) -> np.ndarray:
        """Generate embeddings for a list of images"""
        all_embeddings = []
        
        for i in tqdm(range(0, len(image_paths), self.batch_size), desc="Embedding images"):
            batch_paths = image_paths[i:i + self.batch_size]
            
            images = []
            for path in batch_paths:
                if not os.path.exists(path):
                    continue
                
                img = Image.open(path).convert("RGB")
                img_array = np.array(img)
                
                transformed = self.image_transform(image=img_array)
                img_normalized = transformed['image']
                
                img_chw = np.transpose(img_normalized, (2, 0, 1))
                images.append(img_chw)

            if not images:
                print(f"[DEBUG] No valid images found in batch: {batch_paths}")
                continue
            
            pixel_values = np.stack(images).astype(np.float32)

            onnx_inputs = {
                "pixel_values": pixel_values,
                "input_ids": np.zeros((len(images), 1), dtype=np.int64),
                "attention_mask": np.zeros((len(images), 1), dtype=np.int64)
            }
            
            outputs = self.image_session.run(None, onnx_inputs)
            embeddings = outputs[3]
            all_embeddings.append(embeddings)
        
        if all_embeddings:
            return np.vstack(all_embeddings)
        else:
            return np.zeros((0, 512), dtype=np.float32)