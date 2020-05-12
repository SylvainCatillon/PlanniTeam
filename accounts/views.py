from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView

from accounts.forms import CustomUserCreationForm


class CreateView(FormView):
    template_name = 'accounts/create.html'
    form_class = CustomUserCreationForm
    success_url = '/accounts/login/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.save()
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, email=email, password=password)
        if user:
            login(self.request, user)
        return super().form_valid(form)
