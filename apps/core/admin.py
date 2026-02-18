from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'cedula', 'cargo', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'cedula')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('cedula', 'cargo', 'departamento')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('cedula', 'cargo', 'departamento')}),
    )
