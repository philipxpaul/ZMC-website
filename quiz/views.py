import csv
from django.shortcuts import render, redirect
from .models import Quiz, Question, Answer,Submission, SubmissionAnswer,Teacher,Student
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from .form import QuizForm
from django.contrib.auth.decorators import login_required
from users.models import Video
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Quiz, Question, Answer
from django.http import HttpResponse
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



def quiz_results(request):
    # Ensure the user is authenticated and is a teacher
    if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 2:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('users:login')  # Ensure this is the correct path for your login view

    try:
        teacher_profile = Teacher.objects.get(user=request.user)
        students = Student.objects.filter(teacher=teacher_profile)
        quizzes = Quiz.objects.filter(teacher=teacher_profile)

        # Fetch and filter results
        filtered_results = get_filtered_results(request, students, teacher_profile)

        # Handle CSV export
        if request.GET.get('format') == 'csv':
            return export_to_csv(request)  # Make sure this is calling the correct function with the correct arguments

        # Paginate results
        paginator = Paginator(filtered_results, 50)  # Adjust the number per page as necessary
        page = request.GET.get('page', 1)

        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        context = {
            'results': results,
            'quizzes': quizzes,
            'filters': {
                'student_code': request.GET.get('student_code', ''),
                'name': request.GET.get('name', ''),
                'advisor': request.GET.get('advisor', ''),
                'total_score': request.GET.get('total_score', ''),
                'quiz_title': request.GET.get('quiz_title', '')
            }
        }

        return render(request, 'quiz/quiz_results.html', context)

    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect('dashboard')  # Ensure this is the correct path for your dashboard view


def get_filtered_results(request, students, teacher_profile):
    # Retrieve filters from the request
    student_code_filter = request.GET.get('student_code', '').strip()
    name_filter = request.GET.get('name', '').strip().lower()
    advisor_filter = request.GET.get('advisor', '').strip().lower()
    total_score_filter = request.GET.get('total_score', '').strip()
    quiz_title_filter = request.GET.get('quiz_title', '').strip().lower()

    filtered_results = []
    for student in students:
        student_data = {
            'code': student.code,
            'name': student.name,
            'advisor': student.advisor if student.advisor else "N/A",
            'total_score': 0,
            'quiz_data': []
        }

        # Aggregate quiz data
        quiz_data_qs = Submission.objects.filter(
            student=student, quiz__teacher=teacher_profile
        ).values('quiz__title', 'score')

        for quiz_data in quiz_data_qs:
            student_data['quiz_data'].append({
                'title': quiz_data['quiz__title'],
                'score': quiz_data['score']
            })
            student_data['total_score'] += quiz_data['score']

        # Apply filters
        if (
            (not student_code_filter or student_code_filter in student_data['code']) and
            (not name_filter or name_filter in student_data['name'].lower()) and
            (not advisor_filter or advisor_filter in (student_data['advisor'].lower() if student_data['advisor'] else '')) and
            (not total_score_filter or total_score_filter.isdigit() and int(total_score_filter) == student_data['total_score']) and
            (not quiz_title_filter or any(quiz_title_filter in quiz['title'].lower() for quiz in student_data['quiz_data']))
        ):
            filtered_results.append(student_data)

    return filtered_results


def export_to_csv(request):
    # Ensure the user is authenticated and is a teacher
    if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 2:
        return HttpResponse(status=403)  # Forbidden access

    teacher_profile = None
    try:
        teacher_profile = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return HttpResponse(status=404)  # Not found

    # Get the students for the teacher_profile. This should be a queryset or list of Student objects.
    students = Student.objects.filter(teacher=teacher_profile)

    # Fetch and filter results
    filtered_results = get_filtered_results(request, students, teacher_profile)

    # Set up the HttpResponse object with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="quiz_results_{request.user.username}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student Code', 'Name', 'Advisor', 'Total Score', 'Quiz Title', 'Quiz Score'])

    for student_data in filtered_results:
        # If student has quiz data, write each quiz and score
        if student_data['quiz_data']:
            for quiz in student_data['quiz_data']:
                writer.writerow([
                    student_data['code'],
                    student_data['name'],
                    student_data['advisor'],
                    student_data['total_score'],
                    quiz['title'],
                    quiz['score']
                ])
        # If no quiz data, write student info with N/A for quiz and score
        else:
            writer.writerow([
                student_data['code'],
                student_data['name'],
                student_data['advisor'],
                student_data['total_score'],
                "N/A",
                "N/A"
            ])

    return response



