from django.urls import path
from . import views


urlpatterns = [
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('add_video/', views.add_video, name='add_video'),
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('register_teacher/', views.register_teacher, name='register_teacher'),
    path('lesson/', views.lesson, name='lesson'),
    path('edit_students/<int:student_id>/', views.edit_students, name='edit_students'),
    path('students/', views.students, name='students'),
    path('upload/', views.upload_students, name='upload_students'),
    path('delete_students/<int:student_id>/', views.delete_students, name='delete_students'),
    path('center/', views.TeacherLoginView.as_view(), name='center'),
    path('login/', views.StudentLoginView.as_view(), name='student_login'),
    path('logout/', views.user_logout, name='logout'),
    path('newlink/', views.newlink, name='newlink'),
    
]
