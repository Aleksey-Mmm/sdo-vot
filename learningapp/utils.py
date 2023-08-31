from .models import *
from datetime import datetime, timedelta
from django.db.models import Sum

def AddQuizAttemptGrade(curr_quizattempt):
    grade = 0

    grade = LearningQuizAttemptGrade.objects.filter(quiz_attempt = curr_quizattempt, weight = 1, status = 'checked').count()
    for question in LearningQuizAttemptGrade.objects.filter(quiz_attempt = curr_quizattempt, status = 'checked').exclude(weight = 1).values_list('question', flat=True).distinct():
        if not 0 in LearningQuizAttemptGrade.objects.filter(quiz_attempt = curr_quizattempt, question = question, status = 'checked').values_list('weight', flat=True):
            if LearningQuizAttemptGrade.objects.filter(quiz_attempt = curr_quizattempt, question = question, status = 'checked').aggregate(Sum('weight'))['weight__sum'] > 0.9:
               grade += 1

    curr_attempt = LearningQuizAttempt.objects.get(pk = curr_quizattempt)

    LearningQuizAttempt.objects.filter(pk = curr_quizattempt).update(
        grade = grade, 
        timefinish = (datetime.now() if datetime.now() - curr_attempt.timestart < (curr_attempt.timestart + timedelta(minutes=20) - curr_attempt.timestart) else curr_attempt.timestart + timedelta(minutes=20)), 
        status = Status.objects.get(pk = 3)
        )
         