"""
URL configuration for iris_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), 
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



# Command = PGPASSWORD=dPUkVG6qNaLsuTJZufAH3zcBIInLIesH psql -h dpg-d2vmuav5r7bs73ajt570-a.oregon-postgres.render.com -U root postirisdb
# External = postgresql://root:dPUkVG6qNaLsuTJZufAH3zcBIInLIesH@dpg-d2vmuav5r7bs73ajt570-a.oregon-postgres.render.com/postirisdb
# Internal = postgresql://root:dPUkVG6qNaLsuTJZufAH3zcBIInLIesH@dpg-d2vmuav5r7bs73ajt570-a/postirisdb
# Password = dPUkVG6qNaLsuTJZufAH3zcBIInLIesH