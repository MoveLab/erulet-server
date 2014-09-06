from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import mixins
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.db.models import Q
from serializers import *
from models import *
import os
import zipfile
import StringIO
from django.http import HttpResponse


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


class BoxViewSet(ReadOnlyModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class ReferenceViewSet(ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class RouteViewSet(ReadWriteOnlyModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class StepViewSet(ReadWriteOnlyModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_default_renderer(self, view):
        return JSONRenderer()


