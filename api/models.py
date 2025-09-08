from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone

# 1. نموذج المستخدم (User)
# نوسع النموذج الافتراضي لإضافة حقول إذا احتجنا
class User(AbstractUser):
    # يمكنك إضافة حقول مثل رقم الهاتف، التخصص، إلخ.
    email = models.EmailField(unique=True) # جعل البريد الإلكتروني فريدًا ومطلوبًا
    
    USERNAME_FIELD = 'email' # تسجيل الدخول باستخدام البريد الإلكتروني
    REQUIRED_FIELDS = ['username'] # لا يزال اسم المستخدم مطلوبًا عند إنشاء superuser

# 2. نموذج المريض (Patient)
class Patient(models.Model):
    # يربط كل مريض بالمستخدم (الطبيب) الذي أضافه
    doctor = models.ForeignKey(User, related_name='patients', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # هذا هو التحديث المهم:
        # يضمن أن تركيبة الطبيب واسم المريض فريدة دائمًا.
        # يمنع إنشاء مريضين بنفس الاسم لنفس الطبيب.
        unique_together = ('doctor', 'name')
        
    def __str__(self):
        return self.name

# 3. نموذج التشخيص (Diagnosis)
# دالة لتحديد مسار حفظ الصورة
# def get_diagnosis_image_path(instance, filename):
#     return f'diagnoses/{instance.patient.id}/{filename}'
# دالة لتحديد مسار حفظ الصورة
def get_diagnosis_image_path(instance, filename):
    # الحصول على السنة، الشهر واليوم من تاريخ التشخيص
    diagnosis_date = instance.diagnosis_date or instance.patient.diagnoses.first().diagnosis_date
    return f'diagnoses/{instance.patient.id}/{diagnosis_date.year}/{diagnosis_date.month:02d}/{diagnosis_date.day:02d}/{filename}'

class Diagnosis(models.Model):
    patient = models.ForeignKey(Patient, related_name='diagnoses', on_delete=models.CASCADE)
    # حقل الصورة، سيتم حفظ الصور في media/diagnoses/<patient_id>/
    iris_image = models.ImageField(upload_to=get_diagnosis_image_path)
    results = models.CharField(max_length=50) # e.g., "مصاب", "غير مصاب"
    ratio = models.FloatField() # نسبة الثقة
    note = models.TextField(blank=True, null=True) # ملاحظات إضافية
    diagnosis_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnosis for {self.patient.name} on {self.diagnosis_date.date()}"

# نموذج لتخزين رمز إعادة تعيين كلمة المرور
class ResetCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at