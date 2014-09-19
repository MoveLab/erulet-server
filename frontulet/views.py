from django.shortcuts import render, render_to_response
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import authenticate, login
import gpxpy
import gpxpy.gpx
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from appulet.models import *
from frontulet.forms import *
import zipfile, shutil
from django.conf import settings


def show_landing_page(request):
    context = {}
    return render(request, 'frontulet/landing_page.html', context)


def show_privacy_policy(request):
    context = {}
    return render(request, 'frontulet/privacy.html', context)


def show_home(request):
    context = {}
    return render(request, 'frontulet/home.html', context)


def show_about(request):
    context = {}
    return render(request, 'frontulet/about.html', context)


def show_map(request):
    step_list = list()
    for route in Route.objects.all():
        step_list.append(route.track.steps.all().order_by('order'))
    context = {'routes': Route.objects.all(), 'steps': step_list}
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
        has_reference = this_route.reference is not None
        reference_html = ''
        if has_reference:
            reference_html_raw = this_route.reference.reference_html
            reference_html = reference_html_raw.replace('src="', 'src="'+this_route.reference.reference_url_base+'/')
        owner = request.user == this_route.created_by
        these_steps = this_route.track.steps.all().order_by('order')
        these_highlights = [[highlight, [[reference, reference.reference_html.replace('src="', 'src="'+reference.reference_url_base+'/').split('</head>')[-1].split('</html>')[0]] for reference in highlight.references.all()]] for highlight in Highlight.objects.all() if highlight.step in these_steps]
        these_highlights.sort(key=lambda x: x[0].order)
        context = {'owner': owner, 'name': this_route.__unicode__(), 'short_description': this_route.short_description, 'description': this_route.description, 'has_reference': has_reference, 'reference_html': reference_html, 'steps': these_steps, 'these_highlights': these_highlights, 'id': this_id}
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

    if this_route.gpx_track:
        gpx_file = open(settings.MEDIA_ROOT + this_route.gpx_track.name)
        gpx = gpxpy.parse(gpx_file)

        for step in Step.objects.filter(track=this_track):
            step.delete()

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

    if this_route.gpx_waypoints:

        gpx_file = open(settings.MEDIA_ROOT + this_route.gpx_waypoints.name)
        gpx = gpxpy.parse(gpx_file)

        if gpx.waypoints:
            this_order_number = 1
            for waypoint in gpx.waypoints:
                new_step = Step()
                new_step.latitude = waypoint.latitude
                new_step.longitude = waypoint.longitude
                new_step.altitude = waypoint.elevation
                new_step.track = this_track
                new_step.save()

                new_highlight = Highlight()
                new_highlight.created_by = this_user
                new_highlight.type = 1
                new_highlight.name = waypoint.name
                new_highlight.step = new_step
                new_highlight.order = this_order_number
                new_highlight.save()
                this_order_number += 1


def parse_gpx_pois(this_user, this_route, this_track):

    if this_route.gpx_pois:
        gpx_file = open(settings.MEDIA_ROOT + this_route.gpx_pois.name)
        gpx = gpxpy.parse(gpx_file)

        if gpx.waypoints:
            this_order_number = 1
            for waypoint in gpx.waypoints:
                new_step = Step()
                new_step.latitude = waypoint.latitude
                new_step.longitude = waypoint.longitude
                new_step.altitude = waypoint.elevation
                new_step.track = this_track
                new_step.save()

                new_highlight = Highlight()
                new_highlight.created_by = this_user
                new_highlight.type = 0
                new_highlight.name = waypoint.name
                new_highlight.step = new_step
                new_highlight.order = this_order_number
                new_highlight.save()
                this_order_number += 1


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
        return render(request, 'registration/no_permission_must_login.html')


