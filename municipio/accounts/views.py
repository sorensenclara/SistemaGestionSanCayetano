from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import DniAuthenticationForm
from django.shortcuts import render


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = DniAuthenticationForm

    def get_success_url(self):
        return reverse_lazy("dashboard")

    def form_valid(self, form):
        # Si el checkbox "remember" está marcado, la sesión dura 30 días.
        # Si no, expira al cerrar el navegador.
        remember = self.request.POST.get("remember")
        if remember:
            self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 días
        else:
            self.request.session.set_expiry(0)  # expira al cerrar el navegador
        return super().form_valid(form)


def acceso_inicial(request):
    return render(request, "acceso_inicial.html")