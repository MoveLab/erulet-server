from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import mixins
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.db.models import Q
from appulet.serializers import *
from appulet.models import *
import os
import zipfile
import StringIO
from django.http import HttpResponse
import gpxpy
import gpxpy.gpx
from django.conf import settings
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from appulet.forms import RouteForm, OfficialRouteForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


class ReadOnlyModelViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides `retrieve`, and 'list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass


class WriteOnlyModelViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides`create` action.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass


class ReadWriteOnlyModelViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    A viewset that provides `retrieve`, 'list`, and `create` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass


def get_route_files(request, route_id):


    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    filenames = ["/tmp/file1.txt", "/tmp/file2.txt"]

    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = "somefiles"
    zip_filename = "%s.zip" % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    return resp


@api_view(['POST'])
def post_media(request):
    """
API endpoint for uploading media associated with a highlight. Data must be posted as multipart form,
with with _media_ used as the form key for the file itself.

**Fields**

* media: The media file's binary data
* id: The id of the highlight.
* created_by: The user id who created this highlight.
* name: The name of the highlight.
* long_text: Text that should be displayed with the highlight.
* radius: Radius, in meters on the ground, that the highlight covers.
* type: Type of highlight.

    """
    if request.method == 'POST':
        instance = Highlight(media=request.FILES['media'], id=request.DATA['id'], created_by=request.DATA['created_by'],
                             name=request.DATA['name'], long_text=request.DATA['long_text'], radius=request.DATA['radius'], type=request.DATA['type'])
        instance.save()
        return Response('uploaded')


class HighlightViewSet(ReadWriteOnlyModelViewSet):
    queryset = Highlight.objects.all()
    serializer_class = HighlightSerializer


class InteractiveImageViewSet(ReadOnlyModelViewSet):
    queryset = InteractiveImage.objects.all()
    serializer_class = InteractiveImageSerializer


class TrackViewSet(ReadWriteOnlyModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer


class TrackNestedViewSet(ReadWriteOnlyModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackNestedSerializer


class BoxViewSet(ReadOnlyModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class ReferenceViewSet(ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class RouteViewSet(ReadWriteOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class RouteNestedViewSet(ReadOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteNestedSerializer


class StepViewSet(ReadWriteOnlyModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_default_renderer(self, view):
        return JSONRenderer()


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


@login_required()
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
            args['form'] = RouteForm()

        return render_to_response('appulet/create_route.html', args)

    else:
        return render(request, 'registration/no_permission.html')

