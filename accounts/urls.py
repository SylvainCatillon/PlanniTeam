from django.urls import path, include
from django.contrib.auth.views import LoginView

from accounts.views import CreateView

app_name = "accounts"
urlpatterns = [
    #path("", include('django.contrib.auth.urls')),
    path(
        'login/',
        LoginView.as_view(template_name='accounts/login.html'),
        name='login'),
    path(
        'create/',
        CreateView.as_view(),
        name='create',
    )
]