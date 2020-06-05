from django.contrib.auth.forms import UserCreationForm

from accounts.models import User


class CustomUserCreationForm(UserCreationForm):
    """Form for the user creation"""

    class Meta:
        model = User
        fields = ('email', 'first_name')
