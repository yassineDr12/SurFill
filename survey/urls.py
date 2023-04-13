# survey/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name="Home page"),
  path('register/', views.RegisterView.as_view(), name='register'),
  path('login/', auth_views.LoginView.as_view(template_name='survey/login.html'), name='login'),
  path('profile/', views.ProfileView.as_view(), name='profile'),
  path('logout/', auth_views.LogoutView.as_view(), name='logout'),
  path('surveys_list/', views.SurveyListview, name='survey_list'),
  path('fill_survey/<int:survey_id>/', views.fill_survey, name='fill_survey'),
  path('response_successful', views.survey_submitted, name='survey_submitted'),
  path('survey-expired', views.survey_expired, name='survey_expired'),
  path('surveys/create/', views.SurveyCreateView.as_view(), name='survey_create'),
  path('survey-results/<int:survey_id>/', views.SurveyResultsView.as_view(), name='survey_results'),
  path('surveys/edit/<int:survey_id>/', views.SurveyEditView.as_view(), name='edit_survey'),
  path('profile/share-points/', views.SharePointsView.as_view(), name='share_points'),
]
