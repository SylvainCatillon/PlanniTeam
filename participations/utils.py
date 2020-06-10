def prepare_events(events, user, other_participants):
    """Prepare the events to be displayed, by adding some information."""
    for event in events:
        # Set the participations as None, to have a sequence of participations
        # in the same order that the other_participants list.
        # Each item will be the participation if founded, or the default None
        event.other_participations = [None] * len(other_participants)
        event.user_participation = None
        # Participations_summary is a dict {answer: list of participants name},
        # to display a summary of the answers in the planning
        event.participations_summary = {'YES': [], 'MAYBE': [], 'NO': []}
        for part in event.participation_set.all():
            event.participations_summary[part.answer].append(
                part.participant.first_name)
            if part.participant == user:
                event.user_participation = part
            elif part.participant in other_participants:
                p_index = other_participants.index(part.participant)
                event.other_participations[p_index] = part
    return events
