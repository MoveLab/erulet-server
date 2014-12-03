from django.db import models
import uuid
import os
import os.path
from django.contrib.auth.models import User
import string
from django.conf import settings
import codecs
from PIL import Image
import pytz
from datetime import datetime
from django.db.models import Avg, Min, Max, StdDev
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _


class Track(models.Model):
    name_oc = models.CharField(max_length=200, blank=True)
    name_es = models.CharField(max_length=200, blank=True)
    name_ca = models.CharField(max_length=200, blank=True)
    name_fr = models.CharField(max_length=200, blank=True)
    name_en = models.CharField(max_length=200, blank=True)
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        return str(self.id)

    def get_name(self, lang='oc'):
        lang_names_dict = {'oc': self.name_oc, 'es': self.name_es, 'ca': self.name_ca, 'fr': self.name_fr, 'en': self.name_en}
        if lang_names_dict[lang] is not None and lang_names_dict[lang] != '':
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


def make_map_uuid(path):
    def wrapper(instance, filename):
        extension = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), extension)
        new_path = os.path.join(path)
        return os.path.join(new_path, filename)
    return wrapper


def make_reference_image_uuid(path):
    def wrapper(instance, filename):
        return os.path.join(path, str(instance.highlight.id), filename)
    return wrapper


class Step(models.Model):
    absolute_time = models.DateTimeField(blank=True, null=True)
    track = models.ForeignKey(Track, blank=True, null=True, related_name='steps')
    order = models.IntegerField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(blank=True, null=True)
    precision = models.FloatField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        return str(self.id)


def filenamei18(base, lang='oc'):
    bs = base.split('.')
    return bs[0] + '_' + lang + '.' + bs[1]


class Reference(models.Model):
    name_oc = models.CharField(verbose_name=_("name_aranese"), max_length=200, blank=True)
    name_es = models.CharField(verbose_name=_("name_spanish"), max_length=200, blank=True)
    name_ca = models.CharField(verbose_name=_("name_catalan"), max_length=200, blank=True)
    name_fr = models.CharField(verbose_name=_("name_french"), max_length=200, blank=True)
    name_en = models.CharField(verbose_name=_("name_english"), max_length=200, blank=True)
    html_file = models.FileField(verbose_name=_('zip_file'), upload_to=make_media_uuid('holet/references'))
    highlight = models.ForeignKey('Highlight', blank=True, null=True, related_name='references', verbose_name=_("highlight"))
    general = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        names = [self.name_oc, self.name_es, self.name_ca, self.name_fr, self.name_en]
        for name in names:
            if name is not None and name != '':
                return name
        return str(self.id)

    def get_name(self, lang='oc'):
        lang_names_dict = {'oc': self.name_oc, 'es': self.name_es, 'ca': self.name_ca, 'fr': self.name_fr, 'en': self.name_en}
        if lang_names_dict[lang] is not None and lang_names_dict[lang] != '':
            return lang_names_dict[lang]
        for name in lang_names_dict.values():
            if name is not None and name != '':
                return name
        return str(self.id)

    def find_reference_url(self):
        temp = str.split(self.html_file.url, '/')
        if len(temp) > 1:
            temp.pop(-1)
            temp.append('reference.html')
        return settings.CURRENT_DOMAIN + string.join(temp, '/')

    def find_reference_url_base(self):
        result = ''
        if self.html_file:
            result = str.split(self.html_file.url, '/')
            if len(result) > 1:
                result.pop(-1)
        return settings.CURRENT_DOMAIN + string.join(result, '/')

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
            this_filename = 'reference.html'
            if os.path.isfile(os.path.join(os.path.dirname(self.html_file.path), this_filename)):
                return os.path.join(os.path.dirname(self.html_file.path), this_filename)
        return ''

    def get_reference_html(self, lang='oc'):
        reference_html_raw = ''
        if os.path.isfile(self.find_reference_path(lang)):
            ref_file = codecs.open(self.find_reference_path(lang), 'r', 'cp1252')
            reference_html_raw = ref_file.read()
            ref_file.close()
        return reference_html_raw

    reference_url = property(find_reference_url)
    reference_url_base = property(find_reference_url_base)


def gpx_tracks(instance, filename):
    return "holet/gpx_tracks/%s.gpx" % uuid.uuid4()


def gpx_waypoints(instance, filename):
    return "holet/gpx_waypoints/%s.gpx" % uuid.uuid4()


def gpx_pois(instance, filename):
    return "holet/gpx_pois/%s.gpx" % uuid.uuid4()


