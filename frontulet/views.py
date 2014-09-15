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


def show_route_detail(request, id):
    context = {'name': 'No Route', 'short_description': '', 'description': 'There is no route with the id number you requested. Try requesting a different id.'}
    this_id = int(id)
    if Route.objects.filter(pk=this_id):
        this_route = Route.objects.get(pk=this_id)
        context = {'name': this_route.__unicode__(), 'short_description': this_route.short_description, 'description': this_route.description, 'steps': this_route.track.steps.all()}
    return render(request, 'frontulet/route_detail.html', context)

