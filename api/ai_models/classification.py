import numpy as np
import onnxruntime as ort
from .utils import softmax
import cv2
class DiabetesClassifier:
    def __init__(self, model_path: str, class_names: list, target_size: tuple = (512, 512)):
        self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.class_names = class_names
        self.target_size = target_size

    def preprocess(self, cropped_iris_image: np.ndarray) -> np.ndarray:
        # تغيير الحجم، التطبيع، تبديل الأبعاد، وإضافة بُعد الدفعة
        img_resiz = cv2.resize(cropped_iris_image, self.target_size)
        img_np = np.array(img_resiz, dtype=np.float32) / 255.0
        img_np = np.transpose(img_np, (2, 0, 1))
        img_input = np.expand_dims(img_np, axis=0)
        return img_input

    def predict(self, cropped_iris_image: np.ndarray) -> tuple[str, float]:
        processed_image = self.preprocess(cropped_iris_image)
        outputs = self.session.run([self.output_name], {self.input_name: processed_image})[0]
        
        probabilities = softmax(outputs)
        
        predicted_class_idx = np.argmax(probabilities, axis=1)[0]
        confidence_score = float(probabilities[0, predicted_class_idx])
        predicted_class_name = self.class_names[predicted_class_idx]
        
        return predicted_class_name, confidence_score