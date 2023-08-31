from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, request, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse
from django.template.defaulttags import register
from datetime import date, datetime, timedelta, timezone
from django.db.models import Sum, Max
from .models import *
from examapp.models import *
from .utils import *
import json
import random
from django.utils.safestring import mark_safe
from openpyxl import load_workbook, Workbook
from cloitLMS.settings import BASE_DIR, MEDIA_ROOT
import os

@register.filter
def question_count(value, curr_user):
    curr_quiz = Quiz.objects.filter(course = value, name__contains = 'Тренинг')
    quizbanks = QuizBankSettings.objects.filter(quiz__in = curr_quiz)
    sum_questions = Question.objects.none()
    for bank in quizbanks:
        if bank.tag.all().first() != None:
            questions = Question.objects.filter(questions_bank__id = bank.bank.id, status = 1, tag__name = bank.tag.all().first())
            sum_questions = sum_questions | questions
        else:
            questions = Question.objects.filter(questions_bank__id = bank.bank.id, status = 1)
            sum_questions = sum_questions | questions
            
    return sum_questions.count()

@register.filter
def quiz_question_count(value):
    return Question.objects.filter(questions_bank = QuizBankSettings.objects.get(quiz = value).bank, status = 1).count()

@register.filter
def sum_qty(x, y):
    return x + y

@register.filter
def report_max_grade(attempt):
    curr_quiz = Quiz.objects.get(pk = attempt.quiz.id)
    if 'Тренинг ' in curr_quiz.name:
        max_grade = LearningQuizAttemptQuestions.objects.filter(learningquizattempt = attempt).count()
    else:
        max_grade = curr_quiz.max_grade
    return max_grade

@register.filter
def percent_result(attempt):
    curr_quiz = Quiz.objects.get(pk = attempt.quiz.id)
    if 'Тренинг ' in curr_quiz.name:
        quotient = attempt.grade / LearningQuizAttemptQuestions.objects.filter(learningquizattempt = attempt).count()
        percent = quotient * 100
    else:
        quotient = attempt.grade / curr_quiz.max_grade
        percent = quotient * 100
    return round(percent)

@register.filter
def percent_learningtest(quiz_slug, user):
    see_questions = QuestionСoefficient.objects.filter(quiz__slug = quiz_slug, user = user, status = 1)
    try:
        quotient = see_questions.exclude(coefficient = None).count() / see_questions.count()
    except:
        quotient = 0
    percent = quotient * 100
    return round(percent)

@register.filter
def get_learning_time(value, user):
    try:
        time = LearningQuizAttemptGrade.objects.filter(
                quiz_attempt__in = LearningQuizAttempt.objects.filter(
                    user = user,
                    quiz__in = Quiz.objects.filter(course = value)
                    )).aggregate(Sum('spend_time'))
        return timedelta(seconds = time['spend_time__sum'])
    except:
        return 0

@register.filter
def get_quiz_learning_time(value, user):
    try:
        time = LearningQuizAttemptGrade.objects.filter(
                quiz_attempt__in = LearningQuizAttempt.objects.filter(
                    user = user,
                    quiz = Quiz.objects.get(name = value)
                    )).aggregate(Sum('spend_time'))
        return timedelta(seconds = time['spend_time__sum'])
    except:
        return 0

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    if d["hours"] < 10:
        d["hours"] = '0' + str(d["hours"])
    if d["minutes"] < 10:
        d["minutes"] = '0' + str(d["minutes"])
    if d["seconds"] < 10:
        d["seconds"] = '0' + str(d["seconds"])
    return fmt.format(**d)

@register.filter
def delta(value, arg):
    delta_ressult = value - arg   
    return strfdelta(delta_ressult, "{hours}:{minutes}:{seconds}")

@register.filter
def shuffle(arg):
    my_list = list(arg[:])
    random.shuffle(my_list)
    return my_list

@register.filter
def get_studied_questions(value, user):
    try:
        return QuestionСoefficient.objects.filter(user = user, coefficient__gte = 23, quiz__in = Quiz.objects.filter(course = value, name__contains = 'Тренинг'), status = 1).count()
    except:
        return 0

@register.filter
def get_quiz_studied_questions(value, user):
    try:
        return QuestionСoefficient.objects.filter(user = user, coefficient__gte = 23, quiz = value, status = 1).count()
    except:
        return 0

