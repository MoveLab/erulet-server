from django.db import models
import uuid
import os
import os.path
from django.contrib.auth.models import User
import string
from django.conf import settings
import codecs


class Track(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        this_name = 'unnamed track'
        if self.name is not None and self.name != '':
            this_name = self.name
        return this_name


def make_media_uuid(path):
    def wrapper(instance, filename):
        extension = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), extension)
        new_path = os.path.join(path, str(instance.id))
        return os.path.join(new_path, filename)
    return wrapper


def make_reference_image_uuid(path):
    def wrapper(instance, filename):
        return os.path.join(path, str(instance.highlight.id), filename)
    return wrapper


class Step(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    absolute_time = models.DateTimeField(blank=True, null=True)
    track = models.ForeignKey(Track, blank=True, null=True, related_name='steps')
    order = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(blank=True, null=True)
    precision = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        this_name = 'step ' + str(self.id)
        if self.track is not None:
            this_name += ' of route ' + self.track.route.name
        return this_name


class Reference(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    name = models.CharField(max_length=200, default='unnamed reference')
    html_file = models.FileField('ZIP file', upload_to=make_media_uuid('erulet/references'))
    highlight = models.ForeignKey('Highlight', blank=True, null=True,related_name='references')

    def __unicode__(self):
        this_name = 'unnamed reference'
        if self.name is not None and self.name != '':
            this_name = self.name
        return this_name

    def find_reference_url(self):
        temp = str.split(self.html_file.url, '/')
        if len(temp) > 1:
            temp.pop(-1)
            temp.append('reference.html')
        return settings.CURRENT_DOMAIN + string.join(temp, '/')

    def find_reference_url_base(self):
        temp = str.split(self.html_file.url, '/')
        if len(temp) > 1:
            temp.pop(-1)
        return settings.CURRENT_DOMAIN + string.join(temp, '/')

    def find_reference_path(self):
        if self.html_file.name:
            return os.path.join(os.path.dirname(self.html_file.path), 'reference.html')
        else:
            return ''

    def get_reference_html(self):
        reference_html_raw = ''
        if os.path.isfile(self.find_reference_path()):
            ref_file = codecs.open(self.find_reference_path(), 'r', 'iso-8859-1')
            reference_html_raw = ref_file.read()
            ref_file.close()
        return reference_html_raw

    reference_url = property(find_reference_url)
    reference_url_base = property(find_reference_url_base)
    reference_path = property(find_reference_path)
    reference_html = property(get_reference_html)


class ReferenceImage(models.Model):
    reference = models.ForeignKey(Reference)
    image = models.ImageField(upload_to=make_reference_image_uuid('erulet/references/'))


def gpx_tracks(instance, filename):
    return "erulet/gpx_tracks/%s.gpx" % uuid.uuid4()


def gpx_waypoints(instance, filename):
    return "erulet/gpx_waypoints/%s.gpx" % uuid.uuid4()


def gpx_pois(instance, filename):
    return "erulet/gpx_pois/%s.gpx" % uuid.uuid4()


class Route(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    id_route_based_on = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='routes')
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=100, blank=True)
    local_carto = models.FileField(upload_to=make_media_uuid('erulet/carto'), blank=True, null=True)
    name = models.CharField(max_length=200)
    reference = models.OneToOneField(Reference, blank=True, null=True)
    track = models.OneToOneField(Track, blank=True, null=True)
    upload_time = models.DateTimeField(blank=True, null=True)
    gpx_track = models.FileField("GPX Track", upload_to=gpx_tracks, blank=True)
    gpx_waypoints = models.FileField("GPX Waypoints", upload_to=gpx_waypoints, blank=True)
    gpx_pois = models.FileField("GPX Points-of-interest", upload_to=gpx_pois, blank=True)
    official = models.BooleanField("Official Route", default=False)

    def __unicode__(self):
        this_name = 'unnamed route'
        if self.name is not None and self.name != '':
            this_name = self.name
        return this_name


class Highlight(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='highlights')
    name = models.CharField(max_length=100, blank=True)
    long_text = models.CharField(max_length=2000, blank=True)
    media = models.FileField(upload_to=make_media_uuid('erulet/highlights'), blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)
    TYPE_CHOICES = ((0, 'point of interest'), (1, 'waypoint'),)
    type = models.IntegerField(choices=TYPE_CHOICES)
    step = models.ForeignKey(Step, blank=True, null=True, related_name='highlights')
    order = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        this_name = 'unnamed highlight'
        if self.name is not None and self.name != '':
            this_name = self.name
        return this_name

    def test_image(self):
        if self.media is not None:
            image_extensions = ['jpg', 'png', 'gif', 'tif']
            ext = self.media.name.split('.')[-1]
            return ext in image_extensions
        else:
            return False

    def get_media_ext(self):
        ext = ''
        if self.media is not None:
            ext = self.media.name.split('.')[-1]
        return ext

    image = property(test_image)
    media_ext = property(get_media_ext)


class InteractiveImage(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    image_file = models.ImageField(upload_to=make_media_uuid('erulet/interactive_images'))
    original_height = models.IntegerField()
    original_width = models.IntegerField()
    highlight = models.ForeignKey(Highlight, blank=True, null=True, related_name='interactive_images')

    def __unicode__(self):
        this_name = 'unlinked interactive image'
        if self.step is not None:
            this_name = 'interactive image for step ' + str(self.step.id) + ' of route ' + self.step.track.route.name
        return this_name


class Box(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    interactive_image = models.ForeignKey(InteractiveImage, related_name='boxes')
    message = models.TextField()
    max_y = models.IntegerField()
    max_x = models.IntegerField()
    min_y = models.IntegerField()
    min_x = models.IntegerField()

    class Meta:
        verbose_name = "box"
        verbose_name_plural = "boxes"

    def __unicode__(self):
        return self.id


class Rating(models.Model):
    rating = models.IntegerField()
    user = models.ForeignKey(User, related_name='ratings')
    time = models.DateTimeField()
    highlight = models.ForeignKey(Highlight, blank=True, null=True)
    route = models.ForeignKey(Route, blank=True, null=True, related_name='ratings')

    def __unicode__(self):
        this_name = 'Rating ' + self.id
        if self.highlight is not None:
            this_name = 'Rating for highlight: ' + self.highlight.name
        elif self.route is not None:
            this_name = 'Rating for route: ' + self.route.name
        return this_name
