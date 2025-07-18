from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import DogProfile, EmailVerification

User = get_user_model()

# Inline for displaying DogProfile inside User admin page
class DogProfileInline(admin.StackedInline):
    model = DogProfile
    can_delete = False
    verbose_name_plural = 'Dog Profile'
    fk_name = 'owner'

# Custom User Admin
class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'is_verified', 'is_active', 'is_staff', 'role')
    list_filter = ('is_verified', 'role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Verification', {'fields': ('is_verified',)}),
        ('Groups & Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    readonly_fields = ('is_verified',)
    search_fields = ('email',)
    ordering = ('email',)
    inlines = [DogProfileInline]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_superuser')}
        ),
    )

# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(DogProfile)
admin.site.register(EmailVerification)
