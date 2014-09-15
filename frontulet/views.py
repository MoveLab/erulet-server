from django.shortcuts import render
from appulet.models import *


def show_landing_page(request):
    context = {}
    return render(request, 'frontulet/landing_page.html', context)


def show_privacy_policy(request):
    context = {}
    return render(request, 'frontulet/privacy.html', context)


def show_map(request):
    context = {'routes': Route.objects.all()}
    return render(request, 'frontulet/map.html', context)


def show_landing_page(request):
    context = {}
    return render(request, 'frontulet/landing_page.html', context)
