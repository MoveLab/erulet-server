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
from PIL import Image
import shutil


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
    route_list = list()
    for route in Route.objects.all():
        these_track_steps = filter(lambda step: step.order is not None, route.track.steps.all().order_by('order'))
        these_highlight_steps = filter(lambda step: step.order is None, route.track.steps.all())
        these_highlights = map(lambda highlight: {'route_name': highlight.step.track.route.get_name(request.LANGUAGE_CODE), 'route_id': highlight.step.track.route.id, 'highlight_id': highlight.id, 'latitude': highlight.step.latitude, 'longitude': highlight.step.longitude, 'name': highlight.get_name(request.LANGUAGE_CODE), 'long_text': highlight.get_long_text(request.LANGUAGE_CODE), 'type': highlight.type}, [hl for hl in Highlight.objects.filter(step__in=these_highlight_steps).order_by('order')])
        route_list.append({'track_steps': these_track_steps, 'highlights': these_highlights})
    context = {'routes': Route.objects.all(), 'route_list': route_list}
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
            title = "Holet's Routes"
        else:
            routes = Route.objects.all()
            title = "All Routes"
    else:
        if whose == 'official':
            routes = Route.objects.filter(official=True)
            title = "Holet's Routes"
        else:
            routes = Route.objects.all()
            title = "All Routes"
    routes_localized = map(lambda route: {'name': route.get_name(request.LANGUAGE_CODE), 'short_description': route.get_short_description(request.LANGUAGE_CODE), 'id': route.id}, [r for r in routes])
    context = {'routes': routes_localized, 'title': title}
    return render(request, 'frontulet/route_list.html', context)


def show_route_detail(request, id):
    context = {'name': 'No Route', 'short_description': '', 'description': 'There is no route with the id number you requested. Try requesting a different id.'}
    this_id = int(id)
    if Route.objects.filter(pk=this_id):
        this_route = Route.objects.get(pk=this_id)
        has_reference = this_route.reference is not None
        reference_html = ''
        if has_reference:
            reference_html_raw = this_route.reference.get_reference_html(request.LANGUAGE_CODE)
            reference_html = reference_html_raw.replace('src="', 'src="'+this_route.reference.reference_url_base+'/').replace('../general_references', '/media/holet/references/general_references')
        owner = request.user == this_route.created_by
        these_steps = this_route.track.steps.all().order_by('order')
        these_highlights_localized = map(lambda h: {'id': h.id, 'uuid': h.uuid, 'name': h.get_name(request.LANGUAGE_CODE), 'long_text': h.get_long_text(request.LANGUAGE_CODE), 'media': h.media, 'image': h.image, 'video': h.video, 'media_ext': h.media_ext, 'radius': h.radius, 'type': h.type, 'step': h.step, 'order': h.order, 'references': map(lambda r: {'id': r.id, 'name': r.get_name(request.LANGUAGE_CODE), 'html': r.get_reference_html(request.LANGUAGE_CODE).replace('src="', 'src="'+r.reference_url_base+'/').replace('../general_references', '/media/holet/references/general_references').split('</head>')[-1].split('</html>')[0], 'uuid': r.uuid}, [ref for ref in h.references.all()]), 'interactive_images': [ii for ii in h.interactive_images.all()]}, [hl for hl in Highlight.objects.filter(step__in=these_steps).order_by('order')])
        context = {'owner': owner, 'name': this_route.get_name(request.LANGUAGE_CODE), 'short_description': this_route.get_short_description(request.LANGUAGE_CODE), 'description': this_route.get_description(request.LANGUAGE_CODE), 'has_reference': has_reference, 'reference_html': reference_html, 'steps': these_steps, 'these_highlights': these_highlights_localized, 'id': this_id}
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

        this_track.name_oc = this_route.name_oc
        this_track.name_es = this_route.name_es
        this_track.name_ca = this_route.name_ca
        this_track.name_fr = this_route.name_fr
        this_track.name_en = this_route.name_en

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


