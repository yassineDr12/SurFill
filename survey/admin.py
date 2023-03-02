from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Survey, Question, Choice, SurveyResponse
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'points', 'is_staff', 'group_name')

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(SurveyResponse)