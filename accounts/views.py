from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic.edit import FormView

from accounts.forms import CustomUserCreationForm


class CreateView(FormView):
    """Class-based view letting a user create an account.
    Inherit of the generic Django view 'FormView'."""
    template_name = 'accounts/create.html'
    form_class = CustomUserCreationForm
    success_url = '/accounts/profile/'

    def form_valid(self, form):
        """Override of the parent method,
        to create a user and log it in when the form is valid"""
        form.save()
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, email=email, password=password)
        if user:
            login(self.request, user)
        return super().form_valid(form)


@login_required
def profile(request):
    """View of the profile page.
    Redirects to 'login' if the user isn't logged.
    Create a list of all the plannings to which the user participated,
    to display them in the profile page."""
    user = request.user
    participated = [event.planning for event in
                    user.event_set.order_by('planning').distinct('planning')]
    return render(request, "accounts/profile.html",
                  {'participated': participated})
