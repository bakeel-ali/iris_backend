from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

# from iris_backend.api.apps import ApiConfig
from .apps import ApiConfig 

from .permissions import IsOwner
from .models import Patient, Diagnosis, ResetCode
# API لتغيير كلمة المرور بعد التحقق من الرمز
from django.contrib.auth import get_user_model
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        if not all([email, code, new_password]):
            return Response({'error': 'يرجى إدخال البريد الإلكتروني، الرمز، وكلمة المرور الجديدة.'}, status=status.HTTP_400_BAD_REQUEST)
        # تحقق من وجود الرمز وصحته
        try:
            reset_code = ResetCode.objects.get(email=email, code=code)
        except ResetCode.DoesNotExist:
            return Response({'error': 'رمز التحقق غير صحيح أو البريد الإلكتروني غير صحيح.'}, status=status.HTTP_400_BAD_REQUEST)
        # تحقق من صلاحية الرمز
        if not reset_code.is_valid():
            reset_code.delete()
            return Response({'error': 'انتهت صلاحية رمز التحقق.'}, status=status.HTTP_400_BAD_REQUEST)
        # تغيير كلمة المرور
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'المستخدم غير موجود.'}, status=status.HTTP_404_NOT_FOUND)
        user.set_password(new_password)
        user.save()
        # حذف الرمز بعد الاستخدام
        reset_code.delete()
        return Response({'message': 'تم تغيير كلمة المرور بنجاح.'}, status=status.HTTP_200_OK)
from .serializers import UserSerializer, PatientSerializer, DiagnosisSerializer, LoginSerializer, RegisterSerializer

from django.core.mail import send_mail
from django.utils import timezone
import random


# 1. عرض لإنشاء حساب جديد