def edit_route(request, id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_route = Route.objects.get(pk=id)
        this_track = this_route.track
        if this_route.created_by == request.user:
            if request.method == 'POST':
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
                    args['form'] = OfficialRouteForm(instance=this_route)
                else:
                    args['form'] = RouteForm(instance=this_route)

                return render(request, 'frontulet/edit_route.html', args)

        else:
            return render(request, 'registration/no_permission_not_yours.html')

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_highlight(request, route_id, highlight_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_highlight = Highlight.objects.get(pk=highlight_id)
        if this_highlight.created_by == request.user:
            if request.method == 'POST':
                form = HighlightForm(request.POST, request.FILES, instance=this_highlight)
                args['form'] = form
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))

            else:
                args['form'] = HighlightForm(instance=this_highlight)

                return render(request, 'frontulet/edit_highlight.html', args)

        else:
            return render(request, 'registration/no_permission_not_yours.html')

    else:
        return render(request, 'registration/no_permission_must_login.html')


def add_css(this_reference):
    this_path = os.path.dirname(this_reference.html_file.path)
    new_css_file = open(os.path.join(this_path, 'erholet-ref-style.css'), 'w')
    new_css_file.write('body{width:94%}img {width:100%; margin-bottom:5px}')
    new_css_file.close()


def set_up_reference(reference):
    ext = reference.html_file.name.split('.')[-1]
    this_dir = os.path.dirname(reference.html_file.path)
    if ext == 'zip':
        this_file = zipfile.ZipFile(reference.html_file.path)
        file_names = this_file.namelist()
        allowed_extensions = ['jpg', 'png', 'gif', 'mp4', 'css', 'html']
        html_file_paths = []
        for name in file_names:
            this_extension = name.split('.')[-1]
            if this_extension == 'html':
                html_file_paths.append(os.path.join(this_dir, name))
            elif this_extension not in allowed_extensions:
                return False
        if len(html_file_paths) != 1:
            return False
        else:
            this_file.extractall(path=this_dir)
            os.rename(html_file_paths[0], os.path.join(this_dir, 'reference.html'))
            these_extensions = [name.split('.')[-1] for name in file_names]
            if 'css' not in these_extensions:
                add_css(reference)
            return True
    elif ext == 'html':
        add_css(reference)
        shutil.copyfile(reference.html_file.path, os.path.join(this_dir, 'reference.html'))
        return True
    else:
        return False


def make_new_route_reference(request, route_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))

        if request.method == 'POST':
            this_reference = Reference()
            this_reference.save()
            this_route = Route.objects.get(pk=route_id)
            this_route.reference = this_reference
            this_route.save()
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                if set_up_reference(this_reference):
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))
                else:
                    args['form'] = ReferenceForm()
                    return render(request, 'frontulet/wrong_file_type.html', args)
        else:
            args['form'] = ReferenceForm()

        return render(request, 'frontulet/create_reference.html', args)

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_route_reference(request, route_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_route = Route.objects.get(pk=route_id)
        this_reference = Reference.objects.get(pk=this_route.reference.id)
        if request.method == 'POST':
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                if set_up_reference(this_reference):
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))
                else:
                    args['form'] = ReferenceForm()
                    return render(request, 'frontulet/wrong_file_type.html', args)
        else:
            args['form'] = ReferenceForm(instance=this_reference)
        return render(request, 'frontulet/edit_reference.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def make_new_highlight_reference(request, route_id, highlight_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))

        if request.method == 'POST':
            this_highlight = Highlight.objects.get(pk=highlight_id)
            this_reference = Reference()
            this_reference.highlight = this_highlight
            this_reference.save()
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                if set_up_reference(this_reference):
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))
                else:
                    args['form'] = ReferenceForm()
                    return render(request, 'frontulet/wrong_file_type.html', args)
            else:
                this_reference.delete()
        else:
            args['form'] = ReferenceForm()

        return render(request, 'frontulet/create_reference.html', args)

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_highlight_reference(request, route_id, reference_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_reference = Reference.objects.get(pk=reference_id)
        if request.method == 'POST':
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                if set_up_reference(this_reference):
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))
                else:
                    args['form'] = ReferenceForm()
                    return render(request, 'frontulet/wrong_file_type.html', args)
        else:
            args['form'] = ReferenceForm(instance=this_reference)
        return render(request, 'frontulet/edit_reference.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_profile(request):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_user = request.user
        if request.method == 'POST':
            form = ProfileForm(request.POST, instance=this_user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('show_profile'))

        else:
            args['form'] = ProfileForm()

        return render(request, 'frontulet/edit_profile.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')
