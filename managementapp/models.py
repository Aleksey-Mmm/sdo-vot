from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from django.contrib.auth.models import User
from django.db.models.fields import CharField
import datetime
from django.utils import timezone
from examapp.models import *

class Subscription(models.Model):
    manager = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT, verbose_name='Менеджер')
    user = models.ForeignKey(User, related_name='+', blank=True,  null=True, on_delete=models.PROTECT, verbose_name='Пользователь')
    course = models.ForeignKey(Course, blank=True,  null=True, on_delete=PROTECT, verbose_name='Курс')
    qty = models.IntegerField(default=0, verbose_name='Кол-во подписок')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    subtype = models.CharField(max_length=255, verbose_name='Тип подписки')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
