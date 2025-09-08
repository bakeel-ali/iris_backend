# import onnxruntime as ort
# import numpy as np

# class BaseONNXModel:
#     """
#     فئة أساسية لتحميل وتشغيل نماذج ONNX.
#     """
#     def __init__(self, model_path):
#         try:
#             self.session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
#             self.input_name = self.session.get_inputs()[0].name
#             self.output_names = [output.name for output in self.session.get_outputs()]
#         except Exception as e:
#             # يمكنك استخدام logging هنا لتسجيل الخطأ
#             print(f"Error loading ONNX model at {model_path}: {e}")
#             raise

#     def softmax(self, x):
#         e_x = np.exp(x - np.max(x))
#         return e_x / e_x.sum(axis=-1, keepdims=True)