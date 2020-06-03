from plannings.models import GuestEmail


def update_guests(planning, new_emails):
    old_emails = planning.get_guest_emails
    for email in new_emails:
        if email in old_emails:
            old_emails.remove(email)
            new_emails.remove(email)

    planning.guest_emails.filter(email__in=old_emails).delete()
    add_guests(planning, new_emails)


def add_guests(planning, emails):
    for email in emails:
        try:
            planning.guest_emails.add(GuestEmail.objects.get(email=email))
        except GuestEmail.DoesNotExist:
            planning.guest_emails.create(email=email)