class Route(models.Model):
    id_route_based_on = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, related_name='related_routes')
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='routes')
    description_oc = models.TextField(verbose_name=_("description_aranese"), blank=True)
    description_es = models.TextField(verbose_name=_("description_spanish"), blank=True)
    description_ca = models.TextField(verbose_name=_("description_catalan"), blank=True)
    description_fr = models.TextField(verbose_name=_("description_french"), blank=True)
    description_en = models.TextField(verbose_name=_("description_english"), blank=True)
    short_description_oc = models.CharField(verbose_name=_("short_description_aranese"), max_length=100, blank=True)
    short_description_es = models.CharField(verbose_name=_("short_description_spanish"), max_length=100, blank=True)
    short_description_ca = models.CharField(verbose_name=_("short_description_catalan"), max_length=100, blank=True)
    short_description_fr = models.CharField(verbose_name=_("short_description_french"), max_length=100, blank=True)
    short_description_en = models.CharField(verbose_name=_("short_description_english"), max_length=100, blank=True)
    name_oc = models.CharField(verbose_name=_("name_aranese"), max_length=200, blank=True)
    name_es = models.CharField(verbose_name=_("name_spanish"), max_length=200, blank=True)
    name_ca = models.CharField(verbose_name=_("name_catalan"), max_length=200, blank=True)
    name_fr = models.CharField(verbose_name=_("name_french"), max_length=200, blank=True)
    name_en = models.CharField(verbose_name=_("name_english"), max_length=200, blank=True)
    reference = models.OneToOneField(Reference, blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("reference"))
    track = models.OneToOneField(Track, blank=True, null=True, related_name='route', verbose_name=_("track"))
    upload_time = models.DateTimeField(blank=True, null=True)
    gpx_track = models.FileField(_("gpx_track"), upload_to=gpx_tracks, blank=True)
    gpx_waypoints = models.FileField(_("gps_waypoints"), upload_to=gpx_waypoints, blank=True)
    gpx_pois = models.FileField(_("gpx_poi"), upload_to=gpx_pois, blank=True)
    official = models.BooleanField(_("official_route"), default=False)
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    display_order = models.PositiveSmallIntegerField(blank=True, null=True)

    def __unicode__(self):
        names = [self.name_oc, self.name_es, self.name_ca, self.name_fr, self.name_en]
        for name in names:
            if name is not None and name != '':
                return name
        return str(self.id)

    def get_name(self, lang='oc'):
        result = 'Unnamed Route - ID: ' + str(self.id)
        lang_names_dict = {'oc': self.name_oc, 'es': self.name_es, 'ca': self.name_ca, 'fr': self.name_fr, 'en': self.name_en}
        if lang_names_dict[lang] is not None and lang_names_dict[lang] != '':
            result = lang_names_dict[lang]
        else:
                for name in lang_names_dict.values():
                    if name is not None and name != '':
                        result = name
        return result

    def get_description(self, lang='oc'):
        lang_description_dict = {'oc': self.description_oc, 'es': self.description_es, 'ca': self.description_ca, 'fr': self.description_fr, 'en': self.description_en}
        if lang_description_dict[lang] is not None and lang_description_dict[lang] != '':
            return lang_description_dict[lang]
        for x in lang_description_dict.values():
            if x is not None and x != '':
                return x
        return ''

    def get_short_description(self, lang='oc'):
        lang_short_description_dict = {'oc': self.short_description_oc, 'es': self.short_description_es, 'ca': self.short_description_ca, 'fr': self.short_description_fr, 'en': self.short_description_en}
        if lang_short_description_dict[lang] is not None and lang_short_description_dict[lang] != '':
            return lang_short_description_dict[lang]
        for x in lang_short_description_dict.values():
            if x is not None and x != '':
                return x
        return ''

    def get_average_rating(self):
        these_ratings = self.ratings.order_by('user', '-time').distinct('user').values_list('rating')
        if these_ratings and len(these_ratings) > 0:
            return sum([v[0] for v in these_ratings])/float(len(these_ratings))
        else:
            return None

    def get_total_ratings(self):
        return self.ratings.all().order_by('user').distinct('user').count()

    def get_user_rating(self, user):
        if self.ratings.filter(user=user).count() > 0:
            return self.ratings.filter(user=user).latest('time').rating
        else:
            return 0

    def get_top_five_user_highlights(self):
        these_highlights = Highlight.objects.filter(step__track__route__official=False, step__track__route__id_route_based_on=self)
        if these_highlights.count() > 0:
            these_highlights_list = list(these_highlights)
            these_highlights_list.sort(key=lambda x: x.average_rating, reverse=True)
            top_five = these_highlights_list[:5]
            return top_five
        else:
            return None

    average_rating = property(get_average_rating)
    total_ratings = property(get_total_ratings)
    top_five_user_highlights = property(get_top_five_user_highlights)


