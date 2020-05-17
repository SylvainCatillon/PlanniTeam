from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import FormView

from accounts.models import User
from plannings.forms import PlanningCreationForm
from plannings.models import Planning, GuestMail


class CreatePlanningView(FormView):
    template_name = 'plannings/create_planning.html'
    form_class = PlanningCreationForm
    success_url = '/planning/create/'

    def form_valid(self, form):
        import pdb; pdb.set_trace()
        return super().form_valid(form)

@login_required
def create_planning(request):
    if request.method == 'POST':
        form = PlanningCreationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            protected = form.cleaned_data.get('protected')
            #if not name
            creator = get_object_or_404(User, pk=request.POST.get('creator_id'))
            params = {'creator': creator, 'name': name}
            if protected:
                params['protected'] = True  # accepter protected=None dans modèle pour enlever cette sécu? Ou alors changer protected après création, mais requete SQL de plus
            planning = Planning.objects.create(**params)
            if protected:
                guest_mails = request.POST.getlist('guest_mail')
                for mail in guest_mails:
                    try:
                        planning.guest_mails.add(GuestMail.objects.get(mail=mail))
                    except GuestMail.DoesNotExist:
                        planning.guest_mails.create(mail=mail)
            return HttpResponseRedirect(reverse('plannings:created', args=(planning.ekey,)))
    else:
        form = PlanningCreationForm()
    return render(request, 'plannings/create_planning.html', {'form': form})


def planning_created(request, planning_ekey): # Remplacer par TemplateView??
    link = request.build_absolute_uri(reverse(
        'plannings:display', args=(planning_ekey,)))  # security hole? Remplacer par link = get_current_site(request) ou gestion desite framework: https://docs.djangoproject.com/en/3.0/ref/contrib/sites/#getting-the-current-domain-for-full-urls
    return render(request, 'plannings/created.html', {'link': link,})


def display_planning(request, planning_ekey):
    pass
