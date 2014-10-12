from django.contrib import admin
from appulet.models import *
from rest_framework.authtoken.models import Token
import csv
from django.utils.encoding import smart_str
from django.http.response import HttpResponse

admin.site.register(Track)
admin.site.register(Route)
admin.site.register(Step)
admin.site.register(Highlight)
admin.site.register(Reference)
admin.site.register(InteractiveImage)
admin.site.register(Box)
admin.site.register(Rating)
admin.site.register(Map)
