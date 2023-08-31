from django.db import models
from django.db.models.deletion import CASCADE, PROTECT
from django.contrib.auth.models import *
from django.db.models.fields import CharField
import datetime
from django.utils import timezone

class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')	
    type = models.CharField(max_length=100, blank=True, verbose_name='Тип')

    class Meta:
        verbose_name = 'Таг'
        verbose_name_plural = 'Таги'

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')	

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name

class CourseType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    slug = models.SlugField(max_length=255, db_index=True, unique=True, verbose_name='URL')
    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = 'Область'
        verbose_name_plural = 'Области'

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    full_name = models.CharField(max_length=250, blank=True, null=True, verbose_name='Полное имя')
    course_type = models.ForeignKey(CourseType, on_delete=PROTECT, blank=True, verbose_name='Область')
    parent = models.ForeignKey('self', on_delete=CASCADE, blank=True, null=True, verbose_name='Родитель')
    slug = models.SlugField(max_length=255, db_index=True, unique=True, verbose_name='URL')
    bank_training = models.BooleanField(blank=True, null=True, verbose_name='Обучение по банкам')
    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.name

class QuestionsBank(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    course = models.ManyToManyField(Course)
    parent = models.ForeignKey('self', on_delete=CASCADE, blank=True, null=True, verbose_name='Родитель')
    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = 'Банк'
        verbose_name_plural = 'Банки'

    def __str__(self):
        return self.name

class Document(models.Model):
    name = models.TextField(verbose_name='Имя')
    status = models.ForeignKey(Status, on_delete=PROTECT, verbose_name='Статус')
    create = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    update = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    create_by = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT, verbose_name='Создатель')
    update_by = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT, verbose_name='Редактор')
    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return self.name

class QuestionType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')

    class Meta:
        verbose_name = 'Тип вопроса'
        verbose_name_plural = 'Типы вопросов'

    def __str__(self):
        return self.name

class Question(models.Model):
    text = models.TextField(verbose_name='Текст вопроса')
    img = models.ImageField(blank=True, null=True)
    questions_bank = models.ManyToManyField(QuestionsBank)
    question_type = models.ForeignKey(QuestionType, on_delete=PROTECT, verbose_name='Тип вопроса')
    explanation = models.TextField(blank=True, null=True, verbose_name='Объяснение')
    document = models.ForeignKey(Document, on_delete=PROTECT, blank=True, null=True, verbose_name='Документ')
    externalid = models.IntegerField(verbose_name='Номер вопроса')
    status = models.ForeignKey(Status, on_delete=PROTECT, verbose_name='Статус')
    create = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    update = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    create_by = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT, verbose_name='Создатель')
    update_by = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT, verbose_name='Редактор')
    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return str(self.id)   

    def question_answers(self):
        return self.answer_set.all().values('id', 'text', 'weight')
    
class Answer(models.Model):
    text = models.TextField(verbose_name='Текст ответа')
    img = models.ImageField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='Вес ответа')
    externalid = models.IntegerField(verbose_name='Номер ответа')
    question = models.ForeignKey(Question, on_delete=CASCADE, verbose_name='Вопрос')
    status = models.ForeignKey(Status, on_delete=PROTECT, verbose_name='Статус')
    create = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    update = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    create_by = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT, verbose_name='Создатель')
    update_by = models.ForeignKey(User, related_name='+', on_delete=models.PROTECT, verbose_name='Редактор')
    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return str(self.externalid)

class Upload(models.Model):
    description = models.TextField(blank=True)
    document = models.FileField(upload_to='import/%Y.%m.%d/')
    upload_time = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, blank=True, null=True, on_delete=CASCADE,verbose_name='Курс')
    status = models.ForeignKey(Status, blank=True, null=True, on_delete=PROTECT, verbose_name='Статус')

    class Meta:
        verbose_name = 'Загрузка'
        verbose_name_plural = 'Загрузки'

    def __str__(self):
        return self.description

class Quiz(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя')
    course = models.ForeignKey(Course, on_delete=PROTECT, blank=True, null=True, verbose_name='Курс')
    bank = models.ManyToManyField(QuestionsBank, through='QuizBankSettings', through_fields=('quiz', 'bank'))
    max_grade = models.IntegerField(verbose_name='Макс оценка')
    feedback = models.BooleanField(verbose_name='Проверка ответа')
    timelimit = models.IntegerField(verbose_name='Ограничение времени')
    status = models.ForeignKey(Status, on_delete=PROTECT, verbose_name='Статус')
    slug = models.SlugField(max_length=255, db_index=True, unique=True, verbose_name='URL')
    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return self.name

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=PROTECT, verbose_name='Тест')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Ученик')
    questions = models.ManyToManyField(Question)
    grade = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='Оценка')
    status = models.ForeignKey(Status, on_delete=PROTECT, verbose_name='Статус')
    timestart = models.DateTimeField(auto_now_add=True, verbose_name='Начало теста')
    timefinish = models.DateTimeField(blank=True, null=True, verbose_name='Конец теста')

    class Meta:
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'

class QuizAttemptGrade(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=PROTECT, verbose_name='Попытка')
    question = models.ForeignKey(Question, on_delete=PROTECT, verbose_name='Вопрос')
    answer = models.ForeignKey(Answer, on_delete=PROTECT, verbose_name='Ответ')
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name='Вес ответа')
    status = models.CharField(max_length=255, blank=True, verbose_name='Статус ответа')

    class Meta:
        verbose_name = 'Детализация попытки теста'
        verbose_name_plural = 'Детализация попыток тестов'  

class QuizBankSettings(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=CASCADE, verbose_name='Тест')
    bank = models.ForeignKey(QuestionsBank, on_delete=CASCADE, verbose_name='Банк')
    qty = models.IntegerField(blank=True, verbose_name='Кол-во вопросов')
    tag = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = 'Настройка банка теста'
        verbose_name_plural = 'Настройки банков тестов' 

class ExtendingUserFields(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    password = models.CharField(max_length=100, blank=True, null=True, verbose_name='Пароль')

class UserRegisteredQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Ученик')
    quiz = models.ForeignKey(Quiz, on_delete=CASCADE, verbose_name='Тест')
    timeregistered = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Зарегистророван на курс пользователя'
        verbose_name_plural = 'Зарегистророваны на курсы пользователей'

class HelpDeskCards(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Ученик')
    card = models.BigIntegerField(verbose_name='ID Карточки')
    status = models.ForeignKey(Status, blank=True, null=True, on_delete=PROTECT, verbose_name='Статус')
    update = models.TextField(blank=True, null=True, verbose_name='Обновлен')

    def __str__(self):
        return str(self.id)
        
    class Meta:
        verbose_name = 'Карточка Тех Поддержки'
        verbose_name_plural = 'Карточки Тех Поддержки'