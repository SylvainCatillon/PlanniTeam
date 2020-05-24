from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from collections import defaultdict

from accounts.models import User
from participations.models import Participation
from plannings.models import Planning


@login_required
def view_planning(request, planning_ekey): # si pas default. num 1
    # TODO: gestion de planning inexistant.
    # get_by_ekey_or_404 ou message custom
    planning = Planning.objects.get_by_ekey(planning_ekey)
    other_participants = []
    for user in User.objects.filter(event__planning__pk=planning.pk)\
                            .distinct()\
                            .order_by('first_name'):
        if user != request.user:
            other_participants.append(user)
    events = list(planning.event_set.all())
    #  TODO: Voir prefetch_related pour optimisation
    for event in events:
        event.user_part = None
        event.parts = [None]*len(other_participants)
        event.availability_count = 0
        event.dico = defaultdict(list)
        event_parts = event.participation_set.all()
        for part in event_parts:
            event.dico[part.answer].append(part.participant.first_name)
            if part.answer == 'YES':
                event.availability_count += 1
            if part.participant == request.user:
                event.user_part = part
            elif part.participant in other_participants:
                event.parts[other_participants.index(part.participant)] = part
    context = {'planning': planning,
               'other_participants': other_participants,
               'events': events}
    return render(request,
                  'participations/view_planning.html', context)

# @login_required
# def view_planning(request, planning_ekey): # si pas default. old function
#     planning = Planning.objects.get_by_ekey(planning_ekey)
#     other_participants = []
#     for user in User.objects.filter(event__planning__pk=planning.pk)\
#                             .distinct()\
#                             .order_by('first_name'):
#         if user != request.user:
#             other_participants.append(user)
#     events = {}
#     #  TODO: Voir prefetch_related pour optimisation
#     for event in planning.event_set.all():
#         vls = []
#         for user in other_participants:
#             try:
#                 part = event.participation_set.get(participant=user)
#                 vls.append(part)
#             except Participation.DoesNotExist:
#                 vls.append(None)
#             events[event] = vls
#     context = {'planning': planning,
#                'other_participants': other_participants,
#                'events': events}
#     return render(request,
#                   'participations/view_planning.html', context)


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
