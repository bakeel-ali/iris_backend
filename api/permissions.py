from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    إذن مخصص للسماح فقط لمالك الكائن بتعديله.
    يفترض أن الكائن يحتوي على حقل 'doctor'.
    """
    def has_object_permission(self, request, view, obj):
        # أذونات القراءة مسموحة لأي مستخدم مصادق
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # أذونات الكتابة (تعديل/حذف) مسموحة فقط لمالك الكائن
        return obj.doctor == request.user