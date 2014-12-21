from django.contrib import admin
from appulet.models import *
from rest_framework.authtoken.models import Token
import csv
from django.utils.encoding import smart_str
from django.http.response import HttpResponse


class RouteAdmin(admin.ModelAdmin):
    list_display = ('name_ca', 'last_modified', 'created',)


class InteractiveImageAdmin(admin.ModelAdmin):
    list_display = ('highlight', 'last_modified', 'created', 'route_link', 'highlight_link')
    readonly_fields = ('image_file', 'highlight', 'last_modified', 'created', 'route_link', 'highlight_link')
    fields = ('image_file', 'highlight', 'last_modified', 'created', 'route_link', 'highlight_link')

    def route_link(self, obj):
        return '<a href="/admin/appulet/route/%s">%s</a>' % (obj.highlight.step.track.route.id, obj.highlight.step.track.route)
    route_link.allow_tags = True

    def highlight_link(self, obj):
        return '<a href="/admin/appulet/highlight/%s">%s</a>' % (obj.highlight.id, obj.highlight)
    highlight_link.allow_tags = True




admin.site.register(Track)
admin.site.register(Route, RouteAdmin)
admin.site.register(Step)
admin.site.register(Highlight)
admin.site.register(Reference)
admin.site.register(InteractiveImage, InteractiveImageAdmin)
admin.site.register(Box)
admin.site.register(Rating)
admin.site.register(Map)
admin.site.register(HighlightTranslationVCS)
admin.site.register(RouteTranslationVCS)
admin.site.register(SurveyScheme)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyInstance)
admin.site.register(SurveyResponse)
