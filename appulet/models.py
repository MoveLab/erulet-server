from django.db import models
import uuid
import os
import os.path
from django.contrib.auth.models import User
from PIL import Image
import datetime
from math import floor
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _


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


class InteractiveImage(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    image_file = models.ImageField(upload_to=make_media_uuid('erulet_interactive_images'))
    original_height = models.IntegerField()
    original_width = models.IntegerField()


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
    content = models.FileField(upload_to=make_media_uuid('erulet_references'))


class Route(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    id_route_based_on = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, blank=True, null=True)
    description = models.TextField(blank=True)
    interactive_image = models.OneToOneField(InteractiveImage, blank=True, null=True)
    local_carto = models.FileField(upload_to=make_media_uuid('erulet_carto'), blank=True, null=True)
    name = models.CharField(max_length=200, default='unnamed route')
    reference = models.OneToOneField(Reference, blank=True, null=True)
    track = models.OneToOneField(Track, blank=True, null=True)
    upload_time = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Step(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    absolute_time = models.DateTimeField(blank=True, null=True)
    track = models.ForeignKey(Track, blank=True, null=True, related_name='steps')
    route = models.ForeignKey(Route, blank=True, null=True)
    reference = models.OneToOneField(Reference, blank=True, null=True)
    interactive_image = models.OneToOneField(InteractiveImage, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(blank=True, null=True)
    precision = models.FloatField(blank=True, null=True)


class Highlight(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=100, default='unnamed highlight')
    long_text = models.CharField(max_length=2000, blank=True)
    media = models.FileField(upload_to=make_media_uuid('erulet_highlights'), blank=True, null=True)
    radius = models.FloatField()
    type = models.IntegerField()
    step = models.OneToOneField(Step)


class Rating(models.Model):
    rating = models.IntegerField()
    user = models.ForeignKey(User)
    time = models.DateTimeField()
    highlight = models.ForeignKey(Highlight, blank=True, null=True)
    route = models.ForeignKey(Route, blank=True, null=True)


def GPX_Folder(instance, filename):
    return "uploaded_gpx_files/%s" % (filename)


class gpxFile(models.Model):
    title = models.CharField("Title", max_length=100)
    gpx_file = models.FileField(upload_to=GPX_Folder, blank=True)

    def __unicode__(self):
        return self.title