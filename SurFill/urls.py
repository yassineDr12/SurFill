from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('survey.urls')),
    path('microsoft/', include('microsoft_auth.urls', namespace='microsoft')),
    path('survey/', include('social_django.urls')),
]