def parse_gpx_waypoints(lang, this_user, this_route, this_track):

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
                new_highlight.name_oc = waypoint.name
                new_highlight.name_es = waypoint.name
                new_highlight.name_ca = waypoint.name
                new_highlight.name_fr = waypoint.name
                new_highlight.name_en = waypoint.name
                new_highlight.step = new_step
                new_highlight.order = this_order_number
                new_highlight.save()
                this_order_number += 1


def parse_gpx_pois(lang, this_user, this_route, this_track):

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
                new_highlight.name_oc = waypoint.name
                new_highlight.name_es = waypoint.name
                new_highlight.name_ca = waypoint.name
                new_highlight.name_fr = waypoint.name
                new_highlight.name_en = waypoint.name
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
                parse_gpx_waypoints(request.LANGUAGE_CODE, request.user, this_route, this_track)
                parse_gpx_pois(request.LANGUAGE_CODE, request.user, this_route, this_track)

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
        if this_route.created_by == request.user:
            if request.method == 'POST':
                if 'scientists' in [group.name for group in request.user.groups.all()]:
                    form = EditOfficialRouteForm(request.POST, instance=this_route)
                else:
                    form = EditRouteForm(request.POST, instance=this_route)
                    args['form'] = form
                if form.is_valid():
                    form.save()

                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(this_route.id)}))

            else:
                if 'scientists' in [group.name for group in request.user.groups.all()]:
                    args['form'] = EditOfficialRouteForm(instance=this_route)
                else:
                    args['form'] = EditRouteForm(instance=this_route)

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
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}) + "#h" + str(highlight_id))
                else:
                    args['error_message'] = 'Wrong file type: Make sure the file you have selected is either a JPG, PNG, GIF, MP4, WEBM, or OGG.'
                    return render(request, 'frontulet/upload_error.html', args)

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
    uploaded_file_name_split = reference.html_file.name.split('.')
    ext = uploaded_file_name_split[-1]
    this_dir = os.path.dirname(reference.html_file.path)
    if ext == 'zip':
        this_file = zipfile.ZipFile(reference.html_file.path)
        file_names = this_file.namelist()
        allowed_extensions = ['jpg', 'png', 'gif', 'mp4', 'css', 'html']
        html_file_paths = []
        for name in file_names:
            if name[:3] == '../':
                return 'At least one of the files in your ZIP archive has a path starting with "../". Please do not try to give files in the archives paths that point outside of the archived folder.'
            elif os.path.isabs(name):
                return 'At least one of the files in your ZIP archive has an absolute path. Please do not try to give files in the archives paths that point outside of the archived folder.'
            name_split = name.split('.')
            this_extension = name_split[-1]
            if this_extension == 'html':
                lang_code = name_split[0].split('-')[-1][:2]
                if lang_code not in map(lambda x: x[0].upper(), settings.LANGUAGES) + map(lambda x: x[0].upper(), settings.LANGUAGES):
                    reference.delete()
                    return 'At least one HTML file in your ZIP archive was missing a supported language code. Please make sure each HTML has a file name that ends in either -oc.html, -es,html, -ca.html, -fr.html, or -en.html.'
                else:
                    html_file_paths.append((lang_code.lower(), os.path.join(this_dir, name)))
            elif this_extension.lower() not in allowed_extensions:
                reference.delete()
                return 'You tried to upload a zip file containing a file or files that are not HTML, CSS, JPG, PNG, GIF, or MP4. Please make sure the ZIP archive contains only those file type.'
        if len(html_file_paths) > 5:
            reference.delete()
            return 'There are more than five HTML files in this ZIP archive. Please include no more than one HTML file for each of the five supported languages (Aranese, Spanish, Catalan, French, and English).'
        elif len(html_file_paths) == 0:
            reference.delete()
            return 'There is no HTML file in this ZIP archive. Please include at least one HTML file.'
        else:
            this_file.extractall(path=this_dir)
            # if it is a general reference, then extract also to general references folder
            if reference.general:
                general_reference_path = os.path.join(os.path.dirname(this_dir), 'general_references')
                this_file.extractall(path=general_reference_path)
            for html_path in html_file_paths:
                with codecs.open(html_path[1], 'r', 'iso-8859-1') as f:
                    this_html_original = f.read()
                    this_html_final = this_html_original.replace('href="IT', 'href="../general_references/IT')
                    new_file = codecs.open(os.path.join(this_dir, 'reference_' + html_path[0] + '.html'), 'w+', 'iso-8859-1')
                    new_file.write(this_html_final)
                    new_file.close()
                    f.close()
                    # delete original file
                    os.remove(html_path[1])
            these_extensions = [name.split('.')[-1] for name in file_names]
            if 'css' not in these_extensions:
                add_css(reference)
            return 'OK'
    elif ext == 'html':
        add_css(reference)
        lang_code = uploaded_file_name_split[0].split('_')[-1]
        shutil.copyfile(reference.html_file.path, os.path.join(this_dir, 'reference_' + lang_code + '.html'))
        return 'OK'
    else:
        reference.delete()
        return 'You tried to upload something other than a ZIP or HTML file. Please check the file and try again.'


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
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
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
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
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
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}) + "#h" + str(highlight_id))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
            else:
                this_reference.delete()
        else:
            args['form'] = ReferenceForm()

        return render(request, 'frontulet/create_reference.html', args)

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_highlight_reference(request, route_id, reference_id):
    if request.user.is_authenticated():
        this_reference = Reference.objects.get(pk=reference_id)
        this_highlight = this_reference.highlight
        args = {}
        args.update(csrf(request))
        args['route_id'] = route_id
        args['highlight_id'] = this_highlight.id
        this_reference = Reference.objects.get(pk=reference_id)
        if request.method == 'POST':
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}) + "#h" + str(this_highlight.id))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
        else:
            args['form'] = ReferenceForm(instance=this_reference)
        return render(request, 'frontulet/edit_reference.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def delete_highlight_reference(request, route_id, reference_id):
    this_reference = Reference.objects.get(pk=reference_id)
    this_highlight = this_reference.highlight
    trees_to_delete = []
    if request.user.is_authenticated():
        if this_reference.highlight.created_by == request.user:
            if this_reference.html_file:
                trees_to_delete.append(os.path.dirname(this_reference.html_file.path))
            this_reference.delete()
            for this_tree in trees_to_delete:
                shutil.rmtree(this_tree)
    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}) + '#h' + str(this_highlight.id))


