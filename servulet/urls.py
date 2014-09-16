from django.conf.urls import *
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse
from django.contrib.gis import admin
from django.conf import settings
from django.conf.urls.static import static
from frontulet.views import show_landing_page, show_privacy_policy, show_map, show_route_detail, show_profile, RegistrationView
from appulet.views import make_new_route
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm

admin.autodiscover()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('', url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include('appulet.urls')),
    url(r'^map/', show_map, name='show_map'),
    url(r'^new_route/', make_new_route, name='make_new_route'),
    url(r'^route_detail/(?P<id>[0-9]+)/$', show_route_detail, name='show_route_detail'),
    url(r'^privacy/', show_privacy_policy, name='show_privacy_policy'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='auth_login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^$', show_landing_page, name='show_landing_page'),
    url(r'^register/$', RegistrationView.as_view(), name='auth_register'),
    url('^accounts/profile/$', show_profile, name='show_profile'),) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
