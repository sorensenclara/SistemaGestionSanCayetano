from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("dni", "first_name", "last_name", "email", "role")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

class DniAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="DNI",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingresá tu DNI",
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingresá tu contraseña",
                "autocomplete": "current-password",
            }
        ),
    )