import cv2
import numpy as np
from .segmentation import IrisSegmentationModel, MultilabelSegmentationBinarization
from .classification import DiabetesClassifier
from .utils import crop_iris_image_color

class DiagnosisPipeline:
    def __init__(self, segmenter_path, classifier_path, class_labels):
        print("Initializing AI Diagnosis Pipeline...")
        self.segmentation_model = IrisSegmentationModel(model_path=segmenter_path)
        
        # إعدادات معالجة الأقنعة
        binarization_params = MultilabelSegmentationBinarization.Parameters()
        self.binarization = MultilabelSegmentationBinarization(params=binarization_params)
        
        # تحميل نموذج التصنيف
        self.classification_model = DiabetesClassifier(model_path=classifier_path, class_names=class_labels)
        print("AI Diagnosis Pipeline initialized successfully.")

    def run(self, image_file):
        # 1. قراءة الصورة باستخدام OpenCV
        # نحول ملف الصورة من Django إلى مصفوفة numpy
        image_bytes = np.frombuffer(image_file.read(), np.uint8)
        original_image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        height, width = original_image.shape[:2]

        # 2. تشغيل نموذج التجزئة
        segmentation_map = self.segmentation_model.run(gray_image, width, height)

        # 3. استخراج قناع القزحية
        geometry_mask, _ = self.binarization.run(segmentation_map)
        iris_mask = geometry_mask.iris_mask.astype(np.uint8) * 255

        # 4. تحسين القناع (Convex Hull)
        contours, _ = cv2.findContours(iris_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            raise ValueError("No iris contour found in the image.")
        all_points = np.vstack(contours)
        hull = cv2.convexHull(all_points)
        cv2.fillPoly(iris_mask, [hull], 255)

        # 5. تطبيق القناع على الصورة الأصلية
        masked_image = cv2.bitwise_and(original_image, original_image, mask=iris_mask)

        # 6. اقتصاص القزحية باستخدام الدالة المخصصة
        cropped_iris = crop_iris_image_color(masked_image)
        if cropped_iris.size == 0:
            raise ValueError("Cropping resulted in an empty image.")

        # 7. تشغيل نموذج التصنيف على الصورة المقتصة
        result, confidence = self.classification_model.predict(cropped_iris)
        
        return result, confidence
    
# onnxruntime.capi.onnxruntime_pybind11_state.NoSuchFile: [ONNXRuntimeError] : 3 : NO_SUCHFILE : Load model from D:\IDP_Final_Project\iris_backend\api/ai_models/saved_models/iris_segmentation.onnx failed:Load model D:\IDP_Final_Project\iris_backend\api/ai_models/saved_models/iris_segmentation.onnx failed. File doesn't exist