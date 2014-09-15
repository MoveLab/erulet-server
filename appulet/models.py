from django.db import models
import uuid
import os
import os.path
from django.contrib.auth.models import User


class Track(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    name = models.CharField(max_length=200, default='unnamed track')

    def __unicode__(self):
        return self.name


def make_media_uuid(path):
    def wrapper(instance, filename):
        extension = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), extension)
        return os.path.join(path, filename)
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


class InteractiveImage(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    image_file = models.ImageField(upload_to=make_media_uuid('erulet/interactive_images'))
    original_height = models.IntegerField()
    original_width = models.IntegerField()
    step = models.ForeignKey(Step, blank=True, null=True)


class Box(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    interactive_image = models.ForeignKey(InteractiveImage)
    message = models.TextField()
    max_y = models.IntegerField()
    max_x = models.IntegerField()
    min_y = models.IntegerField()
    min_x = models.IntegerField()

    class Meta:
        verbose_name = "box"
        verbose_name_plural = "boxes"


class Reference(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    name = models.CharField(max_length=200, default='unnamed reference')
    content = models.FileField(upload_to=make_media_uuid('erulet/references'))


def gpx_tracks(instance, filename):
    return "erulet/gpx_tracks/%s.gpx" % uuid.uuid4()


def gpx_waypoints(instance, filename):
    return "erulet/gpx_waypoints/%s.gpx" % uuid.uuid4()


def gpx_pois(instance, filename):
    return "erulet/gpx_pois/%s.gpx" % uuid.uuid4()


class Route(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
   # id_route_based_on = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, blank=True, null=True)
    description = models.TextField(blank=True)
    interactive_image = models.OneToOneField(InteractiveImage, blank=True, null=True)
    local_carto = models.FileField(upload_to=make_media_uuid('erulet/carto'), blank=True, null=True)
    name = models.CharField(max_length=200, default='unnamed route')
    reference = models.OneToOneField(Reference, blank=True, null=True)
    track = models.OneToOneField(Track, blank=True, null=True)
    upload_time = models.DateTimeField(blank=True, null=True)
    gpx_track = models.FileField("GPX Track", upload_to=gpx_tracks, blank=True)
    gpx_waypoints = models.FileField("GPX Waypoints", upload_to=gpx_waypoints, blank=True)
    gpx_pois = models.FileField("GPX Points-of-interest", upload_to=gpx_pois, blank=True)

    def __unicode__(self):
        return self.name


class Highlight(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    long_text = models.CharField(max_length=2000, blank=True)
    media = models.FileField(upload_to=make_media_uuid('erulet_highlights'), blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)
    type = models.IntegerField()
    step = models.ForeignKey(Step, blank=True, null=True)


class Rating(models.Model):
    rating = models.IntegerField()
    user = models.ForeignKey(User)
    time = models.DateTimeField()
    highlight = models.ForeignKey(Highlight, blank=True, null=True)
    route = models.ForeignKey(Route, blank=True, null=True)
