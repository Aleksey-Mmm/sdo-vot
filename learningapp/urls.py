from django.urls import path
from . import views
from learningapp.views import *
from django.contrib.auth.decorators import login_required

app_name = 'learningapp'
urlpatterns = [
    path('', login_required(CourseList.as_view()), name='courselist'),
    path('course/<slug:course_slug>', login_required(SelectCourse.as_view()), name='selectcourse'),
    path('course/<slug:course_slug>/lec', login_required(Lections.as_view()), name='lec'),
    path('course/<slug:course_slug>/npa', login_required(Npa.as_view()), name='npa'),
    path('course/<slug:course_slug>/test/<slug:quiz_slug>/<int:quizattempt_id>', login_required(ExamTest.as_view()), name='examtest'),
    path('course/<slug:course_slug>/learning/<slug:quiz_slug>/learning/<int:quizattempt_id>', login_required(LearningTest.as_view()), name='learningtest'),
    path('course/<slug:course_slug>/quizattempts', login_required(QuizAttempts.as_view()), name='quizattempts'),
    path('course/<slug:course_slug>/quizattempts/report/<int:quizattempt_id>', login_required(Report.as_view()), name='report'),
    path('course/<slug:course_slug>/questionslist', login_required(QuestionsList.as_view()), name='questionslist'),
    path('course/<slug:course_slug>/questionslist/<int:question_id>', login_required(SelectQuestion.as_view()), name='selectquestion'),
]
