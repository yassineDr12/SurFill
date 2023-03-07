# survey/views.py

import json
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from datetime import datetime

from django.views import View

from .models import Survey, Question, Choice, SurveyResponse
from .tokens import user_tokenizer
from .forms import RegistrationForm, SurveyResponseForm
from django.contrib.auth import get_user_model
User = get_user_model()

def update_surveys():
    now = datetime.now()
    expired_surveys = Survey.objects.filter(deadline__lt=now, expired=False)
    for survey in expired_surveys:
        user = survey.created_by
        points = survey.allocated_points
        survey.expired = True
        survey.allocated_points -= points
        if points > 0:
            user.points += points
        survey.save()
        user.save()

def home(request):
    return render(request, 'survey/home.html', {})

def SurveyListview(request):
    update_surveys()
    surveys = Survey.objects.filter(expired=False)
    user_responses = SurveyResponse.objects.filter(created_by=request.user)
    answered_surveys = [response.question.survey for response in user_responses]
    unanswered_surveys = surveys.exclude(id__in=[survey.id for survey in answered_surveys if survey])
    sorted_surveys = sorted(unanswered_surveys, key=lambda survey: survey.priorityValue(), reverse=True)
    context = {'surveys': sorted_surveys}
    return render(request, 'survey/list_surveys.html', context)

def survey_submitted(request):
    return render(request, 'survey/survey_submitted.html')

def survey_expired(request):
    return render(request, 'survey/survey_expired.html')

def fill_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if survey.expired == True:
        return HttpResponseRedirect(reverse('survey_expired'))
    questions = survey.questions.all()
    form = SurveyResponseForm(questions=questions)

    if request.method == 'POST':
        form = SurveyResponseForm(request.POST, questions=questions)
        if form.is_valid():
            for question, choice_id in form.cleaned_data.items():
                if question.startswith('question_'):
                    question_id = question.replace('question_', '')
                    question = Question.objects.get(id=question_id)
                    if isinstance(choice_id, str):
                        choice = Choice.objects.create(text=choice_id, question_id=question_id)
                    else:    
                        choice = Choice.objects.get(id=choice_id)
                    if request.user.is_authenticated:
                        user = request.user
                        SurveyResponse.objects.create(question_id=question_id, choice=choice, created_by=user)
                    else:
                        SurveyResponse.objects.create(question_id=question_id, choice=choice)   
            if request.user.is_authenticated:             
                user.points += 1
                user.save()
                survey.save()
            survey.allocated_points -= 1    
            return HttpResponseRedirect(reverse('survey_submitted'))

    context = {
        'survey': survey,
        'form': form,
    }
    return render(request, 'survey/fill_survey.html', context)

class RegisterView(View):
    def get(self, request):
        return render(request, 'survey/register.html', { 'form': RegistrationForm() })

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_valid = False
            user.save()
            #token = user_tokenizer.make_token(user)
            #user_id = urlsafe_base64_encode(force_bytes(str(user.id)))
            #url = 'http://localhost:8000' + reverse('confirm_email', kwargs={'user_id': user_id, 'token': token})
            #message = get_template('survey/register_email.html').render({'confirm_url': url})
            #mail = EmailMessage('SurFill Email Confirmation', message, to=[user.email], from_email=settings.EMAIL_HOST_USER)
            #mail.content_subtype = 'html'
            #mail.send()

            return render(request, 'survey/login.html', {
              'form': AuthenticationForm(),
              'message': f'Welcome to SurFill {user.username}. You can now login'
            })

        return render(request, 'survey/register.html', { 'form': form })

# this view class was replaced by django.contrib.auth.views.LoginView
class LoginView(View):
    def get(self, request):
        return render(request, 'survey/login.html', { 'form':  AuthenticationForm() })

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        remember_me = form.cleaned_data['remember_me']  # get remember me data from cleaned_data of form
        if not remember_me:
            self.request.session.set_expiry(0)  # if remember me is 
            self.request.session.modified = True
        if form.is_valid():
            try:
                form.clean()
            except ValidationError:
                return render(
                    request,
                    'survey/login.html',
                    { 'form': form, 'invalid_creds': True }
                )

            login(request, form.get_user())

            return redirect(reverse('profile'))

        return render(request, 'survey/login.html', { 'form': form })


class ProfileView(LoginRequiredMixin, View):

    update_surveys()

    def get(self, request):
        surveys = Survey.objects.filter(created_by=request.user)

        context = {'surveys': surveys}

        return render(request, 'survey/profile.html', context)


