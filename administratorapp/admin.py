from django.contrib import admin
from django.contrib.auth.models import User


admin.site.unregister(User)

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'get_middle_name', 'get_department', 'get_password','email', 'get_groups')
    search_fields = ['username']
    list_filter = ['is_active']

    def get_groups(self, obj):
        return ",\n".join([g.name for g in obj.groups.all()])
    
    def get_middle_name(self, obj):
        return obj.extendinguserfields.middle_name
    def get_department(self, obj):
        return obj.extendinguserfields.department
    def get_password(self, obj):
        return obj.extendinguserfields.password

admin.site.register(User, UserAdmin)
