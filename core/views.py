from django.shortcuts import render


def index(request):
    """View of the main page."""
    return render(request, 'core/index.html')
