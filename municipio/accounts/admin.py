from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("dni", "first_name", "last_name", "email", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")

    ordering = ("dni",)
    search_fields = ("dni", "first_name", "last_name", "email")

    fieldsets = (
        (None, {"fields": ("dni", "password")}),
        ("Datos personales", {"fields": ("first_name", "last_name", "email")}),
        ("Rol de Usuario", {"fields": ("role",)}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("dni", "first_name", "last_name", "email", "role", "password1", "password2"),
        }),
    )


admin.site.register(User, CustomUserAdmin)