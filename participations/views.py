from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from plannings.models import Planning


@login_required
def view_planning(request, planning_ekey):
    context = {'planning': Planning.objects.get_by_ekey(planning_ekey)}
    return render(request,
                  'participations/view_planning.html', context)
