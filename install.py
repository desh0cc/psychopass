import os
from huggingface_hub import hf_hub_download
from export_onnx import export_to_onnx

MODELS_DIR = "src-tauri/models"
os.makedirs(MODELS_DIR, exist_ok=True)

models = {
    "clip-ViT-B-32-multilingual-v1": {
        "repo_id": "sentence-transformers/clip-ViT-B-32-multilingual-v1",
        "files": ["tokenizer.json", "config.json", "vocab.txt", "tokenizer_config.json"]
    },
    "clip-ViT-B-32": {
        "repo_id": "sayantan47/clip-vit-b32-onnx",
        "files": ["vocab.json", "config.json", "preprocessor_config.json", "special_tokens_map.json", "onnx/model_q4.onnx"]
    }
}

for name, data in models.items():
    model_dir = os.path.join(MODELS_DIR, name)
    os.makedirs(model_dir, exist_ok=True)
    print(f"\n[DEBUG] Processing model: {name} -> {model_dir}")

    # Export model to onnx
    if name.endswith("-v1"):
        print(f"[DEBUG] Exporting ONNX for {name}")
        export_to_onnx(data['repo_id'], model_dir)
        print(f"[DEBUG] Export complete for {name}")

    # Installing model files
    for file in data['files']:
        dest_path = os.path.join(model_dir, os.path.basename(file))
        dest_dir = os.path.dirname(dest_path)
        os.makedirs(dest_dir, exist_ok=True)

        if os.path.exists(dest_path):
            print(f"[DEBUG] File {file} already exists, skipped")
            continue

        print(f"[DEBUG] Downloading {file} from {data['repo_id']}")
        file_path = hf_hub_download(
            repo_id=data['repo_id'],
            filename=file
        )
        os.replace(file_path, dest_path)
        print(f"[DEBUG] Saved {file} -> {dest_path}")

print("\n All models processed successfully :p")
