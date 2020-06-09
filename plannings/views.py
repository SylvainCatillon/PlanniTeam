from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from notifications.Notifier import Notifier
from plannings.forms import PlanningCreationForm, EventCreationForm, \
    EventInlineFormSet
from plannings.models import Planning
from plannings.utils import update_guests, add_guests


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
            planning = planning_form.save()

            event_formset = EventInlineFormSet(request.POST, instance=planning)
            if event_formset.is_valid():
                event_formset.save()

            if planning.protected:
                guest_emails = request.POST.getlist('guest_email')
                add_guests(planning, guest_emails)

            return redirect('plannings:created', planning.ekey)
    else:
        planning_form = PlanningCreationForm(
            initial={'creator': request.user.pk})
    event_formset = EventInlineFormSet()
    context = {'planning_form': planning_form,
               'event_formset': event_formset,
               'form_url': reverse('plannings:create')}
    return render(request, 'plannings/create_planning.html', context)


@require_POST
def check_event(request):
    """
    Checks if the event form is valid.
    If it's valid, returns a Http Response with code 200.
    If it's not, returns the form errors as Json, and the Http code 422.
    Accept only POST request.
    """
    form = EventCreationForm(request.POST)
    if form.is_valid():
        return HttpResponse("Les informations sont valides")
    else:
        return HttpResponse(form.errors.as_json(), status=422)


def planning_created(request, planning_ekey):
    """After a planning was created, displays a page with the access link
    of the planning."""
    planning = Planning.objects.get_by_ekey(planning_ekey)
    link = request.build_absolute_uri(planning.get_absolute_url())
    context = {'link': link, 'planning': planning}
    return render(request, 'plannings/planning_created.html', context)


@login_required
def edit_planning(request, planning_ekey):
    """
    GET method:
        Displays the planning edition page
    POST method:
        -Gather the data of the planning form.
        -Test if the planning's form is valid.
        -Update the planning in the database
        -If the planning is protected, update the guests emails in the planning
        -Update the events in the planning
        -Redirects to the planning's display.
    """
    planning = Planning.objects.get_by_ekey_or_404(planning_ekey)
    if request.user != planning.creator:
        redirect_url = f"{reverse('accounts:login')}?next={request.path}"
        return HttpResponseRedirect(redirect_url)

    if request.method == 'POST':
        planning_form = PlanningCreationForm(request.POST, instance=planning)
        if planning_form.is_valid():
            planning_form.save()
            if planning.protected:
                new_emails = request.POST.getlist('guest_email')
                update_guests(planning, new_emails)

            event_formset = EventInlineFormSet(request.POST, instance=planning)
            if event_formset.is_valid():
                event_formset.save()
                notifier = Notifier(planning)
                notifier.notify_events_changes(event_formset)

            return redirect('participations:view', planning.ekey)

    planning_form = PlanningCreationForm(instance=planning)
    event_formset = EventInlineFormSet(instance=planning)
    return render(request,
                  'plannings/create_planning.html',
                  {'event_formset': event_formset,
                   'planning_form': planning_form,
                   'form_url': request.path})
