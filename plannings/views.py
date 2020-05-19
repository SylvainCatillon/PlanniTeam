from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from urllib.parse import unquote


from plannings.forms import PlanningCreationForm, EventCreationForm
from plannings.models import GuestEmail, Event


@login_required
def create_planning(request):
    if request.method == 'POST':
        planning_form = PlanningCreationForm(request.POST)
        if planning_form.is_valid():
            # with transaction.atomic()? Pour eviter un planning incomplet... Mais pas forcement grave, comme on peut le modifier...
            planning = planning_form.save()
            if planning.protected:
                guest_emails = request.POST.getlist('guest_email')
                for email in guest_emails:
                    try:
                        planning.guest_emails.add(GuestEmail.objects.get(email=email))
                    except GuestEmail.DoesNotExist:
                        planning.guest_emails.create(email=email)
            events = request.POST.getlist('event')
            for event_string in events:
                event_args = {'planning': planning}
                for arg in event_string.split('&'):
                    key, value = arg.split('=')
                    if value:
                        event_args[key] = unquote(value)
                Event.objects.create(**event_args)
            return HttpResponseRedirect(reverse(
                'plannings:created', kwargs={'planning_ekey': planning.ekey}))
    else:
        planning_form = PlanningCreationForm(initial={'creator': request.user.pk})
    event_form = EventCreationForm()
    context = {'planning_form': planning_form, 'event_form': event_form}
    return render(request, 'plannings/create_planning.html', context)


def planning_created(request, planning_ekey): # Remplacer par TemplateView en créant link dans create??
    link = request.build_absolute_uri(reverse(
        'plannings:display', args=(planning_ekey,)))  # security hole? Remplacer par link = get_current_site(request) ou gestion desite framework: https://docs.djangoproject.com/en/3.0/ref/contrib/sites/#getting-the-current-domain-for-full-urls
    return render(request, 'plannings/created.html', {'link': link})


def display_planning(request, planning_ekey):
    pass
