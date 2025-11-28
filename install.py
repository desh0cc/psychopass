import shutil
from pathlib import Path
from huggingface_hub import hf_hub_download
from export_onnx import export_to_onnx

# Get the script's directory to ensure correct paths
SCRIPT_DIR = Path(__file__).parent.absolute()
MODELS_DIR = SCRIPT_DIR / "src-tauri" / "models"

print(f"[DEBUG] Script directory: {SCRIPT_DIR}")
print(f"[DEBUG] Models directory: {MODELS_DIR}")

MODELS_DIR.mkdir(parents=True, exist_ok=True)

models = {
    "clip-ViT-B-32-multilingual-v1": {
        "repo_id": "sentence-transformers/clip-ViT-B-32-multilingual-v1",
        "files": ["tokenizer.json", "config.json", "vocab.txt"]
    },
    "clip-ViT-B-32": {
        "repo_id": "sayantan47/clip-vit-b32-onnx",
        "files": ["vocab.json", "config.json", "preprocessor_config.json", "special_tokens_map.json", "onnx/model_q4.onnx"]
    }
}

for name, data in models.items():
    model_dir = MODELS_DIR / name
    model_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[DEBUG] Processing model: {name} -> {model_dir}")

    # Export model to onnx
    if name.endswith("-v1"):
        print(f"[DEBUG] Exporting ONNX for {name}")
        export_to_onnx(data['repo_id'], str(model_dir))
        print(f"[DEBUG] Export complete for {name}")

    # Installing model files
    for file in data['files']:
        dest_path = model_dir / Path(file).name
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        if dest_path.exists():
            print(f"[DEBUG] File {file} already exists, skipped")
            continue

        try:
            print(f"[DEBUG] Downloading {file} from {data['repo_id']}")
            file_path = hf_hub_download(
                repo_id=data['repo_id'],
                filename=file
            )

            shutil.copy2(file_path, str(dest_path))
            print(f"[DEBUG] Saved {file} -> {dest_path}")
        except Exception as e:
            print(f"[WARNING] Could not download {file}: {e}")
            continue

print("\n All models processed successfully :p")