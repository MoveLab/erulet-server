from django.db import models
import uuid
import os
import os.path
from django.contrib.auth.models import User
import string
from django.conf import settings
import codecs
from PIL import Image


class Track(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    name_oc = models.CharField(max_length=200, blank=True)
    name_es = models.CharField(max_length=200, blank=True)
    name_ca = models.CharField(max_length=200, blank=True)
    name_fr = models.CharField(max_length=200, blank=True)
    name_en = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        names = [self.name_oc, self.name_es, self.name_ca, self.name_fr, self.name_en]
        for name in names:
            if name is not None:
                return name
        return str(self.id)

    def get_name(self, lang='oc'):
        lang_names_dict = {'oc': self.name_oc, 'es': self.name_es, 'ca': self.name_ca, 'fr': self.name_fr, 'en': self.name_en}
        if lang_names_dict[lang] is not None:
            return lang_names_dict[lang]
        for name in lang_names_dict.values():
            if name is not None:
                return name
        return str(self.id)


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
        return str(uuid)


def filenamei18(base, lang='oc'):
    bs = base.split('.')
    return bs[0] + '_' + lang + '.' + bs[1]


class Reference(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    name_oc = models.CharField(max_length=200, blank=True)
    name_es = models.CharField(max_length=200, blank=True)
    name_ca = models.CharField(max_length=200, blank=True)
    name_fr = models.CharField(max_length=200, blank=True)
    name_en = models.CharField(max_length=200, blank=True)
    html_file = models.FileField('ZIP file', upload_to=make_media_uuid('erulet/references'))
    highlight = models.ForeignKey('Highlight', blank=True, null=True, related_name='references')

    def __unicode__(self):
        names = [self.name_oc, self.name_es, self.name_ca, self.name_fr, self.name_en]
        for name in names:
            if name is not None:
                return name
        return str(self.id)

    def get_name(self, lang='oc'):
        lang_names_dict = {'oc': self.name_oc, 'es': self.name_es, 'ca': self.name_ca, 'fr': self.name_fr, 'en': self.name_en}
        if lang_names_dict[lang] is not None:
            return lang_names_dict[lang]
        for name in lang_names_dict.values():
            if name is not None:
                return name
        return str(self.id)

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

    def find_reference_path(self, lang='oc'):
        if self.html_file.name:
            this_filename = filenamei18('reference.html', lang)
            if os.path.isfile(os.path.join(os.path.dirname(self.html_file.path), this_filename)):
                return os.path.join(os.path.dirname(self.html_file.path), this_filename)
            else:
                for l in filter(lambda x: x != lang, settings.LANGUAGES):
                    this_filename = filenamei18('reference.html', l[0])
                    if os.path.isfile(os.path.join(os.path.dirname(self.html_file.path), this_filename)):
                        return os.path.join(os.path.dirname(self.html_file.path), this_filename)
                return None

    def get_reference_html(self, lang='oc'):
        reference_html_raw = ''
        if os.path.isfile(self.find_reference_path(lang)):
            ref_file = codecs.open(self.find_reference_path(), 'r', 'iso-8859-1')
            reference_html_raw = ref_file.read()
            ref_file.close()
        return reference_html_raw

    reference_url = property(find_reference_url)
    reference_url_base = property(find_reference_url_base)


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
    description_oc = models.TextField(blank=True)
    description_es = models.TextField(blank=True)
    description_ca = models.TextField(blank=True)
    description_fr = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    short_description_oc = models.CharField(max_length=100, blank=True)
    short_description_es = models.CharField(max_length=100, blank=True)
    short_description_ca = models.CharField(max_length=100, blank=True)
    short_description_fr = models.CharField(max_length=100, blank=True)
    short_description_en = models.CharField(max_length=100, blank=True)
    local_carto = models.FileField(upload_to=make_media_uuid('erulet/carto'), blank=True, null=True)
    name_oc = models.CharField(max_length=200)
    name_es = models.CharField(max_length=200)
    name_ca = models.CharField(max_length=200)
    name_fr = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    reference = models.OneToOneField(Reference, blank=True, null=True)
    track = models.OneToOneField(Track, blank=True, null=True)
    upload_time = models.DateTimeField(blank=True, null=True)
    gpx_track = models.FileField("GPX Track", upload_to=gpx_tracks, blank=True)
    gpx_waypoints = models.FileField("GPX Waypoints", upload_to=gpx_waypoints, blank=True)
    gpx_pois = models.FileField("GPX Points-of-interest", upload_to=gpx_pois, blank=True)
    official = models.BooleanField("Official Route", default=False)

    def __unicode__(self):
        names = [self.name_oc, self.name_es, self.name_ca, self.name_fr, self.name_en]
        for name in names:
            if name is not None:
                return name
        return str(self.id)

    def get_name(self, lang='oc'):
        lang_names_dict = {'oc': self.name_oc, 'es': self.name_es, 'ca': self.name_ca, 'fr': self.name_fr, 'en': self.name_en}
        if lang_names_dict[lang] is not None:
            return lang_names_dict[lang]
        for name in lang_names_dict.values():
            if name is not None:
                return name
        return str(self.id)

    def get_description(self, lang='oc'):
        lang_description_dict = {'oc': self.description_oc, 'es': self.description_es, 'ca': self.description_ca, 'fr': self.description_fr, 'en': self.description_en}
        if lang_description_dict[lang] is not None:
            return lang_description_dict[lang]
        for x in lang_description_dict.values():
            if x is not None:
                return x
        return None

    def get_short_description(self, lang='oc'):
        lang_short_description_dict = {'oc': self.short_description_oc, 'es': self.short_description_es, 'ca': self.short_description_ca, 'fr': self.short_description_fr, 'en': self.short_description_en}
        if lang_short_description_dict[lang] is not None:
            return lang_short_description_dict[lang]
        for x in lang_short_description_dict.values():
            if x is not None:
                return x
        return None


class Highlight(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='highlights')
    name_oc = models.CharField(max_length=100, blank=True)
    name_es = models.CharField(max_length=100, blank=True)
    name_ca = models.CharField(max_length=100, blank=True)
    name_fr = models.CharField(max_length=100, blank=True)
    name_en = models.CharField(max_length=100, blank=True)
    long_text_oc = models.CharField(max_length=2000, blank=True)
    long_text_es = models.CharField(max_length=2000, blank=True)
    long_text_ca = models.CharField(max_length=2000, blank=True)
    long_text_fr = models.CharField(max_length=2000, blank=True)
    long_text_en = models.CharField(max_length=2000, blank=True)
    media = models.FileField(upload_to=make_media_uuid('erulet/highlights'), blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)
    TYPE_CHOICES = ((0, 'point of interest'), (1, 'waypoint'),)
    type = models.IntegerField(choices=TYPE_CHOICES)
    step = models.ForeignKey(Step, blank=True, null=True, related_name='highlights')
    order = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        names = [self.name_oc, self.name_es, self.name_ca, self.name_fr, self.name_en]
        for name in names:
            if name is not None:
                return name
        return str(self.id)

    def get_name(self, lang='oc'):
        lang_names_dict = {'oc': self.name_oc, 'es': self.name_es, 'ca': self.name_ca, 'fr': self.name_fr, 'en': self.name_en}
        if lang_names_dict[lang] is not None:
            return lang_names_dict[lang]
        for name in lang_names_dict.values():
            if name is not None:
                return name
        return str(self.id)

    def get_long_text(self, lang='oc'):
        lang_long_text_dict = {'oc': self.long_text_oc, 'es': self.long_text_es, 'ca': self.long_text_ca, 'fr': self.long_text_fr, 'en': self.long_text_en}
        if lang_long_text_dict[lang] is not None:
            return lang_long_text_dict[lang]
        for x in lang_long_text_dict.values():
            if x is not None:
                return x
        return None

    def get_media_ext(self):
        ext = ''
        if self.media.name:
            ext = self.media.name.split('.')[-1]
        return ext

    def test_image(self):
        return self.get_media_ext() in ['jpg', 'png', 'gif', 'tif']

    def test_video(self):
        return self.get_media_ext() in ['mp4', 'webm', 'ogg']

    image = property(test_image)
    video = property(test_video)
    media_ext = property(get_media_ext)


class InteractiveImage(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    image_file = models.ImageField(upload_to=make_media_uuid('erulet/interactive_images'))
    highlight = models.ForeignKey(Highlight, blank=True, null=True, related_name='interactive_images')

    def __unicode__(self):
        this_name = 'unlinked interactive image'
        if self.highlight is not None:
            this_name = 'interactive image of ' + self.highlight.__unicode__()
        return this_name

    def get_image_height(self):
        im = Image.open(self.image_file.path)
        return im.size[1]

    def get_image_width(self):
        im = Image.open(self.image_file.path)
        return im.size[0]

    original_height = property(get_image_height)
    original_width = property(get_image_width)


class Box(models.Model):
    uuid = models.CharField(max_length=40, blank=True)
    interactive_image = models.ForeignKey(InteractiveImage, related_name='boxes')
    message_oc = models.TextField("Message - Aranese", blank=True)
    message_es = models.TextField("Message - Spanish", blank=True)
    message_ca = models.TextField("Message - Catalan", blank=True)
    message_fr = models.TextField("Message - French", blank=True)
    message_en = models.TextField("Message - English", blank=True)
    max_y = models.IntegerField()
    max_x = models.IntegerField()
    min_y = models.IntegerField()
    min_x = models.IntegerField()

    class Meta:
        verbose_name = "box"
        verbose_name_plural = "boxes"

    def __unicode__(self):
        return str(self.id)

    def get_message(self, lang='oc'):
        lang_message_dict = {'oc': self.message_oc, 'es': self.message_es, 'ca': self.message_ca, 'fr': self.message_fr, 'en': self.message_en}
        if lang_message_dict[lang] is not None:
            return lang_message_dict[lang]
        for x in lang_message_dict.values():
            if x is not None:
                return x
        return None

    def get_all_messages_html(self):
        html = ""
        lang_message_dict = {'oc': self.message_oc, 'es': self.message_es, 'ca': self.message_ca, 'fr': self.message_fr, 'en': self.message_en}
        for key in lang_message_dict:
            if lang_message_dict[key] is not None:
                html += "<p><strong>" + key + ":</strong> " + lang_message_dict[key] + "</p>"
            else:
                html += "<p><strong>" + key + ":</strong> Not yet translated.</p>"
        return html


class Rating(models.Model):
    rating = models.IntegerField()
    user = models.ForeignKey(User, related_name='ratings')
    time = models.DateTimeField()
    highlight = models.ForeignKey(Highlight, blank=True, null=True)
    route = models.ForeignKey(Route, blank=True, null=True, related_name='ratings')

    def __unicode__(self):
        this_name = 'Rating ' + str(self.id)
        if self.highlight is not None:
            this_name = 'Rating for highlight: ' + self.highlight__unicode__()
        elif self.route is not None:
            this_name = 'Rating for route: ' + self.route.__unicode__()
        return this_name
