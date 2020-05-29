import json

from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST


from plannings.forms import PlanningCreationForm, EventCreationForm
from plannings.models import GuestEmail, Planning


@login_required
def create_planning(request):
    """
    GET method:
        Displays the planning creation page, with empty forms
    POST method:
        -Gather the data of the planning form.
        -Test if the planning is valid.
        -Save the planning in the database
        -If the planning is protected, save the guests emails in the planning
        -Save the events in the planning
        -Redirects to planning:created with the hashed id of the planning.
    """
    if request.method == 'POST':
        planning_form = PlanningCreationForm(request.POST)
        if planning_form.is_valid():
            # TODO: with transaction.atomic(),
            #  pour eviter un planning incomplet?
            #  Mais pas forcement grave, comme on peut le modifier...
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
                event_args = {key: value for key, value in json.loads(event).items() if value}
                planning.event_set.create(**event_args)

            # TODO: remplacer par shortcut redirect()
            return HttpResponseRedirect(reverse(
                'plannings:created', kwargs={'planning_ekey': planning.ekey}))
    else:
        planning_form = PlanningCreationForm(initial={'creator': request.user.pk})
    event_form = EventCreationForm()
    context = {'planning_form': planning_form, 'event_form': event_form}
    return render(request, 'plannings/create_planning.html', context)


# TODO: Is post the good method? Put?
#  Si changement, require_Post ==> require_http_methods
@require_POST
def check_event(request):
    """
    Checks if the event form is valid.
    If it's valid, returns the event data as Json.
    If it's not, returns the form errors as Json, and the Http code 422.
    Accept only POST request.
    """
    form = EventCreationForm(request.POST)
    if form.is_valid():
        event = form.save(commit=False)
        if event:  # TODO: verification inutile, suite à form.is_valid?
            return JsonResponse(model_to_dict(event))
    else:
        return JsonResponse(form.errors, status=422)
        # TODO: Change Http error code. 422 ou 400?


def planning_created(request, planning_ekey): # TODO: Remplacer par TemplateView en créant link dans create??
    """After a planning was created, displays a page with the access link
    of the planning."""
    planning = Planning.objects.get_by_ekey(planning_ekey)
    link = request.build_absolute_uri(planning.get_absolute_url())  # TODO: security hole? Remplacer par link = get_current_site(request) ou gestion desite framework: https://docs.djangoproject.com/en/3.0/ref/contrib/sites/#getting-the-current-domain-for-full-urls
    return render(request, 'plannings/created.html', {'link': link})


def edit_planning(request, planning_ekey):
    planning = Planning.objects.get_by_ekey(planning_ekey)
    from django.forms import inlineformset_factory
    from plannings.models import Event
    EventInlineFormSet = inlineformset_factory(Planning, Event,
                                               form=EventCreationForm, extra=1)

    if request.method == 'POST':
        planning_form = PlanningCreationForm(request.POST, instance=planning)
        if planning_form.is_valid():
            planning_form.save()
            event_formset = EventInlineFormSet(request.POST, instance=planning)
            if event_formset.is_valid():
                event_formset.save()

    planning_form = PlanningCreationForm(instance=planning)
    event_formset = EventInlineFormSet(instance=planning)
    return render(request, 'test.html', {'event_formset': event_formset,
                                         'planning_form': planning_form,
                                         'planning': planning})
