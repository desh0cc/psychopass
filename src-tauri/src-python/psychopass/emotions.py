import onnxruntime as ort
import pickle
import numpy as np
from pathlib import Path

class EmotionClassifier:
    def __init__(self, model_path: Path, encoder_path: Path):
        self.session = ort.InferenceSession(
            str(model_path),
            providers=['CPUExecutionProvider']
        )
        
        # Load label encoder
        with open(encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)
        
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
    
    def predict(self, embedding: np.ndarray) -> str:
        """
        predict emotion class
        """
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: embedding.astype(np.float32)}
        )
        
        predicted_idx = np.argmax(np.asarray(outputs[0]), axis=1)[0]
        emotion = self.label_encoder.inverse_transform([predicted_idx])[0]
        
        return emotion
    
    def predict_probs(self, embedding: np.ndarray) -> dict[str, float]:
        """
        Predict emotion class probabilities
        """
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: embedding.astype(np.float32)}
        )
        
        probabilities = np.asarray(outputs[0])[0]
        emotions = self.label_encoder.classes_
        
        return {emotion: float(prob) for emotion, prob in zip(emotions, probabilities)}
    
    def predict_batch(self, embeddings: np.ndarray) -> list[str]:
        """
        Predict batch classes
        """
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: embeddings.astype(np.float32)}
        )
        
        predicted_indices = np.argmax(np.asarray(outputs[0]), axis=1)
        emotions = self.label_encoder.inverse_transform(predicted_indices)
        
        return list(emotions)