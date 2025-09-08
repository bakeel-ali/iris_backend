from django.contrib import admin

# Register your models here.
from .models import Patient,Diagnosis,User
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Diagnosis)