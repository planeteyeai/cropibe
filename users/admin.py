from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Role

User = get_user_model()

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display  = ('name', 'display_name')
    search_fields = ('name', 'display_name')

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 'last_name', 'email', 'phone_number',
            'address', 'village', 'state', 'district', 'taluka',
            'profile_picture'
        )}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'role',
                'password1', 'password2',
                'is_active', 'is_staff', 'is_superuser'
            ),
        }),
    )
    list_display    = (
        'username', 'email', 'role',
        'is_active', 'is_staff', 'is_superuser', 'date_joined'
    )
    list_filter     = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields   = ('username', 'email')
    ordering        = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
