from django.conf.urls import *
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse
from django.contrib.gis import admin
from django.conf import settings
from django.conf.urls.static import static
from frontulet.views import show_landing_page, show_privacy_policy, show_map
from appulet.views import make_new_route

admin.autodiscover()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include('appulet.urls')),
    url(r'^map/', show_map, name='show_map'),
    url(r'^new_route/', make_new_route, name='make_new_route'),
    url(r'^privacy/', show_privacy_policy, name='show_privacy_policy'),
    url(r'^$', show_landing_page, name='show_landing_page'),) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
