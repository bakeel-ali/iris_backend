import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Diagnosis
from django.conf import settings

@receiver(post_delete, sender=Diagnosis)
def delete_iris_image(sender, instance, **kwargs):
    """
    حذف صورة التشخيص من MEDIA_ROOT عند حذف الـ record
    وأيضًا حذف المجلدات الفارغة الخاصة بالمريض
    """
    if instance.iris_image:
        # 1. حذف الملف نفسه
        image_path = instance.iris_image.path
        instance.iris_image.delete(save=False)

        # 2. محاولة حذف المجلدات الفارغة صعودًا حتى جذر media/diagnoses
        dir_path = os.path.dirname(image_path)
        diagnoses_root = os.path.join(settings.MEDIA_ROOT, "diagnoses")

        while dir_path.startswith(diagnoses_root):
            try:
                os.rmdir(dir_path)  # يحذف فقط إذا كان المجلد فارغ
            except OSError:
                break  # يتوقف إذا المجلد فيه ملفات ثانية
            dir_path = os.path.dirname(dir_path)
