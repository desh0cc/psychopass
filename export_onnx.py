import torch, torch.nn as nn, os
from sentence_transformers import SentenceTransformer
from onnxruntime.quantization import quantize_dynamic, QuantType

class STWrapper(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask):
        features = {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }

        out = self.model(features)
        return out["sentence_embedding"]

def export_to_onnx(name: str, path: str):
    model = SentenceTransformer(name)
    model.eval()

    wrapper = STWrapper(model)
    wrapper.eval()

    input_ids = torch.ones(1, 128, dtype=torch.long)
    attention_mask = torch.ones(1, 128, dtype=torch.long)

    onnx_path = os.path.join(path, "model.onnx")

    torch.onnx.export(
        wrapper,
        (input_ids, attention_mask),
        onnx_path,
        input_names=["input_ids", "attention_mask"],
        output_names=["embeddings"],
        opset_version=18,
        dynamic_axes={
            "input_ids": {0: "batch"},
            "attention_mask": {0: "batch"},
            "embeddings": {0: "batch"},
        },
        do_constant_folding=True,
        dynamo=False
    )

    quantize_dynamic(
        onnx_path,
        onnx_path,
        weight_type=QuantType.QInt8
    )