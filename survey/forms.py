# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Survey, Question, Choice
User = get_user_model()

class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False)

class SurveyResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)

        for question in questions:
            if question.istext == True:
                self.fields[f'question_{question.id}'] = forms.CharField(
                    label=question.text,
                    widget=forms.TextInput(attrs={'class': 'input'})
                )
            else:
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    label=question.text,
                    choices=[(c.id, c.text) for c in question.choices.all()],
                    widget=forms.RadioSelect
                )

                    
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=150)
    group_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'group_name', 'password1', 'password2')

