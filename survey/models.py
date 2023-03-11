# models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.conf import settings

class CustomUser(AbstractUser):
    points = models.IntegerField(default=0)
    group_name = models.TextField(null=True, default="Not provided")

    def get_email(self):
        
        return f"{self.email}"

    def get_username(self):

        return f"{self.username}"

    def get_group(self):
        if self.group_name == 'Not provided':
            return ""
        return f"{self.group_name}"
 
class Survey(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='surveys'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)
    allocated_points = models.IntegerField(default=0)
    expired = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Survey({self.id}): {self.title}"

    def priorityValue(self):
        hours_remaining = (self.deadline - timezone.now()).total_seconds() / 3600
        return (1 + self.allocated_points*100) * (1 / hours_remaining)


class Question(models.Model):
    text = models.TextField()
    istext = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    survey = models.ForeignKey(
        Survey, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='questions'
    )

    def __str__(self):
        return f"Question({self.id}): {self.text} - {self.survey}" 


class Choice(models.Model):
    text = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='choices'
    )

    def __str__(self):
        return f"Choice({self.id}): {self.text} - {self.question}"


class SurveyResponse(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_anonymous = models.BooleanField(default=False)
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='question_responses'
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='choices_selected'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_responder'
    )