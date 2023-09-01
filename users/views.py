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
from django.db.models import Q
from .models import uploadLink


def newlink(request):
    allowed_user_types = [2, 1]  # Teacher and Admin user types
    if not request.user.is_authenticated or request.user.user_type not in allowed_user_types:
        return HttpResponseForbidden("You don't have permission to access this page.")

    if request.method == 'POST':
        title = request.POST.get('title')
        thumbnail_link = request.POST.get('thumbnail_link')
        zoom_link = request.POST.get('zoom_link')
        board_link = request.POST.get('board_link')

        # Basic validation to check if all fields are filled
        # if not all([title, thumbnail_link, zoom_link, ]):
        #     # You can handle errors accordingly, maybe return a message to the user
        #     return render(request, 'teacher/uploadlink.html', {'error': 'All fields are required!'})

        # Check if the logged-in user is an admin
        if request.user.user_type == 1:  # Admin user type
            teacher = None  # Admin user does not need a teacher association
        else:
            teacher = request.user  # Teacher user association

        # Check if a link with the given title and teacher already exists
        print(f"Logged in user: {request.user.id}")
        print(f"User type: {request.user.user_type}")

    # Check if a link with the given title and teacher already exists
        existing_link = uploadLink.objects.filter(teacher=teacher)
        if existing_link.exists():
            existing_link.delete()

    # Create a new link
        Link = uploadLink(
            title=title,
            thumbnail_link=thumbnail_link,
            zoom_link=zoom_link,
            board_link=board_link,
            teacher=request.user
    )
        Link.save()

        return redirect('dashboard')

    return render(request, 'teacher/newlink.html')


def students(request):
    # Ensure the user is authenticated and is a teacher
    if not request.user.is_authenticated or request.user.user_type != 2:
        # messages.error(request, "You don't have permission to access this page.")
        return redirect('center')  # or wherever you want to redirect them

    try:
        # Get the teacher's profile
        teacher_profile = Teacher.objects.get(user=request.user)

        # Start with a queryset of students associated with this teacher
        students_queryset = Student.objects.filter(teacher=teacher_profile)

        # Filtering
        code_filter = request.GET.get('code')
        if code_filter:
            students_queryset = students_queryset.filter(code__icontains=code_filter)

        name_filter = request.GET.get('name')
        if name_filter:
            students_queryset = students_queryset.filter(name__icontains=name_filter)

        advisor_filter = request.GET.get('advisor')
        if advisor_filter:
            students_queryset = students_queryset.filter(advisor__icontains=advisor_filter)

        # Sorting
        sort_code = request.GET.get('sort_code')
        if sort_code == 'asc':
            students_queryset = students_queryset.order_by('code')
        elif sort_code == 'desc':
            students_queryset = students_queryset.order_by('-code')

        sort_name = request.GET.get('sort_name')
        if sort_name == 'asc':
            students_queryset = students_queryset.order_by('name')
        elif sort_name == 'desc':
            students_queryset = students_queryset.order_by('-name')

        sort_advisor = request.GET.get('sort_advisor')
        if sort_advisor == 'asc':
            students_queryset = students_queryset.order_by('advisor')
        elif sort_advisor == 'desc':
            students_queryset = students_queryset.order_by('-advisor')

        # Fetch the students and their total scores
        students_associated_with_teacher = students_queryset.annotate(total_score=Sum('submission__score'))

        context = {
            'students': students_associated_with_teacher,
        }
        
        return render(request, 'teacher/students.html', context)

    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect('center')  # redirect to an appropriate page
    
