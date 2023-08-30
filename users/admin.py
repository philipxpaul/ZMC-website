from django.contrib import admin
from .models import CustomUser, Video, Student, Teacher,uploadLink

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'id',)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'student_counter')  # Add 'code' here



class VideoAdmin(admin.ModelAdmin):
    list_display = ('title','upload_date','board_link','video_link','category', 'teacher','id')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher',)


class UploadLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'thumbnail_link','board_link', 'zoom_link']




admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Student)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(uploadLink, UploadLinkAdmin)
