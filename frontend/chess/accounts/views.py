

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from .forms import SignUpForm

def index(request):
    return render(request, 'registration/index.html')

def logout(request):
    return render(request, 'registration/logout.html')

class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
