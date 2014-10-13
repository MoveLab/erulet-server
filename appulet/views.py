import os
import zipfile
import StringIO
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import mixins
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.http import HttpResponse, HttpResponseRedirect
from appulet.serializers import *
from appulet.models import *
from django.conf import settings
from PIL import Image
from django.conf import settings
from datetime import datetime
import pytz
from django.db.models import Max

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


def get_route_map(request, route_id, last_updated_unix_time_utc=0):
    last_updated = pytz.utc.localize(datetime.fromtimestamp(int(last_updated_unix_time_utc)))
    # CASE 0: No route
    if Route.objects.filter(id=route_id).count() == 0:
        return HttpResponse("Route does not exist")
    # CASE 1: Route has no map
    this_route = Route.objects.get(id=route_id)
    if Map.objects.filter(route=this_route).count() == 0:
        return HttpResponse('This route has no map')
    # CASE 2: No changes since last update
    if this_route.map.last_modified < last_updated:
        return HttpResponse('There have been no changes since your last update')
    # CASE 3: there have been modifications, but there is already a zip file made after the most recent modification
    zpath = this_route.map.map_file_name
    zsource = this_route.map.map_file.path
    zip_subdir = "map_route_" + str(route_id)
    zip_filename = "%s.zip" % zip_subdir
    dest_ending = 'holet/route_maps/' + zip_filename
    zip_destination = os.path.join(settings.MEDIA_ROOT, dest_ending)
    if os.path.isfile(zip_destination) and pytz.utc.localize(datetime.utcfromtimestamp(os.path.getmtime(zip_destination))) > this_route.map.last_modified:
        return HttpResponseRedirect(os.path.join(settings.CURRENT_DOMAIN, settings.MEDIA_URL, dest_ending))
    # CASE 3: We actually need to make and serve a new zip file...
    zf = zipfile.ZipFile(zip_destination, "w")
    zf.write(zsource, zpath)
    zf.close()
    return HttpResponseRedirect(os.path.join(settings.CURRENT_DOMAIN, settings.MEDIA_URL, dest_ending))


def get_general_map(request, last_updated_unix_time_utc=0):
    last_updated = pytz.utc.localize(datetime.fromtimestamp(int(last_updated_unix_time_utc)))
    # CASE 0: No general maps on server
    if Map.objects.filter(type=1).count() == 0:
        return HttpResponse("No general maps on server")
    # CASE 1: General map has not been modified since last update
    this_map = Map.objects.filter(type=1).latest('last_modified')
    if this_map.last_modified < last_updated:
        return HttpResponse('There have been no changes since your last update')
    # CASE 2: there have been modifications, but there is already a zip file made after the most recent modification
    zpath = this_map.map_file_name
    zsource = this_map.map_file.path
    zip_subdir = "general_map"
    zip_filename = "%s.zip" % zip_subdir
    dest_ending = 'holet/route_maps/' + zip_filename
    zip_destination = os.path.join(settings.MEDIA_ROOT, dest_ending)
    if os.path.isfile(zip_destination) and pytz.utc.localize(datetime.utcfromtimestamp(os.path.getmtime(zip_destination))) > this_map.last_modified:
        return HttpResponseRedirect(os.path.join(settings.CURRENT_DOMAIN, settings.MEDIA_URL, dest_ending))
    # CASE 3: We actually need to make and serve a new zip file...
    if not os.path.exists(os.path.dirname(zip_destination)):
        os.makedirs(os.path.dirname(zip_destination))
    zf = zipfile.ZipFile(zip_destination, "w")
    zf.write(zsource, zpath)
    zf.close()
    return HttpResponseRedirect(os.path.join(settings.CURRENT_DOMAIN, settings.MEDIA_URL, dest_ending))