@login_required
def quiz_list(request):
    # Ensure the user is authenticated and is a stude
    
    student_teacher = request.user.student_profile.teacher

    # Filter quizzes by the student's teacher
    quizzes = Quiz.objects.filter(teacher=student_teacher)

    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})

def take_quiz(request, quiz_id):
    # Ensure the user is authenticated and is a student
    if not hasattr(request.user, 'student_profile'):
        # Handle unauthenticated users or non-students.
        redirect('student_login')

    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Verify if the student's teacher is the creator of the quiz
    if request.user.student_profile.teacher != quiz.teacher:
        # Handle unauthorized access
        redirect('center')

    return render(request, 'quiz/take_quiz.html', {'quiz': quiz})

def quiz(request):
    if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 2:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('users/center.html')
    
    try:
        teacher_profile = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return HttpResponseForbidden("Only teachers can access this page.")
    
    quizzes = Quiz.objects.filter(teacher=teacher_profile)
    return render(request, 'quiz/Quiz.html', {'quizzes': quizzes})


@login_required
def submit_quiz(request, quiz_id):

    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Check if the student has already attempted this quiz
    if Submission.objects.filter(student=request.user.student_profile, quiz=quiz).exists():
        return redirect('student_dashboard')  # or wherever you want to redirect them to

    if request.method == "POST":    
        submission = Submission(student=request.user.student_profile, quiz=quiz)
        submission.save()

        total_score = 0
        for question in quiz.question_set.all():
            answer_id = request.POST.get(f'question_{question.id}')

            # Move the print statement here, inside the loop.
            print(f"Checking answer for question ID {question.id}, answer ID {answer_id}")

            # Check if answer_id is present and not empty
            if answer_id:
                try:
                    answer = Answer.objects.get(id=answer_id)
                    if answer.is_correct:
                        total_score += 1
                    print(f"Total Score for submission: {total_score}")

                    # Save the student's answer for this question
                    SubmissionAnswer(submission=submission, question=question, answer=answer).save()
                except Answer.DoesNotExist:
                    # You can log this or handle it accordingly
                    pass

        # Now, total_score has the number of correct answers given by the student
        submission.score = total_score
        submission.save()
        return redirect('student_dashboard')  # or wherever you want to redirect after quiz submission

    return render(request, 'submit_quiz.html', {'quiz': quiz})




def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)

    if request.method == "POST":
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('quiz:quiz_list')
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'quiz/edit_quiz.html', {'form': form, 'questions': questions})





def create_quiz(request):
    allowed_user_types = [2, 1]  # Teacher and Admin user types

    if not request.user.is_authenticated or request.user.user_type not in allowed_user_types:
        return HttpResponseForbidden("You don't have permission to access this page.")

    if request.method == "POST":
        title = request.POST.get('title')
        teacher = request.user.teacher_profile

        video_id = request.POST.get('video')
        video = None  # Default to None

        if video_id:
            try:
                video = Video.objects.get(id=video_id)
            except Video.DoesNotExist:
                messages.error(request, 'Selected video does not exist!')
                return render(request, 'quiz/create_quiz.html')

        if not title:
            messages.error(request, 'Title is required!')
            return render(request, 'quiz/create_quiz.html')

        # Create the quiz and associate it with the video
        quiz = Quiz.objects.create(title=title, teacher=teacher, video=video)
        if video:
            quiz.video = video
            quiz.save()

        # Loop over questions and create them along with their answers
        question_number = 1
        while True:
            question_text_key = f"question_text_{question_number}"
            question_text = request.POST.get(question_text_key)

            # Break the loop if no more questions are found
            if not question_text:
                break

            # Create the question
            question = Question.objects.create(text=question_text, quiz=quiz)
            
            # Add answers for this question
            for choice_number in range(1, 5):
                choice_key = f"choice_{question_number}_{choice_number}"
                choice_text = request.POST.get(choice_key)

                if choice_text:
                    is_correct = request.POST.get(f'correct_choice_{question_number}') == str(choice_number)
                    Answer.objects.create(text=choice_text, question=question, is_correct=is_correct)

            question_number += 1

        quiz.calculate_total_marks()

        messages.success(request, 'Quiz and its questions created successfully!')
        return redirect('quiz:quiz')  # Redirect to wherever you display the quiz

    # Fetch videos for the dropdown
    videos = Video.objects.all()
    # Modified code to fetch videos associated with the logged-in teacher
    # teacher_profile = Teacher.objects.get(user=request.user)
    # videos = Video.objects.filter(teacher=teacher_profile)
    return render(request, 'quiz/create_quiz.html',{'score': Submission.score, 'total_marks': Quiz.total_marks, 'videos': videos})