@register.filter
def get_percent(value, user):
    try:
        percent = QuestionСoefficient.objects.filter(user = user, quiz = Quiz.objects.get(course = value, name__contains = 'Тренинг'), status = 1)
        percent = percent.filter(coefficient__gte = 23).count() / percent.count() * 100
        
        return round(percent)
    except:
        
        return 0

@register.filter
def decodeDesignImage(data, is_safe=True):
    return mark_safe(data)

class CheckUserPermissions(UserPassesTestMixin):
    def test_func(self):
        return (True if not self.request.user.groups.filter(name='manager').exists() else False)
    
    def handle_no_permission(self):
        return redirect('managementapp:users')

class CourseList(CheckUserPermissions, ListView):
    model = UserRegisteredCourse
    template_name = 'learningapp/home.html'
    context_object_name = 'object_list'

    def get_queryset(self, **kwargs):
        return (
            UserRegisteredCourse.objects
            .filter(user = self.request.user)
            .exclude(timefinish = None)
            .select_related('course')
            .order_by('-id'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class SelectCourse(CheckUserPermissions, DetailView):
    model = Course
    context_object_name = 'object'
    template_name = 'learningapp/select course.html'
    
    def get_object(self):
        return get_object_or_404(Course, slug = self.kwargs['course_slug'])
        
    def post(self, request, **kwargs):
                
        if request.POST.get("form_type") == 'learningtest':
            
            curr_quiz = Quiz.objects.get(course__slug = self.kwargs['course_slug'], name__contains = 'Тренинг')

            last_quiz_attempt, created_quiz_attempt = LearningQuizAttempt.objects.get_or_create(
                quiz = curr_quiz,
                user = self.request.user,
                grade = 0,
                status = Status.objects.get(name = 'В процессе'),
            )
            if created_quiz_attempt == True:
                quizbanks = QuizBankSettings.objects.filter(quiz = curr_quiz)
                bulk_list = []
                sum_questions = Question.objects.none()
                for bank in quizbanks:
                    if bank.tag.all().first():
                        questions = Question.objects.filter(questions_bank__id = bank.bank.id, status = 1, tag__name = bank.tag.all().first())
                    else:
                        questions = Question.objects.filter(questions_bank__id = bank.bank.id, status = 1)
                    last_quiz_attempt.questions.add(*questions.order_by('?')[:bank.qty])
                    sum_questions = sum_questions | questions                
                
                upd = LearningQuizAttemptQuestions.objects.filter(learningquizattempt = last_quiz_attempt).first()
                upd.see_question = False
                upd.save()
                bulk_questions = Question.objects.filter(pk__in = sum_questions)
                status_approved = Status.objects.get(name = 'Утвержден')
                for question in bulk_questions:
                    if not QuestionСoefficient.objects.filter(user = self.request.user, quiz = curr_quiz, question = question, status = status_approved).exists():
                        bulk_list.append(QuestionСoefficient(user = self.request.user, quiz = curr_quiz, question = question, status = status_approved))
                QuestionСoefficient.objects.bulk_create(bulk_list)
            
            return redirect('learningapp:learningtest', course_slug = self.kwargs['course_slug'], quiz_slug = curr_quiz.slug, quizattempt_id = last_quiz_attempt.id)
                    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_slug'] = self.kwargs['course_slug']
        context['register_course'] = self.request.user.userregisteredcourse_set.get(course__slug = self.kwargs['course_slug'])
        context['npa'] = Upload.objects.filter(course__slug = self.kwargs['course_slug'], description__contains = 'НПА').exists()
        context['lec'] = Upload.objects.filter(course__slug = self.kwargs['course_slug'], description__contains = 'Лекция').exists()

        return context

class ExamTest(CheckUserPermissions, ListView):
    model = LearningQuizAttempt
    context_object_name = 'object_list'
    paginate_by = 1
    template_name = 'learningapp/examtest.html'
    __start_time = None
    __checked_page = list()

    def get_queryset(self, **kwargs):
        return (
            LearningQuizAttempt.objects
            .select_related('user')
            .prefetch_related('questions')
            .get(pk=self.kwargs['quizattempt_id'])
            .questions
            .order_by()
        )

    def post(self, request, *args, **kwargs):
        if 'page' in self.request.GET:
            page_num = self.request.GET['page']
        else:
            page_num = 1
        if request.POST.getlist('answeroption') != []:
            select_answer = request.POST.getlist('answeroption')
            for obj in select_answer:
                curr_answer = Answer.objects.get(pk = obj)
                LearningQuizAttemptGrade.objects.filter(
                    quiz_attempt = self.kwargs['quizattempt_id'],
                    question = curr_answer.question.id,
                ).exclude(answer__in = select_answer).update(status = '')
                
                last, created = LearningQuizAttemptGrade.objects.get_or_create(
                    quiz_attempt = LearningQuizAttempt.objects.get(pk = self.kwargs['quizattempt_id']), 
                    question = curr_answer.question,
                    answer = curr_answer, 
                    weight = curr_answer.weight,
                    status = 'checked'
                )
            
            LearningQuizAttemptGrade.objects.filter(pk = last.id).update(spend_time = ((datetime.now() - ExamTest.__start_time).seconds if ExamTest.__start_time != None else 15))           
            if page_num not in self.__checked_page:
                self.__checked_page.append(int(page_num))

        if int(page_num) == LearningQuizAttempt.objects.get(pk = self.kwargs['quizattempt_id']).questions.all().count():
            AddQuizAttemptGrade(self.kwargs['quizattempt_id'])
            ExamTest.__start_time = None
            self.__checked_page.clear()
            return redirect('learningapp:quizattempts', course_slug = self.kwargs['course_slug'])
        else:
            page_num = str(int(page_num) + 1)
            return HttpResponseRedirect("?page=%s" % page_num)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        curr_quiz_attempt = LearningQuizAttempt.objects.get(pk = self.kwargs['quizattempt_id'])
        answers_options = list(answer.answer.id for answer in LearningQuizAttemptGrade.objects.filter(question = context['object_list'], quiz_attempt=self.kwargs['quizattempt_id'], status='checked'))
        context['checked_page'] = self.__checked_page
        context['answers_options'] = answers_options
        context['course_slug'] = self.kwargs['course_slug']
        context['quiz_slug'] = self.kwargs['quiz_slug']
        context['quiz'] = Quiz.objects.get(slug = self.kwargs['quiz_slug'])
        context['js_end_date']= json.dumps(curr_quiz_attempt.timefinish.strftime("%Y-%m-%dT%H:%M:%S"))
        context['timer_time'] = (
            (('0' + str(curr_quiz_attempt.timefinish - datetime.now())[:1] + ' ч ') if str(curr_quiz_attempt.timefinish - datetime.now())[:1] == '1' else '00 ч ') +
            (str(curr_quiz_attempt.timefinish - datetime.now()))[2:4] + ' мин ' +
            (str(curr_quiz_attempt.timefinish - datetime.now()))[5:7] + ' сек '
        )

        return context

    def get(self, request, *args, **kwargs):
        curr_quiz_attempt = LearningQuizAttempt.objects.get(pk = self.kwargs['quizattempt_id'])

        if curr_quiz_attempt.user != self.request.user:
            return redirect('learningapp:courselist')

        if curr_quiz_attempt.timefinish == None:
            quiz_attempt = curr_quiz_attempt
            quiz_attempt.timefinish = (datetime.now() + timedelta(minutes = Quiz.objects.get(slug = self.kwargs['quiz_slug']).timelimit))
            quiz_attempt.save()

        if (curr_quiz_attempt.timefinish != None) and (curr_quiz_attempt.timefinish.timestamp() < datetime.now().timestamp()):
            ExamTest.__start_time = None
            AddQuizAttemptGrade(self.kwargs['quizattempt_id'])
            return redirect('learningapp:quizattempts', course_slug = self.kwargs['course_slug'])
        
        ExamTest.__start_time = datetime.now()
        
        return super().get(request, *args, **kwargs)

class QuizAttempts(CheckUserPermissions, ListView):
    model = LearningQuizAttempt
    context_object_name = 'object_list'
    paginate_by = 3
    template_name = 'learningapp/quiz attempts.html'

    def dispatch(self, request, *args, **kwargs):
        self.curr_quiz = Quiz.objects.get(
            course__slug = self.kwargs['course_slug'],
            name__contains = 'Проверка знаний'
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return LearningQuizAttempt.objects.filter(
            user = self.request.user,
            quiz = self.curr_quiz
        ).prefetch_related('questions').order_by('-timestart')   
    
    def post(self, request, **kwargs):
        last_quiz_attempt, created_quiz_attempt = LearningQuizAttempt.objects.get_or_create(
            quiz = self.curr_quiz,
            user = self.request.user,
            grade = 0,
            status = Status.objects.get(name = 'В процессе'),
        )

        if created_quiz_attempt == True:
            quizbanks = QuizBankSettings.objects.filter(quiz = self.curr_quiz)
            for bank in quizbanks:
                if bank.tag.all().first():
                    questions = Question.objects.filter(questions_bank__id = bank.bank.id, status = 1, tag__name = bank.tag.all().first()).order_by('?')[:bank.qty]
                else:
                    questions = Question.objects.filter(questions_bank__id = bank.bank.id, status = 1).order_by('?')[:bank.qty]
                
                last_quiz_attempt.questions.add(*questions)
                    
        return redirect('learningapp:examtest', course_slug = self.kwargs['course_slug'], quiz_slug = self.curr_quiz.slug, quizattempt_id = last_quiz_attempt.id)
                
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_slug = Quiz.objects.get(course__slug=self.kwargs['course_slug'], name__contains='Проверка знаний').slug
        context.update({
            'quiz_test': quiz_slug,
            'course_slug': self.kwargs['course_slug'],
            'course': Course.objects.get(slug=self.kwargs['course_slug']),
            'quiz_slug': quiz_slug,
            'last_attempt': LearningQuizAttempt.objects.filter(
                user=self.request.user,
                quiz__course__slug = self.kwargs['course_slug'],
                quiz__name__contains = 'Проверка знаний'
            ).aggregate(last_attempt=Max('id'))['last_attempt']
        })

        return context

@register.filter
def attempt_answers(question, quiz_attempt):
    return Answer.objects.filter(
        pk__in = LearningQuizAttemptGrade.objects
        .filter(
            question = question, quiz_attempt = quiz_attempt, status = 'checked'
            )
        .values('answer')
    )

class Report(CheckUserPermissions, DetailView):
    model = LearningQuizAttempt
    context_object_name = 'object'
    template_name = 'learningapp/report.html'

    def get_object(self, **kwargs):
        return LearningQuizAttempt.objects.get(pk = self.kwargs['quizattempt_id'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quiz_test'] = Quiz.objects.get(course__slug = self.kwargs['course_slug'], name__contains = 'Проверка знаний').slug
        context['course_slug'] = self.kwargs['course_slug']
        context['quizattempt_id'] = self.kwargs['quizattempt_id']
        context['extend_user'] = ExtendingUserFields.objects.get(user = self.get_object().user)
        context['attempt_questions'] = Question.objects.filter(pk__in = LearningQuizAttemptGrade.objects.filter(quiz_attempt = self.kwargs['quizattempt_id']).values('question'))

        return context

class Lections(CheckUserPermissions, ListView):
    model = Upload
    context_object_name = 'object_list'
    template_name = 'learningapp/lec.html'
    
    def get_queryset(self, **kwargs):
        return Upload.objects.filter(course__slug = self.kwargs['course_slug'], description__contains = 'Лекция').order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_slug'] = self.kwargs['course_slug']

        return context

class Npa(CheckUserPermissions, ListView):
    model = Upload
    context_object_name = 'object_list'
    template_name = 'learningapp/npa.html'
    
    def get_queryset(self, **kwargs):
        return Upload.objects.filter(course__slug = self.kwargs['course_slug'], description__contains = 'НПА').order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_slug'] = self.kwargs['course_slug']

        return context

class LearningTest(CheckUserPermissions, DetailView):
    model = Question
    template_name = 'learningapp/learningtest.html'
    context_object_name = 'object'
    __CURR_ANSWERS = None
    __start_time = datetime.now()
    __CURR_QUESTION = None

    def get_object(self, **kwargs):
        try:
            obj = LearningQuizAttemptQuestions.objects.get(see_question = False, learningquizattempt = self.kwargs['quizattempt_id']).question
            self.__CURR_QUESTION = obj
            return obj
        except:
            if LearningQuizAttemptQuestions.objects.filter(see_question = False, learningquizattempt = self.kwargs['quizattempt_id']).count() > 1:
                LearningQuizAttemptQuestions.objects.filter(see_question = False, learningquizattempt = self.kwargs['quizattempt_id']).exclude(pk = LearningQuizAttemptQuestions.objects.filter(see_question = False, learningquizattempt = self.kwargs['quizattempt_id']).first().id).update(see_question = None)
                obj = LearningQuizAttemptQuestions.objects.get(see_question = False, learningquizattempt = self.kwargs['quizattempt_id']).question
                self.__CURR_QUESTION = obj
                return obj
            elif LearningQuizAttemptQuestions.objects.filter(see_question = False, learningquizattempt = self.kwargs['quizattempt_id']).count() == 0:
                obj = LearningQuizAttemptQuestions.objects.filter(see_question = None, learningquizattempt = self.kwargs['quizattempt_id']).first()
                obj.see_question = False
                obj.save()
                obj = LearningQuizAttemptQuestions.objects.get(see_question = False, learningquizattempt = self.kwargs['quizattempt_id']).question
                self.__CURR_QUESTION = obj
                return obj
            raise Http404("No MyModel matches the given query.")
    
    def __del__(self, **kwargs):
        LearningTest.__start_time = datetime.now()        

    def post(self, request, *args, **kwargs):
        curr_quiz = Quiz.objects.get(slug = self.kwargs['quiz_slug'])
        last_quiz_attempt = LearningQuizAttempt.objects.get(pk = self.kwargs['quizattempt_id'])
        upd_true = LearningQuizAttemptQuestions.objects.get(learningquizattempt = self.kwargs['quizattempt_id'], see_question = False)        
        
        if request.POST.get("form_type") == 'next':
            
            if LearningQuizAttemptGrade.objects.filter(quiz_attempt = last_quiz_attempt, status = 'checked').last() != None and LearningQuizAttemptGrade.objects.filter(quiz_attempt = last_quiz_attempt, status = 'checked').last() == LearningQuizAttemptGrade.objects.filter(quiz_attempt = last_quiz_attempt, status = 'checked', question = self.get_object()).last():
                
                try:
                    upd_flase = LearningQuizAttemptQuestions.objects.filter(learningquizattempt = self.kwargs['quizattempt_id'], see_question = None).order_by('?')[:1].first()
                    upd_flase.see_question = False
                    upd_flase.save()
                    upd_true.see_question = True
                    upd_true.save()
                except:
                    if LearningQuizAttemptQuestions.objects.filter(learningquizattempt = self.kwargs['quizattempt_id'], see_question = None).count() == 0:
                        upd_none = LearningQuizAttemptQuestions.objects.filter(learningquizattempt = self.kwargs['quizattempt_id'], see_question = True).first()
                        upd_none.see_question = None
                        upd_none.save()
                        
                        upd_flase = LearningQuizAttemptQuestions.objects.filter(learningquizattempt = self.kwargs['quizattempt_id'], see_question = None).order_by('?')[:1].first()
                        upd_flase.see_question = False
                        upd_flase.save()
                        upd_true.see_question = True
                        upd_true.save()
                
                if LearningQuizAttemptQuestions.objects.filter(learningquizattempt = self.kwargs['quizattempt_id'], see_question = None).count() == 0:
                    upd_none = LearningQuizAttemptQuestions.objects.filter(learningquizattempt = self.kwargs['quizattempt_id'], see_question = True).first()
                    upd_none.see_question = None
                    upd_none.save()

                return super(LearningTest, self).get(request, **kwargs)

            else:
                
                if request.POST.getlist('answeroption') != []:
                    list_answer = []
                    select_answer = request.POST.getlist('answeroption')
                    curr_question_weight = 0
                    for obj in select_answer:
                        list_answer.append(int(obj))
                        curr_answer = Answer.objects.get(pk = obj)
                        if len(select_answer) == 1:
                            curr_question_weight += curr_answer.weight
                        else:
                            if curr_answer.weight != 1:
                                if curr_answer.weight == 1:
                                    curr_question_weight += 10
                                else:
                                    curr_question_weight += curr_answer.weight
                    
                    self.__CURR_ANSWERS = list_answer
                    
                    if curr_question_weight < 0.9 and curr_question_weight > 1:
                        curr_question_weight = 0

                    LearningQuizAttemptGrade.objects.create(
                        quiz_attempt = last_quiz_attempt, 
                        question = curr_answer.question, 
                        spend_time = (datetime.now() - LearningTest.__start_time).seconds,  
                        weight = curr_question_weight, 
                        status = 'checked'
                        )
                    
                    QuestionСoefficient.add_coeff(last_quiz_attempt = last_quiz_attempt, curr_answer = curr_answer, curr_quiz = curr_quiz, user = self.request.user)
                    
                    if LearningQuizAttemptQuestions.objects.filter(learningquizattempt = self.kwargs['quizattempt_id'], see_question = None).count() == 1:
                        notseen = Question.objects.filter(
                            pk__in = QuestionСoefficient.objects
                            .filter(status = 1, quiz = curr_quiz, user = self.request.user, coefficient = None)
                            .exclude(pk = upd_true.question.id)
                            .values('question')
                            .order_by('?')[:curr_quiz.max_grade/2]
                            )
                        good = Question.objects.filter(
                            pk__in = QuestionСoefficient.objects
                            .filter(status = 1, quiz = curr_quiz, user = self.request.user, coefficient__gte = 12, coefficient__lte = 23)
                            .exclude(pk = upd_true.question.id)
                            .values('question')
                            ).order_by('?')[:curr_quiz.max_grade/5]
                        bad = Question.objects.filter(
                            pk__in = QuestionСoefficient.objects
                            .filter(status = 1, quiz = curr_quiz, user = self.request.user, coefficient__gte = 0, coefficient__lte = 11)
                            .exclude(pk = upd_true.question.id).values('question')
                            ).order_by('?')[:curr_quiz.max_grade/5]
                        
                        if notseen.count() != curr_quiz.max_grade/2:
                            notseen = Question.objects.filter(
                                pk__in = QuestionСoefficient.objects
                                .filter(status = 1, quiz = curr_quiz, user = self.request.user, coefficient = None)
                                .exclude(pk = upd_true.question.id).values('question')
                                .order_by('?')[:notseen.count()]
                                )
                            notseen = notseen | Question.objects.filter(
                                pk__in = QuestionСoefficient.objects
                                .filter(status = 1, quiz = curr_quiz, user = self.request.user)
                                .exclude(pk = upd_true.question.id)
                                .exclude(pk__in = notseen)
                                .exclude(pk__in = good)
                                .exclude(pk__in = bad)
                                .order_by('coefficient')
                                .values('question')[:curr_quiz.max_grade/2 - notseen.count()]
                                )

                        if good.count() != curr_quiz.max_grade/5:
                            good = Question.objects.filter(
                                pk__in = QuestionСoefficient.objects
                                .filter(status = 1, quiz = curr_quiz, user = self.request.user, coefficient__gte = 12, coefficient__lte = 23)
                                .exclude(pk = upd_true.question.id)
                                .values('question')
                                ).order_by('?')[:good.count()]
                            good = good | Question.objects.filter(
                                pk__in = QuestionСoefficient.objects
                                .filter(status = 1, quiz = curr_quiz, user = self.request.user)
                                .exclude(pk = upd_true.question.id)
                                .exclude(pk__in = notseen)
                                .exclude(pk__in = good)
                                .exclude(pk__in = bad)
                                .order_by('coefficient')
                                .values('question')[:curr_quiz.max_grade/5 - good.count()]
                                )
                        
                        if bad.count() != curr_quiz.max_grade/5:
                            bad = Question.objects.filter(
                                pk__in = QuestionСoefficient.objects
                                .filter(status = 1, quiz = curr_quiz, user = self.request.user, coefficient__gte = 0, coefficient__lte = 11)
                                .exclude(pk = upd_true.question.id)
                                .values('question')
                                ).order_by('?')[:bad.count()]
                            bad = bad | Question.objects.filter(
                                pk__in = QuestionСoefficient.objects
                                .filter(status = 1, quiz = curr_quiz, user = self.request.user)
                                .exclude(pk = upd_true.question.id)
                                .exclude(pk__in = notseen)
                                .exclude(pk__in = good)
                                .exclude(pk__in = bad)
                                .order_by('coefficient')
                                .values('question')[:curr_quiz.max_grade/5 - bad.count()]
                                )

                        LearningQuizAttemptQuestions.objects.filter(
                            learningquizattempt = self.kwargs['quizattempt_id'], question__in = (notseen | good | bad)
                            ).exclude(
                                question = upd_true.question
                                ).update(see_question = None)
                        last_quiz_attempt.questions.add(*(notseen | good | bad))

                    return super(LearningTest, self).get(request, **kwargs)
                
                else:
                    messages.error(request, 'Выберите вариант ответа!')
                    return super(LearningTest, self).get(request, **kwargs)
                
        if 'question_' in request.POST.get("form_type"):
            upd_flase = LearningQuizAttemptQuestions.objects.get(
                learningquizattempt = self.kwargs['quizattempt_id'], question__id = int(str(request.POST.get("form_type"))
                .replace('question_', ''))
                )
            upd_true.see_question = None
            upd_true.save()
            upd_flase.see_question = False
            upd_flase.save()

        return super(LearningTest, self).get(request, **kwargs)
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_slug'] = self.kwargs['course_slug']
        context['quiz_slug'] = self.kwargs['quiz_slug']
        context['quizattempt_id'] = self.kwargs['quizattempt_id']
        context['quiz'] = Quiz.objects.get(slug = self.kwargs['quiz_slug'])
        context['check_answer'] = self.__CURR_ANSWERS
        context['question_list'] = (
            QuestionСoefficient.objects
            .filter(status = 1, quiz__slug = self.kwargs['quiz_slug'], user = self.request.user)
            .select_related('question')
            .order_by('id')
            .values('question__id', 'coefficient', 'sequence_false', 'sequence_true', 'qty_true_answer')
            )
        LearningTest.__start_time = datetime.now()
        return context

class QuestionsList(CheckUserPermissions, ListView):
    model = Question
    context_object_name = 'object_list'
    template_name = 'learningapp/questionslist.html'
    __course = None
    __register_course = None
    
    def get_queryset(self, **kwargs):
        
        curr_quiz = Quiz.objects.get(course__slug = self.kwargs['course_slug'], name__contains = 'Тренинг')
        quizbanks = QuizBankSettings.objects.filter(quiz = curr_quiz)
        sum_questions = Question.objects.none()
        for bank in quizbanks:
            questions = Question.objects.filter(questions_bank__id = bank.bank.id, status = 1, tag__name = bank.tag.all().first())
            sum_questions = sum_questions | questions
                
        return sum_questions
    
    def get(self, request, *args, **kwargs):
        self.__course = Course.objects.get(slug = self.kwargs['course_slug'])
        self.__register_course = UserRegisteredCourse.objects.get(course__slug = self.kwargs['course_slug'], user = self.request.user)
        if self.__register_course.vot_qty <= 0 or self.__register_course.vot == False:
            return redirect('learningapp:selectcourse', course_slug = self.kwargs['course_slug'])

        return super(QuestionsList, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_slug'] = self.kwargs['course_slug']
        context['course'] = self.__course
        context['register_course'] = self.__register_course         
        
        return context

class SelectQuestion(CheckUserPermissions, DetailView):
    template_name = 'learningapp/selectquestion.html'
    context_object_name = 'object'
    __course = None
    __register_course = None

    def get_object(self, **kwargs):
        return Question.objects.get(pk = self.kwargs['question_id'])

    def get(self, request, *args, **kwargs):
        self.__course = Course.objects.get(slug = self.kwargs['course_slug'])
        self.__register_course = UserRegisteredCourse.objects.get(course__slug = self.kwargs['course_slug'], user = self.request.user)
        if self.__register_course.vot_qty <= 0 or self.__register_course.vot == False:
            return redirect('learningapp:selectcourse', course_slug = self.kwargs['course_slug'])
        self.__register_course.vot_qty = self.__register_course.vot_qty - 1
        self.__register_course.save()

        return super(SelectQuestion, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_slug'] = self.kwargs['course_slug']
        context['course'] = self.__course
        context['register_course'] = self.__register_course 
        
        return context
