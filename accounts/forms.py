from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from django.forms import EmailField


class CustomUserCreationForm(UserCreationForm):
    email = EmailField()

    class Meta:
        model = User
        fields = ('username', 'email',)
