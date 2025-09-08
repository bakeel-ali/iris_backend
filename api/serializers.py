from rest_framework import serializers
from .models import User, Patient, Diagnosis
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message='هذا البريد الإلكتروني مسجل مسبقًا.')],
        error_messages={
            'required': 'حقل البريد الإلكتروني مطلوب',
            'invalid': 'الرجاء إدخال بريد إلكتروني صحيح'
        }
    )
    password = serializers.CharField(
        write_only=True, 
        required=True,
        min_length=8,
        error_messages={
            'required': 'حقل كلمة المرور مطلوب',
            'blank': 'كلمة المرور لا يمكن أن تكون فارغة',
            'min_length': 'يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {
            'username': {
                'required': True,
                'error_messages': {
                    'required': 'حقل اسم المستخدم مطلوب',
                    'invalid': 'يجب أن يحتوي اسم المستخدم على أحرف وأرقام و _ فقط',
                    'max_length': 'اسم المستخدم طويل جداً (الحد الأقصى 150 حرفاً)'
                }
            }
        }

    def validate_username(self, value):
        """
        التحقق من صحة اسم المستخدم
        """
        if not value.replace('_', '').isalnum():
            raise serializers.ValidationError("يجب أن يحتوي اسم المستخدم على أحرف وأرقام و _ فقط")
        return value.strip()

    def validate_password(self, value):
        """
        التحقق من قوة كلمة المرور
        """
        errors = []
        
        # التحقق من طول كلمة المرور
        if len(value) < 8:
            errors.append('يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل')
            
        # التحقق من وجود حرف كبير
        if not any(c.isupper() for c in value):
            errors.append('يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل')
            
        # التحقق من وجود حرف صغير
        if not any(c.islower() for c in value):
            errors.append('يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل')
            
        # التحقق من وجود رقم
        if not any(c.isdigit() for c in value):
            errors.append('يجب أن تحتوي كلمة المرور على رقم واحد على الأقل')
            
        # التحقق من وجود رمز خاص
        special_chars = '!@#$%^&*()-_=+[]{}|;:,.<>?'
        if not any(c in special_chars for c in value):
            errors.append('يجب أن تحتوي كلمة المرور على رمز خاص واحد على الأقل (!@#$%^&*()-_=+[]{}|;:,.<>?)')
            
        if errors:
            raise serializers.ValidationError(errors)
            
        return value

    def create(self, validated_data):
        """
        إنشاء مستخدم جديد مع التحقق من الأخطاء
        """
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'].lower().strip(),
                password=validated_data['password']
            )
            
            # تسجيل عملية إنشاء المستخدم
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'تم إنشاء مستخدم جديد: {user.email}')
            
            return user
            
        except Exception as e:
            # تسجيل الخطأ بالتفصيل
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'خطأ في إنشاء المستخدم: {str(e)}')
            
            if 'username' in str(e).lower():
                raise serializers.ValidationError({
                    'username': ['اسم المستخدم مستخدم مسبقاً']
                })
            elif 'email' in str(e).lower():
                raise serializers.ValidationError({
                    'email': ['البريد الإلكتروني مستخدم مسبقاً']
                })
            else:
                raise serializers.ValidationError({
                    'non_field_errors': [f'حدث خطأ أثناء إنشاء الحساب: {str(e)}']
                })

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
        }

    def create(self, validated_data):
        # استخراج كلمة المرور من البيانات
        password = validated_data.pop('password', None)
        
        # إنشاء المستخدم
        user = User(**validated_data)
        
        # تعيين كلمة المرور بشكل صحيح (سيتم تشفيرها تلقائيًا)
        if password:
            user.set_password(password)
        
        # حفظ المستخدم
        user.save()
        return user
        
    def validate_email(self, value):
        # التحقق من عدم وجود مستخدم بنفس البريد الإلكتروني
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مسجل مسبقًا.")
        return value

class LoginSerializer(serializers.Serializer):
    """
    Serializer مخصص لتسجيل الدخول باستخدام البريد الإلكتروني وكلمة المرور.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    # إضافة حقول بيانات المستخدم
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
            
            # استخدام دالة authenticate من Django للتحقق من بيانات الاعتماد
            user = authenticate(request=self.context.get('request'), 
                              email=email, 
                              password=password)

            if not user:
                raise serializers.ValidationError({
                    "password": ["كلمة المرور غير صحيحة."]
                })
                
            # التحقق من أن الحساب مفعل
            if not user.is_active:
                raise serializers.ValidationError({
                    "email": ["هذا الحساب غير مفعل. يرجى التواصل مع الدعم الفني."]
                })
            
        # إذا كانت بيانات الاعتماد صحيحة، قم بإنشاء التوكنات
            refresh = RefreshToken.for_user(user)
        
        # إضافة بيانات المستخدم إلى الرد  
        # self.user_data = UserSerializer(user).data
            
            return {
                'email': user.email,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_id': user.id, 
                'username': user.username, 
            }
            
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": ["لا يوجد حساب مسجل بهذا البريد الإلكتروني."]
            })

class DiagnosisSerializer(serializers.ModelSerializer):
    # لجعل رابط الصورة كاملاً في الـ JSON
    iris_image_url = serializers.ImageField(source='iris_image', read_only=True)

    class Meta:
        model = Diagnosis
        fields = ['id', 'patient', 'iris_image', 'iris_image_url', 'results', 'ratio', 'note', 'diagnosis_date']
        read_only_fields = ['results', 'ratio', 'note', 'diagnosis_date'] # هذه الحقول يتم إنشاؤها بواسطة الخادم


class PatientSerializer(serializers.ModelSerializer):
    # لعرض قائمة التشخيصات مع كل مريض
    diagnoses = DiagnosisSerializer(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'doctor', 'name', 'age', 'created_at', 'diagnoses']
        read_only_fields = ['doctor'] # يتم تحديد الطبيب تلقائيًا من المستخدم المسجل دخوله
        
            # التحقق على مستوى الحقل (Field-level validation)
    def validate_age(self, value):
        """
        التحقق من أن عمر المريض ضمن نطاق معقول.
        """
        if not (1 <= value <= 120):
            raise serializers.ValidationError("العمر يجب أن يكون بين 1 و 120 سنة.")
        return value

    # التحقق على مستوى الكائن (Object-level validation)
    def validate(self, data):
        """
        التحقق من عدم وجود مريض بنفس الاسم والعمر لنفس الطبيب.
        """
        doctor = self.context['request'].user
        name = data.get('name')
        
        # عند الإنشاء فقط (Create)
        if self.instance is None:
            if Patient.objects.filter(doctor=doctor, name=name).exists():
                raise serializers.ValidationError(
                    f"لديك بالفعل مريض مسجل بهذا الاسم: {name}"
                )
        return data