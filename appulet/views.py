import os
import zipfile
import StringIO
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import mixins
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.http import HttpResponse
from appulet.serializers import *
from appulet.models import *


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


def get_route_content_files(request, route_id):
    zip_dic = {}
    this_route = Route.objects.get(id=route_id)
    these_steps = this_route.track.steps.all()
    # all route reference files
    if this_route.reference.html_file is not None:
        this_dir = os.path.dirname(this_route.reference.html_file.path)
        these_file_names = os.listdir(this_dir)
        for this_file_name in these_file_names:
            if this_file_name.split('.')[-1] != 'zip':
                zip_dic['route_reference/' + this_file_name] = os.path.join(this_dir, this_file_name)
    # highlight content
    for h in Highlight.objects.filter(step__in=these_steps):
        # highlight media
        if h.media:
            zip_dic['highlight_' + str(h.id) + '/media/' + os.path.split(h.media.path)[-1]] = h.media.path
        # references
        for r in h.references.all():
            # all reference files
            this_dir = os.path.dirname(r.html_file.path)
            these_file_names = os.listdir(this_dir)
            for this_file_name in these_file_names:
                if this_file_name.split('.')[-1] != 'zip':
                    zip_dic['highlight_' + str(h.id) + '/reference_' + str(r.id) + '/' + this_file_name] = os.path.join(this_dir, this_file_name)
        # interactive images
        for i in h.interactive_images.all():
            if i.image_file:
                zip_dic['highlight_' + str(h.id) + '/interactive_image_' + str(i.id) + '/' + os.path.split(i.image_file.path)[-1]] = i.image_file.path
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    zip_subdir = "content_route" + str(route_id)
    zip_filename = "%s.zip" % zip_subdir
    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()
    # The zip compressor
    zf = zipfile.ZipFile(s, "w")
    for zpath in zip_dic:
        # Add file, at correct path
        zf.write(zip_dic[zpath], zpath)
    # Must close zip for all contents to be written
    zf.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), mimetype="application/x-zip-compressed")
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
* name_x: The name of the highlight in language specified by language code x where x = oc, es, ca, fr, or en.
* long_text_x: Text that should be displayed with the highlight in language specified by language code x where x = oc, es, ca, fr, or en..
* radius: Radius, in meters on the ground, that the highlight covers.
* type: Type of highlight.

    """
    if request.method == 'POST':
        instance = Highlight(media=request.FILES['media'], id=request.DATA['id'], created_by=request.DATA['created_by'], name_oc=request.DATA['name_oc'], name_es=request.DATA['name_es'], name_ca=request.DATA['name_ca'], name_fr=request.DATA['name_fr'], name_en=request.DATA['name_en'], long_text_oc=request.DATA['long_text_oc'], long_text_es=request.DATA['long_text_es'], long_text_ca=request.DATA['long_text_ca'], long_text_fr=request.DATA['long_text_fr'], long_text_en=request.DATA['long_text_en'], radius=request.DATA['radius'], type=request.DATA['type'])
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

