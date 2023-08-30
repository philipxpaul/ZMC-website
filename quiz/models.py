import datetime
from django.db import models
from users.models import Student, Teacher,Video

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="quizzes",null=True )
    total_marks = models.PositiveIntegerField(default=0)
    date = models.DateField(default=datetime.date.today)



    def calculate_total_marks(self):
        self.total_marks = self.question_set.count()
        self.save()

    def __str__(self):
        return self.title

    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    
    def __str__(self):
        return str(self.quiz) + ": " + self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return self.text
    
class Submission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)

class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