def delete_route_reference(request, route_id):
    this_route = Route.objects.get(id=route_id)
    this_reference = this_route.reference
    trees_to_delete = []
    if request.user.is_authenticated():
        if this_reference.route.created_by == request.user:
            if this_reference.html_file:
                trees_to_delete.append(os.path.dirname(this_reference.html_file.path))
            this_reference.delete()
            for this_tree in trees_to_delete:
                shutil.rmtree(this_tree)
    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))


def delete_route(request, route_id):
    this_route = Route.objects.get(id=route_id)
    this_track = this_route.track
    trees_to_delete = []
    files_to_delete = []
    if request.user.is_authenticated():
        if this_route.created_by == request.user:
            # remove all route reference files
            if this_route.reference:
                if this_route.reference.html_file:
                    trees_to_delete.append(os.path.dirname(this_route.reference.html_file.path))
            # remove all gpx files
            if this_route.gpx_track:
                files_to_delete.append(this_route.gpx_track.path)
            if this_route.gpx_waypoints:
                files_to_delete.append(this_route.gpx_waypoints.path)
            if this_route.gpx_pois:
                files_to_delete.append(this_route.gpx_pois.path)
            for step in Step.objects.filter(track=this_track):
                for highlight in step.highlights.all():
                    if highlight.media:
                        files_to_delete.append(highlight.media.path)
                    for reference in highlight.references.all():
                        # remove all highlight reference files
                        if reference.html_file:
                            trees_to_delete.append(os.path.dirname(reference.html_file.path))
                    for interactive_image in highlight.interactive_images.all():
                        # remove interactive image files
                        if interactive_image.image_file:
                            files_to_delete.append(interactive_image.image_file.path)
            # first delete the route from the database
            this_route.delete()
            # now delete all associated files
            for this_file in files_to_delete:
                os.remove(this_file)
            for this_tree in trees_to_delete:
                shutil.rmtree(this_tree)
    return HttpResponseRedirect(reverse('show_home'))


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
            args['form'] = ProfileForm(instance=this_user)

        return render(request, 'frontulet/edit_profile.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def create_ii(request, highlight_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_ii = InteractiveImage()
        this_highlight = Highlight.objects.get(id=highlight_id)
        this_ii.highlight = this_highlight
        if request.method == 'POST':
            this_ii.save()
            form = InteractiveImageForm(request.POST, request.FILES, instance=this_ii)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('create_ii_box', kwargs={'ii_id': this_ii.id}))
            else:
                args['form'] = InteractiveImageForm()
                this_ii.delete()
                return render(request, 'frontulet/wrong_file_type_ii.html', args)

        else:
            args['form'] = InteractiveImageForm(instance=this_ii)

        return render(request, 'frontulet/create_ii.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_ii(request, ii_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_ii = InteractiveImage.objects.get(id=ii_id)
        if request.method == 'POST':
            form = InteractiveImageForm(request.POST, instance=this_ii)
            if form.is_valid():
                form.save()
                # clear all boxes from old ii
                for box in this_ii.boxes.all():
                    box.delete()
                return HttpResponseRedirect(reverse('create_ii_box', kwargs={'ii_id': this_ii.id}))

        else:
            args['form'] = InteractiveImageForm(instance=this_ii)

        return render(request, 'frontulet/create_ii.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def create_ii_box(request, ii_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_ii = InteractiveImage.objects.get(id=ii_id)
        args['image_url'] = this_ii.image_file.url
        args['display_width'] = 600.00
        args['scaling_factor'] = args['display_width'] / this_ii.original_width
        args['display_height'] = this_ii.original_height * args['scaling_factor']
        args['original_height'] = this_ii.original_height
        args['original_width'] = this_ii.original_width
        args['route_id'] = this_ii.highlight.step.track.route.id
        args['highlight_id'] = this_ii.highlight.id
        args['editing'] = False
        args['ii_id'] = ii_id
        this_box = Box()
        this_box.interactive_image = this_ii
        if this_ii.boxes.count() > 0:
            args['boxes'] = map(lambda b: {'box': b, 'message':b.get_message(request.LANGUAGE_CODE), 'all_messages': b.get_all_messages_html()}, [box for box in this_ii.boxes.all()])
        if request.method == 'POST':
            form = BoxForm(request.POST, instance=this_box)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('create_ii_box', kwargs={'ii_id': this_ii.id}))

        else:
            args['form'] = BoxForm(instance=this_box)

        return render(request, 'frontulet/create_ii_box.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_ii_box(request, ii_id, box_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_ii = InteractiveImage.objects.get(id=ii_id)
        args['image_url'] = this_ii.image_file.url
        args['display_width'] = 600.00
        args['scaling_factor'] = args['display_width'] / this_ii.original_width
        args['display_height'] = this_ii.original_height * args['scaling_factor']
        args['original_height'] = this_ii.original_height
        args['original_width'] = this_ii.original_width
        args['route_id'] = this_ii.highlight.step.track.route.id
        args['highlight_id'] = this_ii.highlight.id
        this_box = Box.objects.get(id=box_id)
        args['this_box'] = this_box
        args['editing'] = True
        args['ii_id'] = ii_id
        other_boxes = filter(lambda b: b != this_box, [box for box in this_ii.boxes.all()])
        if len(other_boxes) > 0:
            args['boxes'] = map(lambda b: {'box': b, 'message': b.get_message(request.LANGUAGE_CODE), 'all_messages': b.get_all_messages_html()}, other_boxes)
        if request.method == 'POST':
            form = BoxForm(request.POST, instance=this_box)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('create_ii_box', kwargs={'ii_id': this_ii.id}))

        else:
            args['form'] = BoxForm(instance=this_box)

        return render(request, 'frontulet/create_ii_box.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def view_ii(request, ii_id):
    args = {}
    args.update(csrf(request))
    this_ii = InteractiveImage.objects.get(id=ii_id)
    if request.user == this_ii.highlight.created_by:
        args['owner'] = True
    else:
        args['owner'] = False
    args['ii_id'] = ii_id
    args['image_url'] = this_ii.image_file.url
    args['display_width'] = 600.00
    args['scaling_factor'] = args['display_width'] / this_ii.original_width
    args['display_height'] = this_ii.original_height * args['scaling_factor']
    args['original_height'] = this_ii.original_height
    args['original_width'] = this_ii.original_width
    args['route_id'] = this_ii.highlight.step.track.route.id
    args['highlight_id'] = this_ii.highlight.id
    if this_ii.boxes.count() > 0:
        args['boxes'] = map(lambda b: {'box': b, 'message': b.get_message(request.LANGUAGE_CODE)}, [box for box in this_ii.boxes.all()])
    return render(request, 'frontulet/view_ii.html', args)


def delete_ii(request, ii_id):
    args = {}
    args.update(csrf(request))
    this_ii = InteractiveImage.objects.get(id=ii_id)
    this_highlight_id = this_ii.highlight.id
    this_route_id = this_ii.highlight.step.track.route.id
    this_ii.delete()
    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': this_route_id}) +"#h" + str(this_highlight_id) )


def show_general_references(request):
    scientist = 'scientists' in [group.name for group in request.user.groups.all()]
    these_references = map(lambda r: {'id': r.id, 'name': r.get_name(request.LANGUAGE_CODE), 'html': r.get_reference_html(request.LANGUAGE_CODE).replace('src="', 'src="'+r.reference_url_base+'/').split('</head>')[-1].split('</html>')[0], 'uuid': r.uuid}, [ref for ref in Reference.objects.filter(general=True)])
    context = {'references': these_references, 'scientist': scientist}
    return render(request, 'frontulet/general_references.html', context)


def make_new_general_reference(request):
    if request.user.is_authenticated() and 'scientists' in [group.name for group in request.user.groups.all()]:
        args = {}
        args.update(csrf(request))
        if request.method == 'POST':
            this_reference = Reference()
            this_reference.general = True
            this_reference.save()
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_general_references'))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
        else:
            args['form'] = ReferenceForm()

        return render(request, 'frontulet/create_reference.html', args)

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_general_reference(request, reference_id):
    if request.user.is_authenticated() and'scientists' in [group.name for group in request.user.groups.all()]:
        args = {}
        args.update(csrf(request))
        this_reference = Reference.objects.get(id=reference_id)
        if request.method == 'POST':
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_general_references'))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
        else:
            args['form'] = ReferenceForm(instance=this_reference)
        return render(request, 'frontulet/edit_reference.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def delete_general_reference(request, reference_id):
    this_reference = Reference.objects.get(id=reference_id)
    trees_to_delete = []
    if request.user.is_authenticated() and 'scientists' in [group.name for group in request.user.groups.all()]:
        if this_reference.html_file:
            trees_to_delete.append(os.path.dirname(this_reference.html_file.path))
        this_reference.delete()
        for this_tree in trees_to_delete:
            shutil.rmtree(this_tree, True)
        return HttpResponseRedirect(reverse('show_general_references'))
    else:
        return render(request, 'registration/no_permission_must_login.html')
