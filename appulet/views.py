import os
import zipfile
from rest_framework import viewsets
from rest_framework.generics import mixins
from django.http import HttpResponse, HttpResponseRedirect
from appulet.serializers import *
from appulet.models import *
from PIL import Image
from django.conf import settings
from datetime import datetime
import pytz
from django.db.models import Max
from appulet.permissions import IsOwnerOrNothing, IsUserOwnerOrNothing
from rest_framework.decorators import api_view
from rest_framework.response import Response
import django_filters
from django.shortcuts import render
import markdown


class ReadOnlyModelViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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


class ReadWriteOnlyModelViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    A viewset that provides `retrieve`, 'list`, and `create` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass


def show_file_download_endpoint(request, view):
    context = {}
    context['title'] = string.capwords(" ".join(view.split("_")))
    context['help_text'] = markdown.markdown(eval(view).__doc__)
    return render(request, 'rest_framework/file_download_endpoints.html', context)


def get_route_map(request, route_id, last_updated_unix_time_utc=0):
    """
Endpoint for downloading route maps.

**Usage**

    /api/route_map/<route_id>/

    /api/route_map/<route_id>/<modified_since>/

**Parameters**

* route_id: server_id of the route whose map you are requesting
* modified_since: Optional. If there have been no modifications to the map since the entered time, the server will return an HTML response indicating this (and no file will be sent). This time should be entered as a Unix time integer -- i.e., number of seconds since 1 January 1970 UTC.

**Examples**

* [/api/route_map/9/](/api/route_map/9/)

* [/api/route_map/9/1416250115/](/api/route_map/9/1416250115/)
    """
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
    """
Endpoint for downloading the general map used for the app's itinerary selection activity.

**Usage**

    /api/general_map/

    /api/general_map/<modified_since>/

**Parameters**

* modified_since: Optional. If there have been no modifications to the map since the entered time, the server will return an HTML response indicating this (and no file will be sent). This time should be entered as a Unix time integer -- i.e., number of seconds since 1 January 1970 UTC.

**Examples**

* [/api/general_map/](/api/general_map/)

* [/api/general_map/1416250115/](/api/general_map/1416250115/)
    """

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
    """
Endpoint for downloading the general references displayed in the app as html.

**Usage**

    /api/general_references/

    /api/general_references/<max_width>/

    /api/general_references/<max_width>/<modified_since>/

**Parameters**

* max_width: Optional. This will ensure that all image and video files returned as part of this reference will not exceed this width. The idea is that you should pass the width of the user's device, and thereby ensure that the user receives the smallest necessary files. Should be entered as an integer representing the number of pixels.
* modified_since: Optional. If there have been no modifications to the reference since the entered time, the server will return an HTML response indicating this (and no file will be sent). This time should be entered as a Unix time integer -- i.e., number of seconds since 1 January 1970 UTC.

**Examples**

[/api/general_references/](/api/general_references/)

[/api/general_references/400/](/api/general_references/400/)

[/api/general_references/400/1416250115/](/api/general_references/400/1416250115/)
    """

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
    """
Endpoint for downloading all content files needed for a given route.

**Usage**

    /api/route_content/<route_id>/

    /api/route_content/<route_id>/<max_width>/

    /api/route_content/<route_id>/<max_width>/<modified_since>/

**Parameters**

* route_id: server_id of the route whose content you are requesting
* max_width: Optional. This will ensure that all image and video files returned as part of this reference will not exceed this width. The idea is that you should pass the width of the user's device, and thereby ensure that the user receives the smallest necessary files. Should be entered as an integer representing the number of pixels.
* modified_since: Optional. If there have been no modifications to the content since the entered time, the server will return an HTML response indicating this (and no file will be sent). This time should be entered as a Unix time integer -- i.e., number of seconds since 1 January 1970 UTC.

**Examples**

[/api/route_content/9/](/api/route_content/9/)

[/api/route_content/9/400/](/api/route_content/9/400/)

[/api/route_content/9/400/1416250115/](/api/route_content/9/400/1416250115/)
    """

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
                    if 'interactive_image' in zpath:
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


