from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.models import User
from participations.models import Participation
from plannings.models import Planning


@login_required
def view_planning(request, planning_ekey): # si pas default. num 1
    planning = Planning.objects.get_by_ekey(planning_ekey)
    other_participants = []
    for user in User.objects.filter(event__planning__pk=planning.pk)\
                            .distinct()\
                            .order_by('first_name'):
        if user != request.user:
            other_participants.append(user)
    events = {}
    #  TODO: Voir prefetch_related pour optimisation
    for event in planning.event_set.all():
        vls = []
        for user in other_participants:
            try:
                part = event.participation_set.get(participant=user)
                vls.append(part)
            except Participation.DoesNotExist:
                vls.append(None)
            events[event] = vls
    context = {'planning': planning,
               'other_participants': other_participants,
               'events': events}
    return render(request,
                  'participations/view_planning.html', context)


# TODO: Voir si une réponses 'NA' par défault dans Participation,
#  et une vue de ce genre seraient plus opti
# @login_required
# def view_planning(request, planning_ekey): # si answer default num 1
#     planning = Planning.objects.get_by_ekey(planning_ekey)
#     other_participants = []
#     # for user in User.objects.filter(event__planning__pk=planning.pk)\
#     #                         .distinct()\
#     #                         .order_by('first_name'):
#     #     if user != request.user:
#     #         other_participants.append(user)
#     context = {'planning': planning, 'other_participants': other_participants}
#     return render(request,
#                   'participations/view_planning.html', context)
