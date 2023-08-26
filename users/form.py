# forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Teacher

class TeacherRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 2  # Set user type to Teacher
        if commit:
            user.save()
            teacher = Teacher(user=user)
            teacher.save()  # Only save the teacher object to get an ID
        return user

class StudentRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=150, help_text="Enter the student's full name")
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 3  # Set user type to Student
        if commit:
            user.save()
        return user