class RouteTranslationVCS(models.Model):
    route = models.ForeignKey(Route, related_name='route_translation_vcs_entries')
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    user = models.ForeignKey(User)
    description_oc = models.TextField(verbose_name=_("description_aranese"), blank=True)
    description_es = models.TextField(verbose_name=_("description_spanish"), blank=True)
    description_ca = models.TextField(verbose_name=_("description_catalan"), blank=True)
    description_fr = models.TextField(verbose_name=_("description_french"), blank=True)
    description_en = models.TextField(verbose_name=_("description_english"), blank=True)
    short_description_oc = models.CharField(verbose_name=_("short_description_aranese"), max_length=100, blank=True)
    short_description_es = models.CharField(verbose_name=_("short_description_spanish"), max_length=100, blank=True)
    short_description_ca = models.CharField(verbose_name=_("short_description_catalan"), max_length=100, blank=True)
    short_description_fr = models.CharField(verbose_name=_("short_description_french"), max_length=100, blank=True)
    short_description_en = models.CharField(verbose_name=_("short_description_english"), max_length=100, blank=True)
    name_oc = models.CharField(verbose_name=_("name_aranese"), max_length=200, blank=True)
    name_es = models.CharField(verbose_name=_("name_spanish"), max_length=200, blank=True)
    name_ca = models.CharField(verbose_name=_("name_catalan"), max_length=200, blank=True)
    name_fr = models.CharField(verbose_name=_("name_french"), max_length=200, blank=True)
    name_en = models.CharField(verbose_name=_("name_english"), max_length=200, blank=True)

    def __unicode__(self):
        return self.route.__unicode__()


class Map(models.Model):
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='map', on_delete=models.SET_NULL)
    route = models.OneToOneField(Route, blank=True, null=True)
    TYPE_CHOICES = ((0, 'route'), (1, 'general'),)
    type = models.IntegerField(choices=TYPE_CHOICES)
    map_file = models.FileField(upload_to=make_map_uuid('holet/maps'))
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        if self.route:
            return 'Map for route: ' + self.route.get_name()
        else:
            return 'General Map'

    def get_map_file_name(self):
        if self.map_file:
            return os.path.basename(self.map_file.name)
        else:
            return ''

    map_file_name = property(get_map_file_name)


