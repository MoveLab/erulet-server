from django.shortcuts import render, render_to_response
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import authenticate, login
import gpxpy
import gpxpy.gpx
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from appulet.models import *
from frontulet.forms import RegistrationForm
from frontulet.forms import RouteForm, OfficialRouteForm


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


def parse_gpx_track(this_route, this_track):

    gpx_file = open(settings.MEDIA_ROOT + this_route.gpx_track.name)
    gpx = gpxpy.parse(gpx_file)

    if gpx.tracks:
        for track in gpx.tracks:
            if track.segments:
                for segment in track.segments:
                    if segment.points:
                        this_order_number = 1
                        for point in segment.points:
                            new_step = Step()
                            new_step.track = this_track
                            new_step.latitude = point.latitude
                            new_step.longitude = point.longitude
                            new_step.order = this_order_number
                            new_step.save()
                            this_order_number += 1


def parse_gpx_waypoints(this_user, this_route, this_track):

    gpx_file = open(settings.MEDIA_ROOT + this_route.gpx_waypoints.name)
    gpx = gpxpy.parse(gpx_file)

    if gpx.waypoints:
        for waypoint in gpx.waypoints:
            new_step = Step()
            new_step.latitude = waypoint.latitude
            new_step.longitude = waypoint.longitude
            new_step.altitude = waypoint.elevation
            new_step.track = this_track
            new_step.save()

            new_highlight = Highlight()
            new_highlight.user = this_user
            new_highlight.type = 1
            new_highlight.name = waypoint.name
            new_highlight.step = new_step
            new_highlight.save()


def parse_gpx_pois(this_user, this_route, this_track):

    gpx_file = open(settings.MEDIA_ROOT + this_route.gpx_pois.name)
    gpx = gpxpy.parse(gpx_file)

    if gpx.waypoints:
        for waypoint in gpx.waypoints:
            new_step = Step()
            new_step.latitude = waypoint.latitude
            new_step.longitude = waypoint.longitude
            new_step.altitude = waypoint.elevation
            new_step.track = this_track
            new_step.save()

            new_highlight = Highlight()
            new_highlight.user = this_user
            new_highlight.type = 0
            new_highlight.name = waypoint.name
            new_highlight.step = new_step
            new_highlight.save()


def make_new_route(request):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))

        if request.method == 'POST':
            this_route = Route()
            this_route.created_by = request.user
            this_track = Track()
            this_track.save()
            this_route.track = this_track
            this_route.save()
            if 'scientists' in [group.name for group in request.user.groups.all()]:
                form = OfficialRouteForm(request.POST, request.FILES, instance=this_route)
            else:
                form = RouteForm(request.POST, request.FILES, instance=this_route)
            args['form'] = form
            if form.is_valid():
                form.save()
                parse_gpx_track(this_route, this_track)
                parse_gpx_waypoints(request.user, this_route, this_track)
                parse_gpx_pois(request.user, this_route, this_track)

                return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(this_route.id)}))

        else:
            if 'scientists' in [group.name for group in request.user.groups.all()]:
                args['form'] = OfficialRouteForm()
            else:
                args['form'] = RouteForm()

        return render(request, 'frontulet/create_route.html', args)

    else:
        return render(request, 'registration/no_permission.html')

