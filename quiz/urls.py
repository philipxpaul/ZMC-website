from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz, name='quiz'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    # path('<int:quiz_id>/add_question/', views.add_question, name='add_question'),
    path('<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('take_quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz_list/', views.quiz_list, name='quiz_list'),
    path('submit_quiz/<int:quiz_id>/', views.submit_quiz, name='submit_quiz'),
    path('quiz_results/', views.quiz_results, name='quiz_results'),
    path('quiz_results/download_csv/', views.quiz_results, name='download_csv'),  # Define a URL pattern for CSV download


       
    
]