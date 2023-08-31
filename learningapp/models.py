from pyexpat import model
from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from django.contrib.auth.models import User
from django.db.models.fields import CharField
import datetime
from django.utils import timezone
from examapp.models import *


class UserRegisteredCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Ученик')
    course = models.ForeignKey(Course, on_delete=PROTECT, verbose_name='Курс')
    manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name='manager_user', verbose_name='Менеджер')
    timeregistered = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    timeactive = models.DateTimeField(blank=True, null=True, verbose_name='Дата активации')
    timefinish = models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')
    vot = models.BooleanField(blank=True, null=True, verbose_name='Вопрос ответ')
    vot_qty = models.IntegerField(blank=True, null=True, verbose_name='Кол-во попыток ВОТ')
    problem = models.BooleanField(blank=True, null=True, verbose_name='Задачи')
    interview = models.BooleanField(blank=True, null=True, verbose_name='Собеседование')
    status = models.ForeignKey(Status, blank=True, null=True, on_delete=PROTECT, verbose_name='Статус')


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Обучение курс пользователя'
        verbose_name_plural = 'Обучение курсы пользователей'

class LearningQuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=PROTECT, verbose_name='Тест')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Ученик')
    questions = models.ManyToManyField(Question, through='LearningQuizAttemptQuestions', through_fields=('learningquizattempt', 'question'))
    grade = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='Оценка')
    status = models.ForeignKey(Status, on_delete=PROTECT, verbose_name='Статус')
    timestart = models.DateTimeField(auto_now_add=True, verbose_name='Начало теста')
    timefinish = models.DateTimeField(blank=True, null=True, verbose_name='Конец теста')

    class Meta:
        verbose_name = 'Обучение Попытка'
        verbose_name_plural = 'Обучение Попытки'

class LearningQuizAttemptQuestions(models.Model):
    learningquizattempt = models.ForeignKey(LearningQuizAttempt, on_delete=CASCADE)
    question = models.ForeignKey(Question, on_delete=CASCADE)
    see_question = models.BooleanField(blank=True, null=True)

class LearningQuizAttemptGrade(models.Model):
    quiz_attempt = models.ForeignKey(LearningQuizAttempt, on_delete=CASCADE, verbose_name='Попытка')
    question = models.ForeignKey(Question, on_delete=PROTECT, verbose_name='Вопрос')
    answer = models.ForeignKey(Answer, on_delete=PROTECT, blank=True, null=True, verbose_name='Ответ')
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='Вес ответа')
    spend_time = models.BigIntegerField(blank=True, null=True, verbose_name='Затречено времени')
    status = models.CharField(max_length=255, blank=True, verbose_name='Статус ответа')

    class Meta:
        verbose_name = 'Обучение Детализация попытки теста'
        verbose_name_plural = 'Обучение Детализация попыток тестов'  

    @classmethod
    def get_weight(cls, last_quiz_attempt, curr_answer):
        qq = cls.objects.filter(quiz_attempt = last_quiz_attempt, status = 'checked', question = curr_answer.question).last()
        if qq.weight > 0.9 and qq.weight <= 1:
            return 1
        else:
            return 0
    
    @classmethod
    def get_sequence(cls, last_quiz_attempt, curr_answer):
        curr_querry = cls.objects.filter(quiz_attempt = last_quiz_attempt, status = 'checked', question = curr_answer.question)
        if curr_querry.count() != 1:
            weight_list = []
            for x in curr_querry.order_by('-id')[:2]:
                weight_list.append(x.weight)
            if weight_list.count(1) == 2:
                return 1
            elif weight_list.count(0) == 2:
                return 0
            
class QuestionСoefficient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Ученик')
    quiz = models.ForeignKey(Quiz, on_delete=CASCADE, verbose_name='Тест')
    question = models.ForeignKey(Question, on_delete=CASCADE, verbose_name='Вопрос')
    sequence_true = models.IntegerField(default=0, verbose_name='Последовательность верных ответов')
    qty_true_answer = models.IntegerField(default=0, verbose_name='Кол-во верных ответов')
    sequence_false = models.IntegerField(default=0, verbose_name='Последовательность неверных ответов')
    qty_false_answer = models.IntegerField(default=0, verbose_name='Кол-во неверных ответов')
    coefficient = models.IntegerField(blank=True, null=True, verbose_name='Вес вопроса')
    status = models.ForeignKey(Status, on_delete=PROTECT, blank=True, null=True, verbose_name='Статус')

    class Meta:
        verbose_name = 'Вес вопроса'
        verbose_name_plural = 'Вес вопросов'

    @classmethod
    def update_qty_true(cls, user, curr_quiz, curr_answer):
        curr_coeff = cls.objects.get(user = user, quiz = curr_quiz, question = curr_answer.question)
        cls.objects.filter(user = user, quiz = curr_quiz, question = curr_answer.question).update(
            qty_true_answer = curr_coeff.qty_true_answer + 1,
            coefficient = (curr_coeff.coefficient + 1 if curr_coeff.coefficient != None else 1)
            )
    
    @classmethod
    def update_qty_false(cls, user, curr_quiz, curr_answer):
        curr_coeff = cls.objects.get(user = user, quiz = curr_quiz, question = curr_answer.question)
        coeff = curr_coeff.coefficient - 1 if curr_coeff.coefficient != None and curr_coeff.coefficient >= 1 else 0
        cls.objects.filter(user = user, quiz = curr_quiz, question = curr_answer.question).update(
            qty_false_answer = curr_coeff.qty_false_answer + 1,
            coefficient = coeff
            )    
    
    @classmethod
    def update_sequence_true(cls, user, curr_quiz, curr_answer):
        curr_coeff = cls.objects.get(user = user, quiz = curr_quiz, question = curr_answer.question)
        cls.objects.filter(user = user, quiz = curr_quiz, question = curr_answer.question).update(
            sequence_true = curr_coeff.sequence_true + 1,
            coefficient = curr_coeff.coefficient + 10
            )
    
    @classmethod
    def update_sequence_false(cls, user, curr_quiz, curr_answer):
        curr_coeff = cls.objects.get(user = user, quiz = curr_quiz, question = curr_answer.question)
        cls.objects.filter(user = user, quiz = curr_quiz, question = curr_answer.question).update(
            sequence_false = curr_coeff.sequence_false + 1
            )
    
    @classmethod
    def add_coeff(cls, last_quiz_attempt, curr_answer, curr_quiz, user):
        if LearningQuizAttemptGrade.get_weight(last_quiz_attempt, curr_answer) == 1:
            QuestionСoefficient.update_qty_true(user, curr_quiz, curr_answer)
            
        else:
            QuestionСoefficient.update_qty_false(user, curr_quiz, curr_answer)
        
        if LearningQuizAttemptGrade.get_sequence(last_quiz_attempt, curr_answer) == 1:
            QuestionСoefficient.update_sequence_true(user, curr_quiz, curr_answer)
            
        elif LearningQuizAttemptGrade.get_sequence(last_quiz_attempt, curr_answer) == 0:
            QuestionСoefficient.update_sequence_false(user, curr_quiz, curr_answer)
