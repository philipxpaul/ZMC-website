from django.contrib import admin
from .models import Quiz, Question, Answer, Submission, SubmissionAnswer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1  # Number of empty choice forms to show
    

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Number of empty question forms to show
    inlines = [AnswerInline]


class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score')  # Fields you want to display in the admin list view
    search_fields = ('student__user__username', 'quiz__title')  # Fields you want to be searchable
    list_filter = ('quiz', 'student')  # Fields you want to filter by in the sidebar


admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmissionAnswer)

