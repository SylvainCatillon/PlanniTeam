import json

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse, Http404, \
    JsonResponse
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
            # import pdb;pdb.set_trace()
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
            for event in events:
                planning.event_set.create(**json.loads(event))
            # for event_string in events:
            #     event_args = {'planning': planning}
            #     for arg in event_string.split('&'):
            #         key, value = arg.split('=')
            #         if value:
            #             event_args[key] = unquote(value)
            #     Event.objects.create(**event_args)
            return HttpResponseRedirect(reverse(
                'plannings:created', kwargs={'planning_ekey': planning.ekey}))
    else:
        planning_form = PlanningCreationForm(initial={'creator': request.user.pk})
    event_form = EventCreationForm()
    context = {'planning_form': planning_form, 'event_form': event_form}
    return render(request, 'plannings/create_planning.html', context)


def check_event(request):
    if request.method == 'POST': # is POST the good method?
        form = EventCreationForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            if event: # verification inutile, suite à form.is_valid?
                return JsonResponse(model_to_dict(event))
        else:
            return JsonResponse(form.errors, status=422)  # Change Http error code. 422 ou 400?
    raise Http404('No Get on this page')  # Change error message


def planning_created(request, planning_ekey): # Remplacer par TemplateView en créant link dans create??
    link = request.build_absolute_uri(reverse(
        'plannings:display', args=(planning_ekey,)))  # security hole? Remplacer par link = get_current_site(request) ou gestion desite framework: https://docs.djangoproject.com/en/3.0/ref/contrib/sites/#getting-the-current-domain-for-full-urls
    return render(request, 'plannings/created.html', {'link': link})


def display_planning(request, planning_ekey):
    pass

"""
if form.is_valid():
    event = form.save(commit=False)
    data = serializers.serialize('json', [event])
    return data in contexte to js
    
for e in serializers.deserialize('json', data):
    e.save()
"""
