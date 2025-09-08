# from PIL import Image
# import numpy as np
# from .base_onnx_model import BaseONNXModel

# class IrisSegmenter(BaseONNXModel):
#     """
#     فئة لمعالجة نموذج استخراج القزحية.
#     """
#     def __init__(self, model_path):
#         super().__init__(model_path)
#         # تحديد أبعاد المدخلات للنموذج
#         self.input_shape = self.session.get_inputs()[0].shape[2:] # (height, width)

#     def preprocess(self, image):
#         # تغيير حجم الصورة لتناسب النموذج
#         resized_image = image.resize(self.input_shape[::-1]) # (width, height)
#         img_array = np.array(resized_image, dtype=np.float32) / 255.0
#         # إضافة بعد الدفعة وتغيير الترتيب إلى NCHW
#         img_array = np.transpose(img_array, (2, 0, 1))
#         img_array = np.expand_dims(img_array, axis=0)
#         return img_array

#     def predict(self, image: Image.Image) -> Image.Image:
#         """
#         يستقبل صورة PIL ويُرجع صورة PIL جديدة تحتوي على القزحية المقتطعة.
#         """
#         original_width, original_height = image.size
#         processed_image = self.preprocess(image)
        
#         # تشغيل الاستدلال
#         outputs = self.session.run(self.output_names, {self.input_name: processed_image})
        
#         # --- هذا الجزء يعتمد كليًا على مخرجات نموذجك ---
#         # لنفترض أن النموذج يُرجع إحداثيات (x_min, y_min, x_max, y_max)
#         # كمثال، قد تكون المخرجات في `outputs[0]`
#         boxes = outputs[0][0] # افترض أن هذا هو شكل المخرجات
        
#         # تحويل الإحداثيات المنسوبة إلى إحداثيات بكسل حقيقية
#         x_min = int(boxes[0] * original_width)
#         y_min = int(boxes[1] * original_height)
#         x_max = int(boxes[2] * original_width)
#         y_max = int(boxes[3] * original_height)

#         # اقتصاص الصورة الأصلية بناءً على الإحداثيات
#         cropped_iris = image.crop((x_min, y_min, x_max, y_max))
        
#         return cropped_iris