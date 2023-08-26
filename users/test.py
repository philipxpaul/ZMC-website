from django.shortcuts import render, redirect
from .models import Video
from django.http import HttpResponseForbidden
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from .form import TeacherRegistrationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from django.contrib.auth.hashers import make_password
from .models import Teacher, Student,Advisor
from io import TextIOWrapper
from django.contrib.auth.models import User
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from quiz.models import Quiz,Submission
from django.contrib.auth import logout
from django.db.models import Sum


def student_scores(request):
    # Fetch all students and their total scores from all their quiz submissions
    students = Student.objects.annotate(total_score=Sum('student_profile__submission__score'))

    print(students.query)  # This will print the generated SQL query to the console
    for student in students:
        print(student.name, student.total_score)
    
    return render(request, 'users/students.html', {'students': students})