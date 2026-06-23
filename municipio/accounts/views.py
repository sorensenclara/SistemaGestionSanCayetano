from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import DniAuthenticationForm
from django.shortcuts import render


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = DniAuthenticationForm

    def get_success_url(self):
        return reverse_lazy("dashboard")


def acceso_inicial(request):
    return render(request, "acceso_inicial.html")