from json import loads

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.http import require_POST

from accounts.models import User
from participations.models import Participation
from plannings.models import Planning, Event


@require_POST
def participate(request):
    if not request.user.is_authenticated:
        return HttpResponse('Veuillez vous connecter', status=401)  # TODO: changer erreur code? 403?
    for json_part in request.POST.getlist('participation'):
        participation = loads(json_part)
        # TODO: gestion no event or no answer. get_object_or_404? Mais je ne
        #   veux pas forcement interrompre la requete si seulement un object
        #   n'est pas conforme...
        #   Forbidden interrompt la boucle, mais une partie des objects est
        #   déjà crée... Use block atomic?
        event = Event.objects.get(pk=participation['event'])
        planning = event.planning
        if not planning.user_has_access(request.user):
            return HttpResponseForbidden()
        Participation.objects.update_or_create(
            participant=request.user, event=event,
            defaults={'answer': participation['answer']}
        )
    return HttpResponse('Votre participation est enregistrée')  # TODO: trad


# TODO:
#   -gestion de planning inexistant, get_by_ekey_or_404 ou message custom
#   -utilisation d'un modelForm avec widget RadioSelect
#   -refactor en plusieurs fonctions
@login_required
def view_planning(request, planning_ekey):
    planning = Planning.objects.get_by_ekey(planning_ekey)
    if not planning.user_has_access(request.user):
        return render(request, 'participations/protected_planning.html')

    # Get a list of all the planning's participants, except the current user
    other_participants = []
    for user in User.objects.filter(event__planning__pk=planning.pk)\
                            .distinct()\
                            .order_by('first_name'):
        if user != request.user:
            other_participants.append(user)

    # Gather all the planning's events, and add information to display
    events = list(planning.event_set.all())
    #  TODO: Voir prefetch_related pour optimisation.
    #   Voir noms variables
    for event in events:
        # Set the participations as None, to have a sequence of participations
        # in the same order that the other_participants list.
        # Each item will be the participation if founded, or the default None
        event.other_participations = [None]*len(other_participants)
        event.user_participation = None
        # Participations_summary is a dict {answer: list of participants name},
        # to display a summary of the answers in the planning
        event.participations_summary = {'YES': [], 'MAYBE': [], 'NO': []}
        for part in event.participation_set.all():
            event.participations_summary[part.answer].append(
                part.participant.first_name)
            if part.participant == request.user:
                event.user_participation = part
            elif part.participant in other_participants:
                p_index = other_participants.index(part.participant)
                event.other_participations[p_index] = part

    context = {'planning': planning,
               'other_participants': other_participants,
               'events': events,
               'answer_choices': Participation.answer_choices}
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
