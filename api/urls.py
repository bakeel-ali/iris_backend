from django.urls import path
from .views import RegisterView, PatientListView, PatientDetailView, DiagnoseView,ServerDiagnosisHistoryView,LoginView,SyncAllDataView,SendResetCodeView
from .views import RegisterView, PatientListView, PatientDetailView, DiagnoseView,ServerDiagnosisHistoryView,LoginView,SyncAllDataView,SendResetCodeView,UserProfileView
from .views import ResetPasswordView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # روابط المصادقة
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # رابط إرسال رمز إعادة تعيين كلمة المرور
    path('send-reset-code/', SendResetCodeView.as_view(), name='send-reset-code'),
    # رابط تغيير كلمة المرور بعد التحقق
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),

    # روابط المرضى
    # path('patients/', PatientListView.as_view(), name='patient-list'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    
    # رابط التشخيص
    path('diagnose/', DiagnoseView.as_view(), name='diagnose'),
    path('diagnoses/history/', ServerDiagnosisHistoryView.as_view(), name='diagnosis-history'),     
    path('sync/all/', SyncAllDataView.as_view(), name='sync-all-data'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
]