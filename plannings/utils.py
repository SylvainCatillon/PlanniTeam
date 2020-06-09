from plannings.models import GuestEmail


def update_guests(planning, new_emails):
    """Update the guests of a plannning.
    Takes as args a Planning object and a list of emails.
    -Get the current guests emails of the planning.
    -Delete the emails of the plannings which aren't on the new list
    -Add the emails of the new list which aren't in the planning's guests"""
    old_emails = planning.get_guest_emails
    # emails_to_delete = emails which are in old_emails but not in new_emails
    emails_to_delete = list(set(old_emails) - set(new_emails))
    # emails_to_add = emails which are in new_emails but not in old_emails
    emails_to_add = list(set(new_emails) - set(old_emails))

    planning.guest_emails.filter(email__in=emails_to_delete).delete()
    add_guests(planning, emails_to_add)


def add_guests(planning, emails):
    """Add guests in a planning.
    Takes as args a Planning object and a list of emails."""
    guests = []
    for email in emails:
        guests.append(GuestEmail.objects.get_or_create(email=email)[0])
    planning.guest_emails.add(*guests)
