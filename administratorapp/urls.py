from django.urls import path
from . import views
from administratorapp.views import *
from django.contrib.auth.decorators import login_required

app_name = 'administratorapp'
urlpatterns = [
    path('managerlist', login_required(ManagerList.as_view()), name='managerlist'),
    path('managerlist/<int:user_id>/activeuser', login_required(ActiveUser.as_view()), name='activeuser'),
]