class Highlight(models.Model):
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='highlights', on_delete=models.SET_NULL)
    id_on_creator_device = models.IntegerField(blank=True, null=True)
    name_oc = models.CharField(verbose_name=_("name_aranese"), max_length=100, blank=True)
    name_es = models.CharField(verbose_name=_("name_spanish"), max_length=100, blank=True)
    name_ca = models.CharField(verbose_name=_("name_catalan"), max_length=100, blank=True)
    name_fr = models.CharField(verbose_name=_("name_french"), max_length=100, blank=True)
    name_en = models.CharField(verbose_name=_("name_english"), max_length=100, blank=True)
    long_text_oc = models.CharField(verbose_name=_("description_aranese"), max_length=2000, blank=True)
    long_text_es = models.CharField(verbose_name=_("description_spanish"), max_length=2000, blank=True)
    long_text_ca = models.CharField(verbose_name=_("description_catalan"), max_length=2000, blank=True)
    long_text_fr = models.CharField(verbose_name=_("description_french"), max_length=2000, blank=True)
    long_text_en = models.CharField(verbose_name=_("description_english"), max_length=2000, blank=True)
    media = models.FileField(verbose_name=_("Media"), upload_to=make_media_uuid('holet/highlights'), blank=True, null=True)
    radius = models.FloatField(verbose_name=_("Radius"), blank=True, null=True)
    TYPE_CHOICES = ((0, 'point of interest'), (1, 'waypoint'), (2, 'alert'),)
    type = models.IntegerField(verbose_name=_("Type"), choices=TYPE_CHOICES)
    step = models.ForeignKey(Step, blank=True, null=True, related_name='highlights')
    order = models.IntegerField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        names = [self.name_oc, self.name_es, self.name_ca, self.name_fr, self.name_en]
        for name in names:
            if name is not None and name != '':
                return name
        return str(self.id)

    def get_name(self, lang='oc'):
        lang_names_dict = {'oc': self.name_oc, 'es': self.name_es, 'ca': self.name_ca, 'fr': self.name_fr, 'en': self.name_en}
        if lang_names_dict[lang] is not None and lang_names_dict[lang] != '':
            return lang_names_dict[lang]
        for name in lang_names_dict.values():
            if name is not None and name != '':
                return name
        return 'Unnamed Highlight - ID: ' + str(self.id)

    def get_long_text(self, lang='oc'):
        lang_long_text_dict = {'oc': self.long_text_oc, 'es': self.long_text_es, 'ca': self.long_text_ca, 'fr': self.long_text_fr, 'en': self.long_text_en}
        if lang_long_text_dict[lang] is not None and lang_long_text_dict[lang] != '':
            return lang_long_text_dict[lang]
        for x in lang_long_text_dict.values():
            if x is not None and x != '':
                return x
        return ''

    def get_media_ext(self):
        ext = ''
        if self.media.name:
            ext = self.media.name.split('.')[-1]
        return ext

    def test_image(self):
        return self.get_media_ext() in ['jpg', 'png', 'gif', 'tif']

    def test_video(self):
        return self.get_media_ext() in ['mp4', 'webm', 'ogg']

    def get_media_file_name(self):
        if self.media:
            return os.path.basename(self.media.name)
        else:
            return ''

    def get_average_rating(self):
        these_ratings = self.ratings.order_by('user', '-time').distinct('user').values_list('rating')
        if these_ratings and len(these_ratings) > 0:
            return sum([v[0] for v in these_ratings])/float(len(these_ratings))
        else:
            return None

    def get_total_ratings(self):
        return self.ratings.all().order_by('user').distinct('user').count()

    def get_user_rating(self, user):
        if self.ratings.filter(user=user).count() > 0:
            return self.ratings.filter(user=user).latest('time').rating
        else:
            return 0

    def get_lat(self):
        return self.step.latitude

    def get_lon(self):
        return self.step.longitude

    def get_altitude(self):
        return self.step.altitude

    def get_media_url(self):
        if self.media:
            return self.media.url
        else:
            return None

    image = property(test_image)
    video = property(test_video)
    media_ext = property(get_media_ext)
    media_name = property(get_media_file_name)
    media_url = property(get_media_url)
    average_rating = property(get_average_rating)
    total_ratings = property(get_total_ratings)
    latitude = property(get_lat)
    longitude = property(get_lon)
    altitude = property(get_altitude)


class HighlightTranslationVCS(models.Model):
    highlight = models.ForeignKey(Highlight, related_name='highlight_translation_vcs_entries')
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    user = models.ForeignKey(User)
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

    def __unicode__(self):
        return self.highlight.__unicode__()


class InteractiveImage(models.Model):
    image_file = models.ImageField(upload_to=make_media_uuid('holet/interactive_images'))
    highlight = models.ForeignKey(Highlight, blank=True, null=True, related_name='interactive_images')
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

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

    def get_image_file_name(self):
        if self.image_file:
            return os.path.basename(self.image_file.name)
        else:
            return ''

    image_name = property(get_image_file_name)

    original_height = property(get_image_height)
    original_width = property(get_image_width)


class Box(models.Model):
    interactive_image = models.ForeignKey(InteractiveImage, related_name='boxes')
    message_oc = models.TextField(verbose_name=_("message_aranese"), blank=True)
    message_es = models.TextField(verbose_name=_("message_spanish"), blank=True)
    message_ca = models.TextField(verbose_name=_("message_catalan"), blank=True)
    message_fr = models.TextField(verbose_name=_("message_french"), blank=True)
    message_en = models.TextField(verbose_name=_("message_english"), blank=True)
    max_y = models.IntegerField()
    max_x = models.IntegerField()
    min_y = models.IntegerField()
    min_x = models.IntegerField()
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    class Meta:
        verbose_name = "box"
        verbose_name_plural = "boxes"

    def __unicode__(self):
        return str(self.id)

    def get_message(self, lang='oc'):
        lang_message_dict = {'oc': self.message_oc, 'es': self.message_es, 'ca': self.message_ca, 'fr': self.message_fr, 'en': self.message_en}
        if lang_message_dict[lang] is not None and lang_message_dict[lang] != '':
            return lang_message_dict[lang]
        for x in lang_message_dict.values():
            if x is not None and x != '':
                return x
        return None

    def get_all_messages_html(self):
        html = ""
        lang_message_dict = {'oc': self.message_oc, 'es': self.message_es, 'ca': self.message_ca, 'fr': self.message_fr, 'en': self.message_en}
        for key in lang_message_dict:
            if lang_message_dict[key] is not None:
                html += "<p><strong>" + key + ":</strong> " + lang_message_dict[key] + "</p>"
            else:
                html += "<p><strong>" + key + ":</strong></p>"
        return html


