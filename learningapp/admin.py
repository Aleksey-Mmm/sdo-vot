from django.contrib import admin
from examapp.models import *
from .models import *

class LearningQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'user', 'grade', 'status', 'timestart', 'timefinish')
    list_filter = ['timestart']
    search_fields = ['user__username']

    # def get_questions(self, obj):
    #     return "\n".join([q.externalid for q in obj.question.all()])

class LearningQuizAttemptGradeAdmin(admin.ModelAdmin):
    list_display = ('quiz_attempt', 'question', 'answer', 'weight')
    search_fields = ['quiz_attempt', 'question', 'answer']

class UserRegisteredCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'manager', 'timeregistered', 'timefinish')
    #list_filter = ['course', 'manager']
    search_fields = ['user__username', 'manager__username']

class QuestionСoefficientAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'question', 'sequence_true', 'qty_true_answer', 'sequence_false', 'qty_false_answer', 'coefficient')
    list_filter = ['quiz']
    search_fields = ['user__username']

admin.site.register(LearningQuizAttemptGrade, LearningQuizAttemptGradeAdmin)
admin.site.register(LearningQuizAttempt, LearningQuizAttemptAdmin)
admin.site.register(UserRegisteredCourse, UserRegisteredCourseAdmin)
admin.site.register(QuestionСoefficient, QuestionСoefficientAdmin)