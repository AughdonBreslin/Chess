
from django.contrib.auth import views as auth_views
from django.urls import path, include

from .views import SignUpView, index, logout

urlpatterns = [
    path('', index, name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('', include('django.contrib.auth.urls')),

]