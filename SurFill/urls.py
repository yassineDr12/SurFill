from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('survey.urls')),
    path('survey/', include('social_django.urls')),
]
