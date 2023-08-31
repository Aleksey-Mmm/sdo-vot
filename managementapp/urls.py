from django.urls import path
from . import views
from managementapp.views import *
from django.contrib.auth.decorators import login_required

app_name = 'managementapp'
urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('about', views.About, name='about'),
    path('login', LogInView.as_view(), name='login'),
    path('support', Support.as_view(), name='support'),
    path('supportcards', login_required(SupportCards.as_view()), name='supportcards'),
    path('logout', login_required(views.logout_user), name='logout'),
    path('registration', login_required(UsersRegistration.as_view()), name='registration'),
    path('edituser/<int:user_id>', login_required(EditUser.as_view()), name='edituser'),
    path('users', login_required(UsersList.as_view()), name='users'),
    path('managers', login_required(ManagersList.as_view()), name='managers'),
    path('usercourses/<int:user_id>/activeuser', login_required(ActiveUser.as_view()), name='activeuser'),
    path('usercourses/<int:user_id>', login_required(UserCourses.as_view()), name='usercourses'),
    path('usercourses/<int:user_id>/bestreport/<int:course_id>', login_required(BestReport.as_view()), name='bestreport'),
    path('usercourses/<int:user_id>/activecourse/<int:course_id>', login_required(ActiveCourse.as_view()), name='activecourse'),
    path('usercourses/<int:user_id>/deletecourse/<int:course_id>', login_required(DeleteCourse.as_view()), name='deletecourse'),
    path('usercourses/<int:user_id>/activecourse/<int:course_id>/statistics', login_required(CourseStatistics.as_view()), name='statistics'),
    path('addnewuser', login_required(UsersList.as_view()), name='addnewuser'),
    path('usercourse/<int:user_id>/addcourse', login_required(AddCourse.as_view()), name='addcourse'),
]
