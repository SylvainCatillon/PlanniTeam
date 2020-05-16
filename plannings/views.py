from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from plannings.models import Planning, GuestMail


@login_required
def create_planning(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name')
        #if not name
        params = {'creator': user, 'name': name}
        protected = request.POST.get('protected')
        if protected:
            params['protected'] = True  # accepter protected=None dans modèle pour enlever cette sécu? Ou alors changer protected après création, mais requete SQL de plus
        planning = Planning.objects.create(**params)
        if protected:
            guest_mails = request.POST.getlist('guest_mails')
            for mail in guest_mails:
                try:
                    planning.guest_mails.add(GuestMail.objects.get(mail=mail))
                except GuestMail.DoesNotExist:
                    planning.guest_mails.create(mail=mail)
    return render(request, 'plannings/created.html')
