from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views.generic import ListView, DetailView, CreateView, TemplateView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from examapp.models import *
from learningapp.models import LearningQuizAttempt, QuestionСoefficient, LearningQuizAttemptQuestions
from managementapp.models import Subscription
from django.template.defaulttags import register
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from openpyxl import load_workbook, Workbook

@register.filter
def count(value):
    return Question.objects.filter(status__id = 1, questions_bank__in = value).count()

@register.filter
def get_saler(value):
    print(User.objects.filter(username = value).values('groups__name'))
    return value

class CheckAdminPermissions(UserPassesTestMixin):
    
    def test_func(self):
        return True if self.request.user.username == 'admin' else False
    
    def handle_no_permission(self):
        return redirect('managementapp:home')

class CheckStaffPermissions(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        return redirect('managementapp:home')

class ManagerList(CheckStaffPermissions, ListView):
    model = User
    paginate_by = 10
    context_object_name = 'object_list'
    template_name = 'administratorapp/managerlist.html'
    
    def get_queryset(self, **kwargs):
        query = self.request.GET.get('search')
        if query == None:
            obj = (
                User.objects
                .filter(groups__name__in = ['manager', 'saler'])
                .select_related('extendinguserfields')
                .order_by('-id')
                )
            return obj
        else:
            obj = (
                User.objects
                .filter(groups__name__in = ['manager', 'saler'])
                .filter(Q(username__icontains = query) | Q(first_name__icontains = query) | Q(last_name__icontains = query) | Q(email__icontains = query) | Q(extendinguserfields__middle_name__icontains = query) | Q(extendinguserfields__department__icontains = query))
                .select_related('extendinguserfields')
                .order_by('-id')
                )
            self.paginate_by = obj.count()
            return obj                

    def post(self, request, *args, **kwargs):
        
        groupe = Group.objects.get(name = 'manager')
        
        if request.POST.get("form_type") == 'add_demo' and request.POST.get('qty') != None:
            
            last_demo_manager = User.objects.filter(username__contains = 'demo-manager').count()

            for i in range(int(request.POST.get('qty'))):

                password = BaseUserManager().make_random_password(length=12, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ0123456789')
                
                last_user, create = User.objects.get_or_create(
                    username = str('demo-manager' + str(last_demo_manager + i + 1)),
                    first_name = 'Демо',
                    last_name = 'Доступ',
                    email = '',
                    is_superuser = False,
                    is_staff = False,
                    is_active = True,
                )
                
                if create:
                    last_user.set_password(password)  
                    last_user.save()

                groupe.user_set.add(last_user)

                extend_user, create = ExtendingUserFields.objects.get_or_create(
                    user = last_user,
                    middle_name = '',
                    department = '',
                    password = password,
                )

                Subscription.objects.create(qty = 3, subtype = 'Тренинг ВОТ', manager = last_user)

            return redirect('administratorapp:managerlist')

        if request.POST.get("form_type") == 'add_manager' and request.POST.get('username') != None and request.POST.get('first_name') != None:

            password = BaseUserManager().make_random_password(length=12, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ0123456789')

            last_user, create = User.objects.get_or_create(
                username = str(request.POST.get('username')),
                first_name = str(request.POST.get('first_name')),
                last_name = '',
                email = request.POST.get('email'),
                is_superuser = False,
                is_staff = False,
                is_active = True,
            )
            
            if create:
                last_user.set_password(password)  
                last_user.save()

            if request.POST.get('saler'):
                groupe, create = Group.objects.get_or_create(name = 'saler')

            groupe.user_set.add(last_user)

            extend_user, create = ExtendingUserFields.objects.get_or_create(
                user = last_user,
                middle_name = '',
                department = str(request.POST.get('first_name')),
                password = password,
            )
            
            return redirect('administratorapp:managerlist')
        
        if request.POST.get("form_type") == 'add_subs' and request.POST.getlist('checkeduser') != []:
            
            if len(request.POST.getlist('checkeduser')) == 1:
                
                checked_user = User.objects.get(pk = request.POST.getlist('checkeduser')[0])
                
                if request.POST.get('trening'):
                    Subscription.objects.create(qty = int(request.POST.get('trening')), subtype = 'Тренинг ВОТ', manager = checked_user)
                            
                return redirect('administratorapp:managerlist')
            
            elif len(request.POST.getlist('checkeduser')) > 1:
                messages.warning(request, 'Выбирите 1 пользователя!')
                return redirect('administratorapp:managerlist')
        
        if request.POST.get("form_type") == 'report':

            start = request.POST.get('start') + ' 00:00:01'
            end = request.POST.get('end') + ' 23:59:59'

            if end >= start:
                
                checked_users = request.POST.getlist('checkeduser')
                check_all = request.POST.getlist('check_all')

                if checked_users:
                    checked_managers = User.objects.filter(pk__in=checked_users)
                    subs = Subscription.objects.filter(
                        manager__in=checked_managers, 
                        date__range=(start, end)
                    ).select_related('user', 'course', 'user__extendinguserfields')
                elif check_all:
                    subs = Subscription.objects.filter(
                        date__range=(start, end)
                    ).select_related('user', 'course', 'user__extendinguserfields')
                else:
                    return HttpResponseBadRequest()
                
                wb = Workbook()
                ws = wb.active
                ws.append(['Логин', 'Организация', 'Подписка', 'Кол-во', 'Пользователь', 'Курс', 'Дата'])
                for sub in subs:
                    ws.append([
                            sub.manager.username, 
                            sub.manager.first_name, 
                            sub.subtype, 
                            sub.qty, 
                            (sub.user.get_full_name() if sub.user is not None else ''), 
                            (sub.course.name if sub.course is not None else ''), 
                            sub.date,
                    ])
                ws.append(['', '', '', ''])
                ws.append([f'Итого списано подписок: {subs.count()}'])
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment;filename="report.xlsx"'
                wb.save(response)

                return response           
             
            return redirect('administratorapp:managerlist')
        
        if request.POST.get("form_type") == 'search_btn' and request.POST.get('search') != []:
            
            return HttpResponseRedirect("?search=%s" % request.POST.get('search'))

        if request.POST.get("form_type") == 'update_attempt':
            
            if LearningQuizAttemptQuestions.objects.filter(learningquizattempt = int(request.POST.get('num')), see_question = False).count() == 0:
                if LearningQuizAttemptQuestions.objects.filter(learningquizattempt = int(request.POST.get('num')), see_question = None).count() == 0:
                    q = LearningQuizAttemptQuestions.objects.filter(learningquizattempt = int(request.POST.get('num')), see_question = True).first()
                    q.see_question = None
                    q.save()
                
                q = LearningQuizAttemptQuestions.objects.filter(learningquizattempt = int(request.POST.get('num')), see_question = None).first()
                q.see_question = False
                q.save()
                
                if LearningQuizAttemptQuestions.objects.filter(learningquizattempt = int(request.POST.get('num')), see_question = None).count() == 0:
                    q = LearningQuizAttemptQuestions.objects.filter(learningquizattempt = int(request.POST.get('num')), see_question = True).first()
                    q.see_question = None
                    q.save()

            return redirect('administratorapp:managerlist')
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

class ActiveUser(CheckStaffPermissions, View):

    def get(self, request, *args, **kwargs):
        
        try:
            active_user = User.objects.get(pk = self.kwargs['user_id'], is_active = True)
            active_user.is_active = False
            active_user.save()

            return redirect('administratorapp:managerlist')
        except:
            active_user = User.objects.get(pk = self.kwargs['user_id'], is_active = False)
            active_user.is_active = True
            active_user.save()

            return redirect('administratorapp:managerlist')