def get_general_reference_files(request, max_width=None, last_updated_unix_time_utc=0):
    last_updated = pytz.utc.localize(datetime.fromtimestamp(int(last_updated_unix_time_utc)))
    these_references = Reference.objects.filter(general=True)
    # CASE 0: no references in database
    if these_references.count() == 0:
        return HttpResponse('There are no general references in the database')
    most_recent_modification_time = these_references.aggregate(Max('last_modified'))['last_modified__max']
    # CASE 1: no modifications since last update
    if most_recent_modification_time and last_updated >= most_recent_modification_time:
        return HttpResponse('There have been no changes since your last update')
    zip_subdir = "general_references" + "_max_width_" + str(max_width)
    zip_filename = "%s.zip" % zip_subdir
    dest_ending = 'holet/zipped_general_references/' + zip_filename
    zip_destination = os.path.join(settings.MEDIA_ROOT, dest_ending)
    # CASE 2: there have been modifications, but there is already a zip file for the requested size and it was made after the most recent modification
    if os.path.isfile(zip_destination) and pytz.utc.localize(datetime.utcfromtimestamp(os.path.getmtime(zip_destination))) > most_recent_modification_time:
        return HttpResponseRedirect(os.path.join(settings.CURRENT_DOMAIN, settings.MEDIA_URL, dest_ending))
    # CASE 3: A new zip file is needed
    else:
        zip_dic = {}
        for reference in these_references:
            this_dir_base = os.path.dirname(reference.html_file.path)
            this_dir = os.path.join(os.path.dirname(this_dir_base), 'general_references')
            these_file_names = os.listdir(this_dir)
            for this_file_name in these_file_names:
                if this_file_name.split('.')[-1] != 'zip':
                    zip_dic[this_file_name] = os.path.join(this_dir, this_file_name)
        # CASE: No content
        if len(zip_dic) == 0:
            return HttpResponse('There is no content in this route')
        if not os.path.exists(os.path.dirname(zip_destination)):
            os.makedirs(os.path.dirname(zip_destination))
        zf = zipfile.ZipFile(zip_destination, "w")
        for zpath in zip_dic:
            if max_width:
                if zip_dic[zpath].split('.')[-1].lower() in ['jpg', 'png', 'gif']:
                    im = Image.open(zip_dic[zpath])
                    try:
                        im.thumbnail((int(max_width), int(max_width)), Image.ANTIALIAS)
                    except IOError:
                        im.thumbnail((int(max_width), int(max_width)), Image.NEAREST)
                    new_path = os.path.join(os.path.dirname(os.path.dirname(zip_dic[zpath])), 'general_references_max_width_' + str(max_width), zip_dic[zpath].split('/')[-1])
                    if not os.path.exists(os.path.dirname(new_path)):
                        os.makedirs(os.path.dirname(new_path))
                    im.save(new_path)
                    zip_dic[zpath] = new_path
            # Add file, at correct path
            zf.write(zip_dic[zpath], zpath)
        # Must close zip for all contents to be written
        zf.close()
        return HttpResponseRedirect(os.path.join(settings.CURRENT_DOMAIN, settings.MEDIA_URL, dest_ending))


def get_route_content_files(request, route_id, max_width=None, last_updated_unix_time_utc=0):
    last_updated = pytz.utc.localize(datetime.fromtimestamp(int(last_updated_unix_time_utc)))
    # CASE 0: Route does not exists: return message saying this
    if Route.objects.filter(id=route_id).count() == 0:
        return HttpResponse("Route does not exist")
    this_route = Route.objects.get(id=route_id)
    this_route_ref = None
    these_highlights = None
    these_references = None
    these_iis = None
    route_ref_lm = pytz.utc.localize(datetime.fromtimestamp(0))
    highlights_lm = pytz.utc.localize(datetime.fromtimestamp(0))
    references_lm = pytz.utc.localize(datetime.fromtimestamp(0))
    iis_lm = pytz.utc.localize(datetime.fromtimestamp(0))
    if this_route.reference:
        this_route_ref = this_route.reference
        route_ref_lm = this_route.reference.last_modified
    if this_route.track:
        these_steps = this_route.track.steps.all()
        if these_steps:
            these_highlights = Highlight.objects.filter(step__in=these_steps)
            if these_highlights:
                highlights_lm = these_highlights.aggregate(Max('last_modified'))['last_modified__max']
                these_references = Reference.objects.filter(highlight__in=these_highlights)
                if these_references:
                    references_lm = these_references.aggregate(Max('last_modified'))['last_modified__max']
                these_iis = InteractiveImage.objects.filter(highlight__in=these_highlights)
                if these_iis:
                    iis_lm = these_iis.aggregate(Max('last_modified'))['last_modified__max']
    # CASE 0.5: No objects other than route (therefore no content)
    if not this_route_ref and not these_highlights and not these_references and not these_iis:
        return HttpResponse('There is no content in this route')
    # CASE 1: no modifications since last update: return message saying this
    most_recent_modification_time = max(route_ref_lm, highlights_lm, references_lm, iis_lm)
    if most_recent_modification_time and last_updated >= most_recent_modification_time:
        return HttpResponse('There have been no changes since your last update')
    zip_subdir = "content_route_" + str(route_id) + "_max_width_" + str(max_width)
    zip_filename = "%s.zip" % zip_subdir
    dest_ending = 'holet/zipped_routes/' + zip_filename
    zip_destination = os.path.join(settings.MEDIA_ROOT, dest_ending)
    # CASE 2: there have been modifications, but there is already a zip file for the requested size and it was made after the most recent modification: return the existing zip file
    if os.path.isfile(zip_destination) and pytz.utc.localize(datetime.utcfromtimestamp(os.path.getmtime(zip_destination))) > most_recent_modification_time:
        return HttpResponseRedirect(os.path.join(settings.CURRENT_DOMAIN, settings.MEDIA_URL, dest_ending))
    # CASE 3: A new zip file is needed
    else:
        # dictionary in which keys are file names to be used in zip archive and values are file names on the server.
        zip_dic = {}
        base_dir = 'route_' + str(route_id) + '/'
        # all route reference files
        if this_route_ref and this_route_ref.html_file is not None:
            this_dir = os.path.dirname(this_route.reference.html_file.path)
            these_file_names = os.listdir(this_dir)
            for this_file_name in these_file_names:
                if this_file_name.split('.')[-1] != 'zip':
                    zip_dic[base_dir + 'route_reference/' + this_file_name] = os.path.join(this_dir, this_file_name)
        # highlight content
        for h in Highlight.objects.filter(step__in=these_steps):
            # highlight media
            if h.media:
                zip_dic[base_dir + 'highlight_' + str(h.id) + '/media/' + os.path.split(h.media.path)[-1]] = h.media.path
            # references
            for r in h.references.all():
                # all reference files
                this_dir = os.path.dirname(r.html_file.path)
                these_file_names = os.listdir(this_dir)
                for this_file_name in these_file_names:
                    if this_file_name.split('.')[-1] != 'zip':
                        zip_dic[base_dir + 'highlight_' + str(h.id) + '/reference_' + str(r.id) + '/' + this_file_name] = os.path.join(this_dir, this_file_name)
            # interactive images
            for i in h.interactive_images.all():
                if i.image_file:
                    zip_dic[base_dir + 'highlight_' + str(h.id) + '/interactive_image_' + str(i.id) + '/' + os.path.split(i.image_file.path)[-1]] = i.image_file.path
        # CASE: No content
        if len(zip_dic) == 0:
            return HttpResponse('There is no content in this route')
        if not os.path.exists(os.path.dirname(zip_destination)):
            os.makedirs(os.path.dirname(zip_destination))
        zf = zipfile.ZipFile(zip_destination, "w")
        for zpath in zip_dic:
            if max_width:
                if zip_dic[zpath].split('.')[-1].lower() in ['jpg', 'png', 'gif']:
                    im = Image.open(zip_dic[zpath])
                    # letting interactive images be up to twice the phone max dimension so they can pan.
                    if zpath.contains('interactive_image'):
                        max_dim = 2*max_width
                    else:
                        max_dim = max_width
                    try:
                        im.thumbnail((int(max_dim), int(max_dim)), Image.ANTIALIAS)
                    except IOError:
                        im.thumbnail((int(max_dim), int(max_dim)), Image.NEAREST)
                    new_path = os.path.join(os.path.dirname(os.path.dirname(zip_dic[zpath])), '_max_width_' + str(max_width), zip_dic[zpath].split('/')[-1])
                    if not os.path.exists(os.path.dirname(new_path)):
                        os.makedirs(os.path.dirname(new_path))
                    im.save(new_path)
                    zip_dic[zpath] = new_path
            # Add file, at correct path
            zf.write(zip_dic[zpath], zpath)
        # Must close zip for all contents to be written
        zf.close()
        # Grab ZIP file from in-memory, make response with correct MIME-type
        # resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        # ..and correct content-disposition
        # resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        #resp['Content-Length'] = str(size)
        # return resp
        return HttpResponseRedirect(os.path.join(settings.CURRENT_DOMAIN, settings.MEDIA_URL, dest_ending))


