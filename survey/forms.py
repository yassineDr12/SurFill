# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
User = get_user_model()


class SurveyResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)

        for question in questions:
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.text,
                choices=[(c.id, c.text) for c in question.choices.all()],
                widget=forms.RadioSelect
            )
                    
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=150)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

