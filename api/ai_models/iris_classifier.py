# # import tensorflow as tf
# import numpy as np
# from PIL import Image
# from .base_model import BaseModel

# class IrisClassifier(BaseModel):
#     def __init__(self, model_path):
#         self.model = tf.keras.models.load_model(model_path)
#         self.class_names = ['مصاب', 'غير مصاب']
#         # تعريف حجم الصورة الذي يتوقعه النموذج
#         self.img_height = 180
#         self.img_width = 180

#     def preprocess(self, image_file):
#         """
#         معالجة الصورة الأولية لتناسب إدخال النموذج.
#         """
#         img = Image.open(image_file).convert('RGB')
#         img = img.resize((self.img_width, self.img_height))
#         img_array = tf.keras.utils.img_to_array(img)
#         img_array = tf.expand_dims(img_array, 0)  # Create a batch
#         return img_array

#     def predict(self, image_file):
#         processed_image = self.preprocess(image_file)
#         predictions = self.model.predict(processed_image)
#         score = tf.nn.softmax(predictions[0])
        
#         predicted_class = self.class_names[np.argmax(score)]
#         confidence_ratio = np.max(score)
        
#         return predicted_class, confidence_ratio