def filter_last_modified_unix_dt(queryset, value):
    if not value:
        return queryset

    try:
        unix_time = int(value)
        t = datetime.fromtimestamp(unix_time)
        result = queryset.filter(last_modified__gt=t)
        return result
    except ValueError:
        return queryset


class MapFilter(django_filters.FilterSet):
    modified_since = django_filters.Filter(action=filter_last_modified_unix_dt)

    class Meta:
        model = Map
        fields = ['modified_since']


class MapViewSet(ReadOnlyModelViewSet):
    queryset = Map.objects.all()
    serializer_class = MapSerializer
    filter_class = MapFilter


class HighlightFilter(django_filters.FilterSet):
    modified_since = django_filters.Filter(action=filter_last_modified_unix_dt)

    class Meta:
        model = Highlight
        fields = ['modified_since']


class HighlightViewSet(ReadOnlyModelViewSet):
    queryset = Highlight.objects.filter(step__track__route__official=True)
    serializer_class = HighlightSerializer
    filter_class = HighlightFilter


class UserHighlightViewSet(viewsets.ModelViewSet):
    queryset = Highlight.objects.all()
    serializer_class = UserHighlightSerializer
    filter_class = HighlightFilter
    permission_classes = (IsOwnerOrNothing,)

    def pre_save(self, obj):
        obj.created_by = self.request.user

    def get_queryset(self):
        return self.request.user.highlights.all()


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


class RouteFilter(django_filters.FilterSet):
    modified_since = django_filters.Filter(action=filter_last_modified_unix_dt)

    class Meta:
        model = Route
        fields = ['modified_since']


class RouteViewSet(ReadOnlyModelViewSet):
    """
    API endpoint for getting Holet's routes. These are the routes created by the Holet team for users to follow, and they cannot be changed by users, so only GET requests are allowed here.

    **Fields**

    * owner: username of the user who created this route.
    * server_id: unique integer id assigned to the route by the server.
    * official: bolean that is true if route was created by Holet team, and false otherwise.
    * last_modified: Date and time when route was last modified. Formatted as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
    *  created_by: User id of the user who created this route.

    **Usage**

        /api/routes/

        /api/routes/<route_id>/

        /api/routes/<route_id>/?modified_since=<modified_since>

    **Parameters**

    * route_id: Optional. Server_id of an individual route to be viewed.
    * modified_since: Optional. Return list of only those routes that have been modified after this time. This time should be entered as a Unix time integer -- i.e., number of seconds since 1 January 1970 UTC.

    **Example**

    *list of all routes*: [/api/routes/](/api/routes/)

    *individual route detail:* [/api/routes/9/](/api/routes/9/)

    *individual route detail with time cutoff:* [/api/routes/9/?modified_since=1416258566](/api/routes/9/?modified_since=1416258566)

    """
    queryset = Route.objects.filter(official=True)
    serializer_class = RouteSerializer
    filter_class = RouteFilter


class UserRouteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for GET and POST requests to a user's routes. The only routes that can be accessed here are those created by the authenticated user. Note that while POST requests are possible with this endpoint, it is intended more for simply listing all of the routes of a given user. It makes more sense to do POST requests to the user's nested routes, where all writable fields are visible.

    **Fields**

    * owner: username of the user who created this route.
    * server_id: unique integer id assigned to the route by the server.
    * official: boolean that is true if route was created by Holet team, and falase otherwise.
    * last_modified: Date and time when route was last modified. Formatted as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
    *  created_by: User id of the user who created this route.

    **Usage**

        /api/my_routes/

        /api/my_routes/<route_id>/

        /api/my_routes/<route_id>/?modified_since=<modified_since>

    **Parameters**

    * route_id: Optional. Server_id of an individual route to be viewed.
    * modified_since: Optional. Return list of only those routes that have been modified after this time. This time should be entered as a Unix time integer -- i.e., number of seconds since 1 January 1970 UTC.

    **Example**

    *list of all routes created by current user*: [/api/my_routes/](/api/my_routes/)

    *individual route detail:* [/api/my_routes/9/](/api/my_routes/9/)

    *individual route detail with time cutoff:* [/api/my_routes/9/?modified_since=1416258566](/api/my_routes/9/?modified_since=1416258566)


    """
    queryset = Route.objects.filter(official=False)
    serializer_class = RouteSerializer
    filter_class = RouteFilter
    permission_classes = (IsOwnerOrNothing,)

    def get_queryset(self):
        return self.request.user.routes.all()


class RouteNestedViewSet(ReadOnlyModelViewSet):
    """
    API endpoint for getting Holet's routes, including all nested data models. These are the routes created by the Holet team for users to follow, and they cannot be changed by users, so only GET requests are allowed here.

    **Fields**

    * owner: username of the user who created this route.
    * server_id: unique integer id assigned to the route by the server.
    * official: boolean that is true if route was created by Holet team, and falase otherwise.
    * last_modified: Date and time when route was last modified. Formatted as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
    * created: Date and time when route was created. Formatted as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
    * created_by: User id of the user who created this route.
    * average_rating: the average rating users have given this route (calculated from rating model)
    * total_ratings: total number of ratings on which the average is based.
    * id_route_based_on: server id of the route the present route is based on. This field should generally be filled only for user routes: it represents the route the user was following when recording a given other route.
    * description_oc: route description in Aranese.
    * description_es: route description in Spanish.
    * description_ca: route description in Catalan.
    * description_fr: route description in French.
    * description_en: route description in English
    * short_description_oc: route's short description in Aranese. (This is primarily used for displaying the route on the webside, and it will often be blank).
    * short_description_es: route's short description in Spanish. (This is primarily used for displaying the route on the webside, and it will often be blank)
    * short_description_ca: route's short description in Catalan. (This is primarily used for displaying the route on the webside, and it will often be blank)
    * short_description_fr: route's short description in Frensh. (This is primarily used for displaying the route on the webside, and it will often be blank)
    * short_description_en: route's short description in English. (This is primarily used for displaying the route on the webside, and it will often be blank)
    * name_oc: route name in Aranese
    * name_es: route name in Spanish
    * name_ca: route name in Catalan
    * name_fr: route name in Frensh
    * name_en: route_name, in Englih
    * reference: nested fields for up to 1 reference.
        * server_id: unique integer ID assigned to the reference by the server
        * name_oc: reference name in Aranese
        * name_es: reference name in Spanish
        * name_ca: reference name in Catalan
        * name_fr: reference name in French
        * name_en: reference name in English
        * html_file: path on server to the zip file containing the reference's html file and associated resources
        * last_modified: Date and time when reference was last modified. Formatted as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
        * created: Date and time when reference was created. Formatted as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
    * top_five_user_highlights: nested array of up to 5 highlights. These are highlights saved by users, with the top five selected based on highest average ratings
    * map: nested fields for the route map
        * last_modified: Date and time when map was last modified. Formated as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
        * created: Date and time when map was created. Formatted as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
        * map_file_name: file name of map file on server.
    * track: nested fields for track associated with this route. (Note that the track is a largely redundant data structure at this point. There is a one-to-one relationship between trakc and route, but it is the track that contains all os the steps.
        * server_id: unique integer ID assigned to the track by the server
        * name_oc: track name in Aranese. (This is irrelevant and can be ignored.)
        * name_es: track name in Spanish. (This is irrelevant and can be ignored.)
        * name_ca: track name in Catalan. (This is irrelevant and can be ignored.)
        * name_fr: track name in French. (This is irrelevant and can be ignored.)
        * name_en: track name in English. (This is irrelevant and can be ignored.)
        * last_modified: Date and time when track was last modified. Formatted as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
        * steps: Array of steps associated with the track
            * server_id: unique integer ID assigned to the step by the server
            * absolute_time: Date and time when step was recorded. Formatted as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),,
            * order: integer indicating order of the step within the track. (This is necessary for non-highlight steps, to ensure path is drawn correctly.)
            * latitude: float latitude of the step location
            * longitude: float longitude of the step location
            * altitude: float altitude of the step location
            * precision: float precision of the step location estimate
            * last_modified: Date and time when step was last modified. Formated as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
            * highlights: array of highlights associated with this step
                * server_id: unique integer ID assigned to the highlight by the server
                * average_rating: average user rating for this highlight (calculated on server from the rating data)
                * total_ratings: total ratings for this highlight (calculated on server from rating data)
                * created_by: server ID of the user who created this highlight,
                * name_oc: highlight name in Aranese
                * name_es: wpV02-inici pista Varrad\u00f2s,
                * name_ca: wpV02-inici pista Varrad\u00f2s,
                * name_fr: wpV02-inici pista Varrad\u00f2s,
                * name_en: wpV02-inici pista Varrad\u00f2s,
                * long_text_oc: ,
                * long_text_es: ,
                * long_text_ca: ,
                * long_text_fr: ,
                * long_text_en: ,
                * radius: null,
                * type: 1,
                * interactive_images: [],
                * references: [],
                * media_name: ,
                * last_modified: 2014-10-11T00:00:00Z



    **Usage**

        /api/nested_routes/

        /api/nested_routes/<route_id>/

    **Example**

    *list of all routes*: [/api/nested_routes/](/api/nested_routes/)

    *individual route detail:* [/api/nested_routes/9/](/api/nested_routes/9/)


    """
    queryset = Route.objects.filter(official=True)
    serializer_class = RouteNestedSerializer
    filter_class = RouteFilter


class UserRouteNestedViewSet(viewsets.ModelViewSet):
    """
    API endpoint for getting Holet's routes. These are the routes created by the Holet team for users to follow, and they cannot be changed by users, so only GET requests are allowed here.

    **Fields**

    * owner: username of the user who created this route.
    * server_id: unique integer id assigned to the route by the server.
    * official: bolean that is true if route was created by Holet team, and falase otherwise.
    * last_modified: Date and time when route was last modified. Formated as [ECMA 262](http://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15) date time string (e.g. "2014-11-11T15:16:49.854Z"),
    *  created_by": User id of the user who created this route.

    **Usage**

        /api/nested_routes/

        /api/nested_routes/<route_id>/

    **Example**

    *list of all routes*: [/api/nested_routes/](/api/nested_routes/)

    *individual route detail:* [/api/nested_routes/9/](/api/nested_routes/9/)


    """
    queryset = Route.objects.filter(official=False)
    serializer_class = RouteNestedSerializer
    filter_class = RouteFilter
    permission_classes = (IsOwnerOrNothing,)

    def get_queryset(self):
        return self.request.user.routes.all()


class StepFilter(django_filters.FilterSet):
    modified_since = django_filters.Filter(action=filter_last_modified_unix_dt)

    class Meta:
        model = Step
        fields = ['modified_since']


class StepViewSet(ReadWriteOnlyModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    filter_class = StepFilter


class UserStepNestedViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = UserStepNestedSerializer
    permission_classes = (IsOwnerOrNothing,)
    filter_class = StepFilter

    def get_queryset(self):
        return Step.objects.filter(track__route__created_by=self.request.user)


class RatingFilter(django_filters.FilterSet):
    modified_since = django_filters.Filter(action=filter_last_modified_unix_dt)

    class Meta:
        model = Rating
        fields = ['modified_since']


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    filter_class = RatingFilter


class UserRatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = (IsUserOwnerOrNothing,)
    filter_class = RatingFilter

    def pre_save(self, obj):
        obj.user = self.request.user

    def get_queryset(self):
        return self.request.user.ratings.all()


