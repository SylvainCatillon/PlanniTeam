from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from accounts import views
from accounts.views import CreateView

app_name = "accounts"
urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name='accounts/login.html'),
        name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('create/', CreateView.as_view(), name='create'),
    path('profile/', views.profile, name='profile')
]
