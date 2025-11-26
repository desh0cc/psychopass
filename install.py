import os
from sentence_transformers import SentenceTransformer

MODELS_DIR = "src-tauri/models"
os.makedirs(MODELS_DIR, exist_ok=True)

MODELS = [
    "sentence-transformers/clip-ViT-B-32-multilingual-v1",
    "sentence-transformers/clip-ViT-B-32"
]

for model_name in MODELS:
    print(f"[INFO] Loading {model_name}...")
    model = SentenceTransformer(model_name)  # this downloads it automatically

    # Save locally
    local_path = os.path.join(MODELS_DIR, model_name.split("/")[-1])
    model.save(local_path)
    print(f"[OK] {model_name} saved to {local_path}\n")
