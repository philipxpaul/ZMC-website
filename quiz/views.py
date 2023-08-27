from django.shortcuts import render, redirect
from .models import Quiz, Question, Answer,Submission, SubmissionAnswer,Teacher,Student
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from .form import QuizForm
from django.contrib.auth.decorators import login_required
from users.models import Video
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .models import Quiz, Question, Answer
from django.http import HttpResponse
# ... other imports
from django.db.models import Sum





def quiz_results(request):
    # Ensure the user is authenticated and is a teacher
    if not request.user.is_authenticated or getattr(request.user, 'user_type', None) != 2:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('users/center.html')

    try:
        teacher_profile = Teacher.objects.get(user=request.user)
        students = Student.objects.filter(teacher=teacher_profile)
        quizzes = Quiz.objects.filter(teacher=teacher_profile)


        # Initialize filters from the request
        student_code_filter = request.GET.get('student_code', '')
        name_filter = request.GET.get('name', '')
        advisor_filter = request.GET.get('advisor', '')
        total_score_filter = request.GET.get('total_score', '')
        quiz_title_filter = request.GET.get('quiz_title', '')
        
        
        # You had already initiated an empty results list
        results = []

        for student in students:
            student_data = {
                'code': student.code,
                'name': student.name,
                'advisor': student.advisor if student.advisor else "N/A", 
                'total_score': 0,  
                'quiz_data': []
            }

            # Fetch all submissions for this student
            submissions = Submission.objects.filter(student=student)
            for submission in submissions:
                if submission.quiz.teacher == teacher_profile:
                    student_data['quiz_data'].append({
                    'title': submission.quiz.title,
                    'score': submission.score
                    })

                    student_data['total_score'] += submission.score
            
            # Check filters before appending to results
            if student_code_filter and student_code_filter not in student_data['code']:
                continue
            if name_filter and name_filter not in student_data['name']:
                continue
            if advisor_filter and advisor_filter not in student_data['advisor']:
                continue
            if total_score_filter:
                try:
                    if int(total_score_filter) != student_data['total_score']:
                        continue

                except ValueError:
                    # Handle the case where total_score_filter is not a valid integer.
                    continue
            if quiz_title_filter:
                quiz_titles = [quiz['title'] for quiz in student_data['quiz_data']]
                if quiz_title_filter not in quiz_titles:
                    continue
            results.append(student_data)

        # Filter quizzes by title, if the filter exists
        if quiz_title_filter:
            quizzes = quizzes.filter(title__icontains=quiz_title_filter)

        context = {
            'results': results,
            'quizzes': quizzes
        }

        return render(request, 'quiz/quiz_results.html', context)

    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
        return redirect('dashboard')




@login_required
def quiz_list(request):
    # Ensure the user is authenticated and is a stude
    quizzes = Quiz.objects.all()
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