class SurveyCreateView(LoginRequiredMixin, View):
    def get(self, request):
        users = User.objects.all()
        return render(request, 'survey/create_survey.html', {'users': users})
    
    def post(self, request):
        data = request.POST
        
        title = data.get('title')
        questions_json = data.getlist('questions')
        deadline = data.get('deadline')
        allocated_points = data.get('points')
        if allocated_points == '':
            allocated_points = 0
        valid = True
        context = {}
        if not title:
            valid = False
            context['title_error'] = 'title is required'

        if not deadline:
            valid = False
            context['deadline_error'] = 'deadline is required' 

        if not questions_json:
            valid = False
            context['questions_error'] = 'questions are required'
            
        if not valid:
            context['users'] = User.objects.all()
            return render(request, 'survey/create_survey.html', context)
            
        survey = Survey.objects.create(title=title, created_by=request.user, 
                                       deadline = deadline, allocated_points=allocated_points)
        request.user.points -= int(allocated_points)
        request.user.save()                               
        for question_json in questions_json:
            question_data = json.loads(question_json)
            question = Question.objects.create(text=question_data['text'], survey=survey)
            for choice_data in question_data['choices']:
                Choice.objects.create(text=choice_data['text'], question=question)

        return redirect(reverse('profile'))


class QuestionViewModel:
    def __init__(self, text):
        self.text = text
        self.choices = []

    def add_survey_response(self, survey_response):
        for choice in self.choices:
            if choice.id == survey_response.choice.id:
                choice.responses += 1
                break


class ChoiceResultViewModel:
    def __init__(self, id, text, responses=0):
        self.id = id
        self.text = text
        self.responses = responses


class SurveyResultsView(View):

    def get_object(self):
        self.obj = get_object_or_404(Survey, pk=self.kwargs['survey_id'])
        return self.obj

    def get(self, request, survey_id):
        self.obj = get_object_or_404(Survey, pk=self.kwargs['survey_id'])
        questions = []
        for question in self.obj.questions.all():
            question_vm = QuestionViewModel(question.text)
            for choice in question.choices.all():
                question_vm.choices.append(ChoiceResultViewModel(choice.id, choice.text))
            
            for survey_response in SurveyResponse.objects.filter(question=question):
                question_vm.add_survey_response(survey_response)
            
            questions.append(question_vm)

        for question in questions:
            print(question.text)
            for choice in question.choices:
                print(choice.text, choice.responses)
            print()

        context = {'survey': self.obj, 'questions': questions}
        
        return render(request, 'survey/survey_results.html', context)

    def post(self, request, survey_id):
        if 'delete' in request.POST:
            survey = self.get_object()
            if survey.allocated_points > 0:
                request.user.points += survey.allocated_points
                request.user.save()
            survey = Survey.objects.get(id=survey_id)
            survey.delete()
            return redirect('profile')
        survey = get_object_or_404(Survey, id=survey_id)
        points = int(request.POST.get('points', 0))
        if points > 0:
            survey.allocated_points += points
            survey.save()
            request.user.points -= int(points)
            request.user.save()
            return redirect('profile') 
        return redirect('survey_results', survey_id=survey_id)    


class TestEmail(View):
    def get(self, request):
        user = User.objects.get(pk=9)
        token = user_tokenizer.make_token(user)
        user_id = urlsafe_base64_encode(force_bytes(user.id))
        url = 'http://localhost:8000' + reverse('confirm_email', kwargs={'user_id': user_id, 'token': token})
        message = get_template('survey/register_email.html').render({
          'confirm_url': url
        })
        mail = EmailMessage('Django Survey Email Confirmation', message, to=[user.email], from_email=settings.EMAIL_HOST_USER)
        mail.content_subtype = 'html'
        mail.send()
        return HttpResponse(f'email sent user_id = {user_id}, token = {token}')


class ConfirmRegistrationView(View):
    def get(self, request, user_id, token):
        user_id = force_str(urlsafe_base64_decode(force_bytes(user_id)))
        
        user = User.objects.get(pk=user_id)

        context = {
          'form': AuthenticationForm(),
          'message': 'Registration confirmation error . Please click the reset password to generate a new confirmation email.'
        }
        if user and user_tokenizer.check_token(user, token):
            user.is_valid = True
            user.save()
            context['message'] = 'Registration complete. Please login'

        return render(request, 'survey/login.html', context)