@api_view(['POST'])
def post_media(request):
    """
API endpoint for uploading media associated with a highlight. Data must be posted as multipart form,
with with _media_ used as the form key for the file itself.

**Fields**

* media: The media file's binary data
* id: The id of the highlight.
* created_by: The user id who created this highlight.
* name_x: The name of the highlight in language specified by language code x where x = oc, es, ca, fr, or en.
* long_text_x: Text that should be displayed with the highlight in language specified by language code x where x = oc, es, ca, fr, or en..
* radius: Radius, in meters on the ground, that the highlight covers.
* type: Type of highlight.

    """
    if request.method == 'POST':
        instance = Highlight(media=request.FILES['media'], id=request.DATA['id'], created_by=request.DATA['created_by'], name_oc=request.DATA['name_oc'], name_es=request.DATA['name_es'], name_ca=request.DATA['name_ca'], name_fr=request.DATA['name_fr'], name_en=request.DATA['name_en'], long_text_oc=request.DATA['long_text_oc'], long_text_es=request.DATA['long_text_es'], long_text_ca=request.DATA['long_text_ca'], long_text_fr=request.DATA['long_text_fr'], long_text_en=request.DATA['long_text_en'], radius=request.DATA['radius'], type=request.DATA['type'])
        instance.save()
        return Response('uploaded')


class MapViewSet(ReadOnlyModelViewSet):
    queryset = Map.objects.all()
    serializer_class = MapSerializer
    filter_fields = 'id'


class HighlightViewSet(ReadWriteOnlyModelViewSet):
    queryset = Highlight.objects.all()
    serializer_class = HighlightSerializer
    filter_fields = ('id', 'created_by')


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


class RouteViewSet(ReadOnlyModelViewSet):
    queryset = Route.objects.filter(official=True)
    serializer_class = RouteSerializer
    filter_fields = ('id', 'created_by')


class RouteNestedViewSet(ReadOnlyModelViewSet):
    queryset = Route.objects.filter(official=True)
    serializer_class = RouteNestedSerializer
    filter_fields = ('id', 'created_by')


class StepViewSet(ReadWriteOnlyModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_default_renderer(self, view):
        return JSONRenderer()

