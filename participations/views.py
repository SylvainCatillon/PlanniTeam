from json import loads

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.http import require_POST

from accounts.models import User
from participations.models import Participation
from participations.utils import prepare_events
from plannings.models import Planning, Event


@require_POST
def participate(request):
    """Update the participations of a user. Takes only POST requests."""
    if not request.user.is_authenticated:
        return HttpResponse('Veuillez vous connecter', status=401)
    for json_part in request.POST.getlist('participation'):
        participation = loads(json_part)
        answer = participation.get('answer')
        if answer:
            event = Event.objects.get(pk=participation['event'])
            planning = event.planning
            if not planning.user_has_access(request.user):
                return HttpResponseForbidden()
            Participation.objects.update_or_create(
                participant=request.user, event=event,
                defaults={'answer': answer}
            )
    return HttpResponse('Votre participation est enregistrée')


@login_required
def view_planning(request, planning_ekey):
    """View to display a planning."""
    planning = Planning.objects.get_by_ekey_or_404(planning_ekey)
    if not planning.user_has_access(request.user):
        return render(request, 'participations/protected_planning.html')

    # Get a list of all the planning's participants, except the current user
    other_participants = []
    for user in User.objects.filter(event__planning__pk=planning.pk)\
                            .distinct()\
                            .order_by('first_name'):
        if user != request.user:
            other_participants.append(user)

    # Gather all the planning's events, and prepare them to be displayed
    events = prepare_events(list(planning.event_set.all()),
                            request.user, other_participants)

    context = {'planning': planning,
               'other_participants': other_participants,
               'events': events,
               'answer_choices': Participation.answer_choices}
    return render(request,
                  'participations/view_planning.html', context)
