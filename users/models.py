from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'admin'),
        (2, 'teacher'),
        (3, 'student'),
    )
    
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=3)

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    student_counter = models.IntegerField(default=0)  # Counter for generating unique student codes


    def generate_student_code(self):
        # Increment the counter
        self.student_counter += 1
        self.save()

    # Generate the code using the first 3 letters of the user's username
        prefix = self.user.username[:3].upper()
        return f"{prefix}{self.student_counter}"

    
    def __str__(self):
        return self.user.username
    
class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=255, default='Default Name') # New name field
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    advisor = models.CharField(max_length=200, default="Default Advisor Name")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name or "Unknown Student"

class Advisor(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
    
class Dashboard(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)

class Update(models.Model):
    content = models.TextField()
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)


class Video(models.Model):
    title = models.CharField(max_length=200)
    upload_date = models.DateTimeField(auto_now_add=True)
    thumbnail_link = models.URLField()
    zoom_link = models.URLField()
    video_link = models.URLField()
    category = models.CharField(max_length=50)
    teacher = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, limit_choices_to={'user_type': 2})
    # quiz = models.OneToOneField('quiz.Quiz', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


class uploadLink(models.Model):
    title = models.CharField(max_length=200,null=True, blank=True)
    thumbnail_link = models.CharField(max_length=255, null=True, blank=True)
    zoom_link = models.URLField(max_length=255, null=True, blank=True)
    teacher = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, limit_choices_to={'user_type': 2})

@receiver(post_save, sender=CustomUser) 
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 2:  # teacher
            Teacher.objects.create(user=instance)
        elif instance.user_type == 3:  # student
            Student.objects.create(user=instance)







