from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import ModifiedAuthenticationForm

class MyLoginView(LoginView):
    """Modifies original loginview with custom authenticationform and redirection behaviour"""
    form_class = ModifiedAuthenticationForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        next_url = self.request.POST.get('next') or self.request.GET.get('next')

        if next_url:
            return next_url
        if user.role == "admin":
            return "/admin/"
        if user.role == "hr":
            return reverse_lazy("portal:hr")
        return reverse_lazy("portal:employee")