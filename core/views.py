from django.shortcuts import render


def index(request):
    """View of the main page."""
    return render(request, 'core/index.html')


def legal(request):
    """View of the legal notice page"""
    return render(request, "core/legal_notice.html")