def edit_students(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        form = Student(request.POST, instance=student)  # Assuming you have a form for Student
        if form.is_valid():
            form.save()
            return redirect('students')
    else:
        form = Student(instance=student)
    return render(request, 'edit_student.html', {'form': form})

def delete_students(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('students')
  
#login redirect
class StudentLoginView(LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect('student_dashboard')  # Redirect to the student dashboard or main page

@login_required
def upload_students(request):
    if request.method == "POST":
        csv_file = request.FILES.get('csv_file', None)
        
        if csv_file:
            csv_file_io = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(csv_file_io)

            for row in csv_reader:
                print(f"Processing row: {row}")  # Print the row being processed

                try:
                    # Get student details
                    student_name = row["name"].strip()  # Strip to remove any leading/trailing spaces
                    email = row["email"].strip()
                    password = make_password(row["password"].strip())
                    advisor_name = row.get("advisor", "Default Advisor Name").strip()

                    # Fetch or create advisor
                    advisor, _ = Advisor.objects.get_or_create(name=advisor_name)

                    # Identify the teacher by ID
                    teacher_id = row["teacher_id"]
                    teacher = Teacher.objects.get(id=teacher_id)

                    student_code = teacher.generate_student_code()
                    print(f"Generated student code: {student_code}")

                    
                    student_code = teacher.generate_student_code()

                    # Check if student (CustomUser) already exists
                    user, user_created = CustomUser.objects.get_or_create(username=student_name, email=email)
                    if user_created:
                        user.set_password(row["password"].strip())
                        user.save()

                    # Check if student profile already exists
                    student, student_created = Student.objects.get_or_create(user=user)
                    # Update the student details irrespective of whether the student was just created or already existed
                    student.name = student_name  # Using the name from the CSV
                    student.code = teacher.generate_student_code()  # Generating student code
                    student.advisor = advisor_name  # Using the advisor name from the CSV or default
                    student.teacher = teacher
                    student.save()
                except (KeyError, Teacher.DoesNotExist) as e:
                    print(f"Error processing row {row}: {e}")  # Print details of the exception

            return redirect('students')

    return render(request, 'teacher/upload.html')

def display_videos(request):
    recent_video = Video.objects.latest('id')

    all_videos_except_recent = Video.objects.exclude(id=recent_video.id).order_by('-upload_date')
    
    # Return videos to template
    context = {
        'recent_video': recent_video,
        'all_videos': all_videos_except_recent,
    }
    
    return render(request, 'users/student_dashboard.html', context)

def edit_students(request):
    return render(request,'teacher/students.html')


def quiz(request):
    return render(request,'teacher/quiz.html')

def lesson(request):
    # You might want to add authentication checks, e.g., is the user a teacher?
    if not request.user.is_authenticated:
        return redirect('center')
    elif request.user.user_type not in [1, 2]:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('center')  # Redirect them somewhere else, maybe a homepage or error page
    
    # If you want to fetch only videos uploaded by the current user/teacher:
    videos_uploaded_by_user = Video.objects.filter(teacher=request.user).order_by('-upload_date')

    context = {
        'videos': videos_uploaded_by_user,
    }

    return render(request, 'teacher/lesson.html', context)


def add_video(request):
    allowed_user_types = [2, 1]  # Teacher and Admin user types
    if not request.user.is_authenticated or request.user.user_type not in allowed_user_types:
        return HttpResponseForbidden("You don't have permission to access this page.")

    if request.method == 'POST':
        title = request.POST.get('title')
        video_link = request.POST.get('video_link')
        board_link = request.POST.get('board_link')

   # Basic validation to check if all fields are filled
        if not all([title, video_link]):
            # You can handle errors accordingly, maybe return a message to the user
            return render(request, 'teacher/add_video.html', {'error': 'All fields are required!'})

        # Check if the logged-in user is an admin
        if request.user.user_type == 1:  # Admin user type
            teacher = None  # Admin user does not need a teacher association
        else:
            teacher = request.user  # Teacher user association


        video = Video(
            title=title,
            video_link=video_link,
            board_link=board_link,
            teacher=request.user
        )
        video.save()
        return redirect('dashboard')  # Replace 'dashboard_view_name' with the name of the dashboard view

    return render(request, 'teacher/add_video.html')

@login_required
def student_dashboard(request):
    # Ensure user is logged in and is a student
    if not request.user.is_authenticated or request.user.user_type != 3:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('student_login')  # or wherever you want to redirect them

    try:
    # Get the student's profile
        student_profile = Student.objects.get(user=request.user)

    # Use ForeignKey relationship to get the associated teacher directly
        associated_teacher = student_profile.teacher

    # Filter videos uploaded by that teacher
        videos_uploaded_by_teacher = Video.objects.filter(teacher=associated_teacher.user).order_by('-upload_date')
        uploaded_link_by_teacher = uploadLink.objects.filter(teacher=associated_teacher.user).first()

    except Student.DoesNotExist:
        videos_uploaded_by_teacher = []  # No videos if student profile not found
        messages.error(request, "Student profile not found.")
    except Teacher.DoesNotExist:
        videos_uploaded_by_teacher = []  # No videos if teacher profile not found
        messages.error(request, "Teacher profile not found.")
    
    context = {
        'all_videos': videos_uploaded_by_teacher,
        'uploaded_link': uploaded_link_by_teacher  # Add the uploaded link to the context

    }

    return render(request, 'users/student_dashboard.html', context)


def teacher_dashboard(request):
    # Ensure the user is authenticated and is a teacher or admin
    if not request.user.is_authenticated:
        return redirect('center')
    elif request.user.user_type not in [1, 2]:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('center')  # Redirect them somewhere else, maybe a homepage or error page


    all_videos = Video.objects.filter(teacher=request.user).order_by('-upload_date')

    try:
        teacher_id = Teacher.objects.get(user=request.user).id  # Try to get the teacher's ID   
    except Teacher.DoesNotExist:  # This will be raised if the user doesn't have an associated Teacher object
        if request.user.is_superuser:  # Check if the user is an admin
            # Redirect them to the admin site or another appropriate page
            return redirect('admin:index')
        else:
            # Handle the error for non-admin users, e.g., display an error message
            messages.error(request, "You don't have permission to access this page.")
            return redirect('center')  # Redirect to a safe location to avoid loop

    context = {
        'all_videos': all_videos,
        'teacher_id': teacher_id  # Pass the teacher ID to the template
    }

    return render(request, 'teacher/dashboard.html', context)


#login   
class TeacherLoginView(LoginView):
    template_name = 'teacher/center.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect('students')  # Redirect to the teacher dashboard or main page

#signup
@csrf_exempt
def register_teacher(request):
    if request.method ==  "POST":
        data = json.loads(request.body)
        form = TeacherRegistrationForm(data)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Registration successful'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed.'}, status=405)


@login_required
def user_logout(request):
    user_type = request.user.user_type
    logout(request)
    
    if user_type == 2:  # teacher
        return redirect('center')
    elif user_type == 3:  # student
        return redirect('student_login')
    
    return redirect('student_login')




    
    

