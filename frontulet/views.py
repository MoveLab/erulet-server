from django.shortcuts import render
from appulet.models import *
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from appulet.forms import RegistrationForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login


def show_landing_page(request):
    context = {}
    return render(request, 'frontulet/landing_page.html', context)


def show_privacy_policy(request):
    context = {}
    return render(request, 'frontulet/privacy.html', context)


def show_home(request):
    context = {}
    return render(request, 'frontulet/home.html', context)


def show_map(request):
    context = {'routes': Route.objects.all()}
    return render(request, 'frontulet/map.html', context)


def show_route_list(request, whose=''):
    if request.user.is_authenticated():
        if whose == 'mine':
            routes = Route.objects.filter(created_by=request.user)
            title = 'My Routes'
        elif whose == 'others':
            routes = Route.objects.exclude(created_by=request.user)
            title = "Other Hikers' Routes"
        elif whose == 'official':
            routes = Route.objects.filter(official=True)
            title = "Official Routes"
        else:
            routes = Route.objects.all()
            title = "All Routes"
    else:
        if whose == 'official':
            routes = Route.objects.filter(official=True)
            title = "Official Routes"
        else:
            routes = Route.objects.all()
            title = "All Routes"
    context = {'routes': routes, 'title': title}
    return render(request, 'frontulet/route_list.html', context)


def show_route_detail(request, id):
    context = {'name': 'No Route', 'short_description': '', 'description': 'There is no route with the id number you requested. Try requesting a different id.'}
    this_id = int(id)
    if Route.objects.filter(pk=this_id):
        this_route = Route.objects.get(pk=this_id)
        context = {'name': this_route.__unicode__(), 'short_description': this_route.short_description, 'description': this_route.description, 'steps': this_route.track.steps.all()}
    return render(request, 'frontulet/route_detail.html', context)


def show_profile(request):
    this_user = request.user
    these_routes = Route.objects.filter(created_by=this_user)
    n_routes = these_routes.count()
    n_pois = Highlight.objects.filter(created_by=this_user).count()
    context = {'user_name': this_user.username, 'first_name': this_user.first_name, 'last_name': this_user.last_name, 'email': this_user.email, 'n_routes': n_routes, 'n_pois': n_pois}
    return render(request, 'frontulet/user_profile.html', context)


class RegistrationView(FormView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('show_profile')

    def form_valid(self, form):
        new_user = form.save()
        request = self.request
        user = authenticate(username=request.POST['username'], password=request.POST['password1'])
        login(self.request, user)
        return HttpResponseRedirect(reverse('show_profile'))