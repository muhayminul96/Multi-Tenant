from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # you can customize how it looks in the admin too if you want
    list_display = ('id', 'email', 'is_active', 'is_staff', 'created_at')
    ordering = ('-created_at',)
