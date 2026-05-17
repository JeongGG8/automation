from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, Menu, RoleMenu


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('role', 'name')}),
    )
    list_display = ('username', 'name', 'role', 'is_active')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_name')


@admin.register(RoleMenu)
class RoleMenuAdmin(admin.ModelAdmin):
    list_display = ('role', 'menu')