def get_now_utc():
    return datetime.now(pytz.utc)


class Rating(models.Model):
    rating = models.IntegerField()
    user = models.ForeignKey(User, related_name='ratings')
    time = models.DateTimeField(default=get_now_utc, blank=True, null=True)
    highlight = models.ForeignKey(Highlight, blank=True, null=True, related_name='ratings')
    route = models.ForeignKey(Route, blank=True, null=True, related_name='ratings')
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        this_name = 'Rating ' + str(self.id)
        if self.highlight is not None:
            this_name = 'Rating for highlight: ' + self.highlight.__unicode__()
        elif self.route is not None:
            this_name = 'Rating for route: ' + self.route.__unicode__()
        return this_name

    # functions for grabbing latest route and highlight stats so that these can be
    # easily returned to apps in POST responses
    def get_average_route_rating(self):
        if self.route:
            return self.route.average_rating
        else:
            return None

    def get_total_route_ratings(self):
        if self.route:
            return self.route.total_ratings
        else:
            return None

    def get_average_highlight_rating(self):
        if self.highlight:
            return self.highlight.average_rating
        else:
            return None

    def get_total_highlight_ratings(self):
        if self.highlight:
            return self.highlight.total_ratings
        else:
            return None

    average_route_rating = property(get_average_route_rating)
    total_route_ratings = property(get_total_route_ratings)
    average_highlight_rating = property(get_average_highlight_rating)
    total_highlight_ratings = property(get_total_highlight_ratings)


class SurveyScheme(models.Model):
    unique_name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, related_name='survey_schemes')
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        return self.unique_name


class SurveyQuestion(models.Model):
    survey_scheme = models.ForeignKey(SurveyScheme, related_name='questions')
    question_oc = models.CharField(max_length=1000)
    question_es = models.CharField(max_length=1000)
    question_ca = models.CharField(max_length=1000)
    question_fr = models.CharField(max_length=1000)
    question_en = models.CharField(max_length=1000)
    created_by = models.ForeignKey(User, related_name='survey_questions')
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        return self.survey_scheme.unique_name + ' question ' + str(self.id)

    def get_question(self, lang='oc'):
        result = ''
        lang_questions_dict = {'oc': self.question_oc, 'es': self.question_es, 'ca': self.question_ca, 'fr': self.question_fr, 'en': self.question_en}
        if lang_questions_dict[lang] is not None and lang_questions_dict[lang] != '':
            result = lang_questions_dict[lang]
        else:
                for question in lang_questions_dict.values():
                    if question is not None and question != '':
                        result = question
        return result

    def get_average_response(self):
        return self.responses.aggregate(Avg('integer_response'))['integer_response__avg']

    def get_min_response(self):
        return self.responses.aggregate(Min('integer_response'))['integer_response__min']

    def get_max_response(self):
        return self.responses.aggregate(Max('integer_response'))['integer_response__max']

    def get_sd_responses(self):
        return self.responses.aggregate(StdDev('integer_response'))['integer_response__stddev']

    def get_total_responses(self):
        return self.responses.all().count()


class SurveyInstance(models.Model):
    survey_scheme = models.ForeignKey(SurveyScheme, related_name='survey_instances')
    language = models.CharField(max_length=2, default='oc')
    route = models.ForeignKey(Route, blank=True, null=True, related_name='survey_instances')
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        return self.survey_scheme.unique_name + ' instance ' + str(self.id)


class SurveyResponse(models.Model):
    survey_instance = models.ForeignKey(SurveyInstance, related_name='responses')
    question = models.ForeignKey(SurveyQuestion, related_name='responses')
    response = models.TextField(blank=True)
    integer_response = models.IntegerField(blank=True, null=True,  validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_modified = models.DateTimeField(auto_now=True, default=datetime.now())
    created = models.DateTimeField(auto_now_add=True, default=datetime.now())

    def __unicode__(self):
        return self.survey_instance.survey_scheme.unique_name + ' response ' + str(self.id)
