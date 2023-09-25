from django.contrib import admin
from .models import *
from django.contrib import messages
from django.utils.translation import ngettext


class QuizBankSettingsInline(admin.TabularInline):
    model = QuizBankSettings
    extra = 1

class AnswersInline(admin.TabularInline):
    model = Answer
    extra = 1

class CourseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tags')
    search_fields = ['name']
    prepopulated_fields = {"slug": ("name", )}

    def get_tags(self, obj):
        return "\n".join([t.name for t in obj.tag.all()])

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_type', 'parent', 'bank_training', 'get_tags')
    search_fields = ['name', 'course_type']
    prepopulated_fields = {"slug": ("name", )}

    def get_tags(self, obj):
        return "\n".join([t.name for t in obj.tag.all()])

class QuestionsBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_course', 'parent', 'get_tags')
    search_fields = ['name', 'get_course']
    inlines = (QuizBankSettingsInline,)

    def get_course(self, obj):
        return "\n".join([c.name for c in obj.course.all()])

    def get_tags(self, obj):
        return "\n".join([t.name for t in obj.tag.all()])

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    list_filter = ['status']
    search_fields = ['name']
    list_per_page = 500

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('externalid', 'text', 'get_questions_bank', 'question_type', 'status', 'get_tags')
    list_filter = ['questions_bank', 'tag', 'status']
    search_fields = ['externalid', 'text']
    list_per_page = 20
    actions = ['q_off', 'q_on', 'qwqwqw']
    inlines = (AnswersInline,)

    @admin.action(description='qwqwqw')
    def qwqwqw(self, request, queryset):
        updated = queryset.update(status = 2)
        # for q in queryset:
        #     Answer.objects.filter(question = q).update(status = 4)
        self.message_user(request, ngettext(
                '%d вопрос qwqwqw.',
                '%d вопросов qwqwqw.',
                updated,
            ) % updated, messages.SUCCESS)

    @admin.action(description='отключить')
    def q_off(self, request, queryset):
        updated = queryset.update(status = 4)
        for q in queryset:
            Answer.objects.filter(question = q).update(status = 4)
        self.message_user(request, ngettext(
                '%d вопрос отключен.',
                '%d вопросов отключено.',
                updated,
            ) % updated, messages.SUCCESS)

    @admin.action(description='вкл')
    def q_on(self, request, queryset):
        updated = queryset.update(status = 1)
        for q in queryset:
            Answer.objects.filter(question = q).update(status = 1)
        self.message_user(request, ngettext(
                '%d вопрос включен.',
                '%d вопросов включено.',
                updated,
            ) % updated, messages.SUCCESS)

    def get_questions_bank(self, obj):
        return "\n".join([q.name for q in obj.questions_bank.all()])
    
    def get_tags(self, obj):
        return "\n".join([t.name for t in obj.tag.all()])

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('externalid', 'text', 'img', 'weight', 'question', 'status', 'create', 'get_tags')
    list_filter = ['status']
    search_fields = ['text']

    def get_tags(self, obj):
        return "\n".join([t.name for t in obj.tag.all()])

class tagAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    search_fields = ['name', 'type']

class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'get_questions_bank', 'max_grade', 'feedback', 'timelimit', 'status', 'get_tags')
    list_filter = ['course']
    search_fields = ['name', 'status']
    prepopulated_fields = {"slug": ("name", )}
    inlines = (QuizBankSettingsInline,)

    def get_questions_bank(self, obj):
        return "\n".join([q.name for q in obj.bank.all()])
    
    def get_tags(self, obj):
        return "\n".join([t.name for t in obj.tag.all()])

class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'user', 'grade', 'status', 'timestart', 'timefinish')
    list_filter = ['timestart']
    search_fields = ['status', 'user', 'quiz']

    def get_questions(self, obj):
        return "\n".join([q.externalid for q in obj.question.all()])

class QuizAttemptGradeAdmin(admin.ModelAdmin):
    list_display = ('quiz_attempt', 'question', 'answer', 'weight')
    search_fields = ['quiz_attempt', 'question', 'answer']

class UserRegisteredQuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'timeregistered')
    list_filter = ['quiz']
    search_fields = ['user', 'quiz']

class ExtendingUserFieldsAdmin(admin.ModelAdmin):
    list_display = ('user', 'middle_name', 'department', 'password')
    list_filter = ['department']
    search_fields = ['user__username']

class UploadAdmin(admin.ModelAdmin):
    list_display = ('description', 'document', 'upload_time', 'course', 'status')
    list_filter = ['course', 'status']
    search_fields = ['description']
    actions = ['q_off', 'q_on']
    
    @admin.action(description='отключить')
    def q_off(self, request, queryset):
        updated = queryset.update(status = 4)
        self.message_user(request, ngettext(
                '%d вопрос отключен.',
                '%d вопросов отключено.',
                updated,
            ) % updated, messages.SUCCESS)

    @admin.action(description='вкл')
    def q_on(self, request, queryset):
        updated = queryset.update(status = 1)
        self.message_user(request, ngettext(
                '%d вопрос включен.',
                '%d вопросов включено.',
                updated,
            ) % updated, messages.SUCCESS)

admin.site.register(ExtendingUserFields, ExtendingUserFieldsAdmin)
admin.site.register(CourseType, CourseTypeAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(QuestionsBank, QuestionsBankAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Tag, tagAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(QuizAttemptGrade, QuizAttemptGradeAdmin)
admin.site.register(Status)
admin.site.register(Upload, UploadAdmin)
admin.site.register(QuestionType)
admin.site.register(QuizBankSettings)
admin.site.register(UserRegisteredQuiz, UserRegisteredQuizAdmin)
