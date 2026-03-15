from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from .forms import RegisterForm
from django.urls import reverse_lazy

class UserLoginView(LoginView):
    template_name = "registration/login.html"

    
class UserLogoutView(LogoutView):
    pass


class UserRegisterView(CreateView):
    
    form_class = RegisterForm
    
    template_name = "registration/register.html"
    
    success_url = reverse_lazy("login")