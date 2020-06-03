import json

from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.http import HttpResponseRedirect, Http404, JsonResponse, \
    HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST


from plannings.forms import PlanningCreationForm, EventCreationForm, \
    EventInlineFormSet
from plannings.models import GuestEmail, Planning
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
            # TODO: with transaction.atomic(),
            #  pour éviter un planning incomplet?
            #  Ou planning_form.save(commit=false)?
            #  Mais pas forcement grave, comme on peut le modifier...
            planning = planning_form.save()

            event_formset = EventInlineFormSet(request.POST, instance=planning)
            if event_formset.is_valid():
                # TODO: ne pas sauver planning si events invalides?
                #  Renvoyer errors?
                event_formset.save()

            if planning.protected:
                guest_emails = request.POST.getlist('guest_email')
                add_guests(planning, guest_emails)

            # TODO: remplacer par shortcut redirect()
            return HttpResponseRedirect(reverse(
                'plannings:created', kwargs={'planning_ekey': planning.ekey}))
    else:
        planning_form = PlanningCreationForm(initial={'creator': request.user.pk})
    event_formset = EventInlineFormSet()
    context = {'planning_form': planning_form,
               'event_formset': event_formset,
               'form_url': reverse('plannings:create')}
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
        return HttpResponse("Les informations sont valides")
    else:
        return HttpResponse(form.errors.as_json(), status=422)


def planning_created(request, planning_ekey): # TODO: Remplacer par TemplateView en créant link dans create??
    """After a planning was created, displays a page with the access link
    of the planning."""
    planning = Planning.objects.get_by_ekey(planning_ekey)
    link = request.build_absolute_uri(planning.get_absolute_url())  # TODO: security hole? Remplacer par link = get_current_site(request) ou gestion desite framework: https://docs.djangoproject.com/en/3.0/ref/contrib/sites/#getting-the-current-domain-for-full-urls
    return render(request, 'plannings/created.html', {'link': link})


@login_required
def edit_planning(request, planning_ekey):
    planning = Planning.objects.get_by_ekey(planning_ekey) # TODO or 404?
    self_url = reverse('plannings:edit', # TODO method django?
                       kwargs={'planning_ekey': planning_ekey})
    if request.user != planning.creator:
        redirect_url = f"{reverse('accounts:login')}?next={self_url}"
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
                # TODO: ne pas sauver planning si events invalides?
                #  Renvoyer errors?
                event_formset.save()

            # TODO: remplacer par shortcut redirect(). Changer redirect
            return HttpResponseRedirect(reverse(
                'plannings:created', kwargs={'planning_ekey': planning.ekey}))

    planning_form = PlanningCreationForm(instance=planning)
    event_formset = EventInlineFormSet(instance=planning)
    return render(request,
                  'plannings/create_planning.html',
                  {'event_formset': event_formset,
                   'planning_form': planning_form,
                   'form_url': self_url})