# API لإرسال رمز إعادة تعيين كلمة المرور
class SendResetCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'يرجى إدخال البريد الإلكتروني.'}, status=status.HTTP_400_BAD_REQUEST)
        # تحقق من وجود المستخدم
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(email=email).exists():
            return Response({'error': 'البريد الإلكتروني غير مسجل.'}, status=status.HTTP_404_NOT_FOUND)
        # إنشاء رمز تحقق عشوائي
        code = str(random.randint(100000, 999999))
        expires = timezone.now() + timezone.timedelta(minutes=10)
        ResetCode.objects.create(email=email, code=code, expires_at=expires)

        try:
            send_mail(
                'رمز إعادة تعيين كلمة المرور',
                f'رمز التحقق الخاص بك هو: {code}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({'message': 'تم إرسال رمز التحقق إلى بريدك الإلكتروني.'}, status=status.HTTP_200_OK)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'خطأ أثناء إرسال البريد الإلكتروني: {str(e)}')
            return Response({'error': 'حدث خطأ أثناء إرسال البريد الإلكتروني. يرجى المحاولة لاحقًا.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterView(generics.CreateAPIView):
    """
    View for user registration with enhanced error handling and logging
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f'بدء عملية تسجيل مستخدم جديد - البيانات المستلمة: {request.data}')
            
            # التحقق من البيانات المطلوبة
            required_fields = ['username', 'email', 'password']
            missing_fields = [field for field in required_fields if field not in request.data]
            
            if missing_fields:
                error_msg = f'حقول مطلوبة ناقصة: {", ".join(missing_fields)}'
                logger.error(error_msg)
                return Response(
                    {'detail': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # معالجة البيانات
            data = request.data.copy()
            data['username'] = data.get('username', '').strip()
            data['email'] = data.get('email', '').lower().strip()
            
            # تسجيل البيانات بعد التنظيف
            logger.info(f'بيانات المستخدم بعد التنظيف: {data}')
            
            # التحقق من صحة البيانات
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # حفظ المستخدم
            user = serializer.save()
            logger.info(f'تم إنشاء المستخدم بنجاح - ID: {user.id}, Email: {user.email}')
            
            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'تم إنشاء الحساب بنجاح'
            }, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            logger.error(f'خطأ في التحقق من صحة البيانات: {e.detail}')
            return Response(
                {'errors': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log the error for debugging
            logger.error(f'حدث خطأ أثناء إنشاء الحساب: {str(e)}', exc_info=True)
            
            # Return appropriate error response
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
                
            return Response(
                {"detail": "حدث خطأ غير متوقع أثناء إنشاء الحساب. يرجى المحاولة مرة أخرى لاحقًا."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(generics.GenericAPIView):
    """
    View مخصص لتسجيل الدخول.
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # تسجيل الخطأ للتحليل
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Login error: {str(e)}")
            
            # إرجاع رسالة خطأ مناسبة
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"detail": "حدث خطأ أثناء محاولة تسجيل الدخول. يرجى المحاولة مرة أخرى لاحقًا."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# 2. عرض لإدارة المرضى (قائمة وإضافة)
class PatientListView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated] # فقط المستخدمون المسجلون يمكنهم الوصول

    def get_queryset(self):
        # إرجاع المرضى الخاصين بالطبيب الحالي فقط
        return Patient.objects.filter(doctor=self.request.user).prefetch_related('diagnoses')

    def perform_create(self, serializer):
        # عند إنشاء مريض جديد، قم بتعيين الطبيب تلقائيًا
        serializer.save(doctor=self.request.user)
        
    def get_serializer_context(self):
        # تمرير 'request' إلى المحول للسماح بالوصول إلى المستخدم
        return {'request': self.request} 
    
    
class SyncAllDataView(APIView):
    """
    نقطة نهاية لإرجاع كل بيانات المستخدم (المرضى والتشخيصات) دفعة واحدة.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # جلب كل المرضى مع تشخيصاتهم باستخدام prefetch_related لتحسين الأداء
        patients_queryset = Patient.objects.filter(doctor=user).prefetch_related('diagnoses')
        
        # استخدام PatientSerializer لإعداد البيانات
        # نستخدم many=True لأن لدينا قائمة من المرضى
        serializer = PatientSerializer(patients_queryset, many=True, context={'request': request})
        
        # إرجاع البيانات كقائمة من المرضى، وكل مريض يحتوي على قائمة تشخيصاته
        return Response(serializer.data, status=status.HTTP_200_OK)    
    
# 3. عرض لتفاصيل مريض معين (عرض، تحديث، حذف)
# class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = PatientSerializer
#     permission_classes = [permissions.IsAuthenticated,IsOwner]
    
#     def get_queryset(self):
#         return  Patient.objects.filter(doctor=self.request.user).prefetch_related('diagnoses')

    # class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    #     serializer_class = PatientSerializer
    #     permission_classes = [permissions.IsAuthenticated, IsOwner]
        
    #     def get_queryset(self):
    #         return Patient.objects.filter(doctor=self.request.user).prefetch_related('diagnoses')

# 3. عرض لتفاصيل مريض معين (عرض، تحديث، حذف)
class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated,IsOwner]
    
    def get_queryset(self):
        return  Patient.objects.filter(doctor=self.request.user).prefetch_related('diagnoses')
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
    # def perform_destroy(self, instance):
    #     diagnoses = instance.diagnoses.all()
    #     for diagnosis in diagnoses:
    #         if diagnosis.iris_image:
    #             try:
    #                 diagnosis.iris_image.delete(save=False)
    #             except ObjectDoesNotExist:
    #                 pass
    #     diagnoses.delete()
    #     super().perform_destroy(instance)
    
# العرض الرئيسي والمحدث
class DiagnoseView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. استلام البيانات من تطبيق Flutter
        # لاحظ استخدام request.POST بدلاً من request.data للوصول إلى الحقول
        # عند استخدام multipart/form-data
        patient_name = request.POST.get('patient_name')
        patient_age = request.POST.get('patient_age')
        image_file = request.FILES.get('iris_image')

        # 2. التحقق من صحة المدخلات
        if not all([patient_name, patient_age, image_file]):
            return Response(
                {'error': 'patient_name, patient_age, and iris_image are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            patient_age_int = int(patient_age)
        except (ValueError, TypeError):
            return Response({'error': 'patient_age must be a valid integer.'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. منطق "Get or Create" للمريض
        # هذا هو قلب التحديث: البحث عن المريض أو إنشاؤه في خطوة واحدة
        patient, created = Patient.objects.get_or_create(
            doctor=request.user,
            name=patient_name,
            defaults={'age': patient_age_int}
        )
        
        # (اختياري) تحديث العمر إذا كان المريض موجودًا بالفعل ولكن العمر تغير
        if not created and patient.age != patient_age_int:
            patient.age = patient_age_int
            patient.save()

        # 4. تشغيل نموذج ONNX للتشخيص
        try:
            pipeline = ApiConfig.DIAGNOSIS_PIPELINE
            result, confidence_ratio = pipeline.run(image_file)
            notes = "تم التشخيص على الخادم باستخدام خط أنابيب من نموذجين."
            
             # --- ترجمة النتيجة إلى العربية بطريقة أكثر أمانًا ---
            translation_map = {
                'diabetic': 'مصاب',
                'non-diabetic': 'غير مصاب'
            }
            # استخدم .get() مع قيمة افتراضية لتجنب الأخطاء إذا كانت النتيجة غير متوقعة
            result_ar = translation_map.get(result, result)
        except Exception as e:
            # Log the full error for debugging
            print(f"PIPELINE FAILED: {str(e)}")
            import traceback
            traceback.print_exc()  # This will print the full traceback
            return Response(
                {'error': f'فشل معالجة الصورة: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            # 5. Create and save diagnosis record
            diagnosis = Diagnosis.objects.create(
                patient=patient,
                iris_image=image_file,
                results=result_ar,  # Save result in Arabic
                ratio=confidence_ratio,
                note=notes
            )
        except Exception as e:
            print(f"DATABASE SAVE FAILED: {str(e)}")
            return Response(
                {'error': 'فشل حفظ نتيجة التشخيص'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 6. إرجاع نتيجة التشخيص إلى تطبيق Flutter
        serializer = DiagnosisSerializer(diagnosis, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ServerDiagnosisHistoryView(generics.ListAPIView):
    """
    عرض لإرجاع قائمة التشخيصات التي تمت على الخادم لمريض معين.
    يتم تحديد المريض عن طريق اسمه.
    """
    serializer_class = DiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 1. الحصول على اسم المريض من الـ query parameters
        # الرابط سيبدو هكذا: /api/diagnoses/history/?patient_name=Ahmed%20Ali
        patient_name = self.request.query_params.get('patient_name', None)

        if patient_name is None:
            # إذا لم يتم توفير اسم المريض، أرجع قائمة فارغة
            return Diagnosis.objects.none()
        
        # 2. جلب جميع التشخيصات للمريض المحدد الذي يخص الطبيب الحالي
        queryset = Diagnosis.objects.filter(
            patient__doctor=self.request.user,
            patient__name=patient_name
        ).order_by('-diagnosis_date') # الترتيب من الأحدث إلى الأقدم
        
        return queryset

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
