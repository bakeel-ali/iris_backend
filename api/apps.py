from django.apps import AppConfig
from django.conf import settings
import os

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    # تعريف مسارات النماذج
    segmenter_path = os.path.join(settings.BASE_DIR, 'api/ai_models/saved_models/iris_semseg_upp_scse_mobilenetv2.onnx')
    classifier_path = os.path.join(settings.BASE_DIR, 'api/ai_models/saved_models/best_cpu_without_simplify.onnx')
    # class_labels = ['non-diabetic', 'diabetic']
    # تحديث ترتيب الفئات ليتطابق مع: {0: 'diabetic', 1: 'non-diabetic'}
    class_labels = ['diabetic', 'non-diabetic']

    # تحميل خط الأنابيب بأكمله ككائن واحد
    from .ai_models.diagnosis_pipeline import DiagnosisPipeline
    DIAGNOSIS_PIPELINE = DiagnosisPipeline(segmenter_path, classifier_path, class_labels)

# from django.apps import AppConfig
# from django.conf import settings
# import os

# class ApiConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'api'
    
#     # تحميل النموذج مرة واحدة فقط عند بدء تشغيل الخادم
#     model_path = os.path.join(settings.BASE_DIR, 'api/ai_models/saved_model/iris_model.h5')
#     # يمكنك استخدام متغير عالمي أو singleton pattern
#     from .ai_models.iris_classifier import IrisClassifier
#     IRIS_CLASSIFIER_MODEL = IrisClassifier(model_path)