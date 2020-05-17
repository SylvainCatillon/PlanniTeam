from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

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
        return HttpResponseRedirect(reverse('plannings:created', args=(planning.ekey,)))
    return render(request, 'plannings/create_planning.html')


def planning_created(request, planning_ekey):
    link = request.build_absolute_uri(reverse(
        'plannings:display', args=(planning_ekey,)))  # security hole? Remplacer par link = get_current_site(request) ou gestion desite framework: https://docs.djangoproject.com/en/3.0/ref/contrib/sites/#getting-the-current-domain-for-full-urls
    return render(request, 'plannings/created.html', {'link': link,})


def display_planning(request, planning_ekey):
    pass
