from django.conf.urls import *
from django.conf.urls.i18n import i18n_patterns
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse
from django.contrib.gis import admin
from django.conf import settings
from django.conf.urls.static import static
from frontulet.views import *

admin.autodiscover()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('', url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include('appulet.urls')),
    url(r'^home/', show_home, name='show_home'),
    url(r'^create_ii/(?P<highlight_id>[0-9]+)/$', create_ii, name='create_ii'),
    url(r'^edit_ii/(?P<ii_id>[0-9]+)/$', edit_ii, name='edit_ii'),
    url(r'^create_ii_box/(?P<ii_id>[0-9]+)/$', create_ii_box, name='create_ii_box'),
    url(r'^view_ii/(?P<ii_id>[0-9]+)/$', view_ii, name='view_ii'),
    url(r'^about/', show_about, name='show_about'),
    url(r'^map/', show_map, name='show_map'),
    url(r'^edit_profile/', edit_profile, name='edit_profile'),
    url(r'^edit_highlight/(?P<route_id>[0-9]+)/(?P<highlight_id>[0-9]+)/$', edit_highlight, name='edit_highlight'),
    url(r'^new_route/', make_new_route, name='make_new_route'),
    url(r'^edit_route/(?P<id>[0-9]+)/$', edit_route, name='edit_route'),
    url(r'^new_route_ref/(?P<route_id>[0-9]+)/$', make_new_route_reference, name='make_new_route_reference'),
    url(r'^edit_route_ref/(?P<route_id>[0-9]+)/$', edit_route_reference, name='edit_route_reference'),
    url(r'^new_highlight_ref/(?P<route_id>[0-9]+)/(?P<highlight_id>[0-9]+)/$', make_new_highlight_reference, name='make_new_highlight_reference'),
    url(r'^edit_highlight_ref/(?P<route_id>[0-9]+)/(?P<reference_id>[0-9]+)/$', edit_highlight_reference, name='edit_highlight_reference'),
    url(r'^delete_highlight_ref/(?P<route_id>[0-9]+)/(?P<reference_id>[0-9]+)/$', delete_highlight_reference, name='delete_highlight_reference'),
    url(r'^routes/$', show_route_list, name='show_route_list_all'),
    url(r'^routes/(?P<whose>\w+)/$', show_route_list, name='show_route_list'),
    url(r'^route_detail/(?P<id>[0-9]+)/$', show_route_detail, name='show_route_detail'),
    url(r'^privacy/', show_privacy_policy, name='show_privacy_policy'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='auth_login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^$', show_landing_page, name='show_landing_page'),
    url(r'^register/$', RegistrationView.as_view(), name='auth_register'),
    url('^accounts/profile/$', show_profile, name='show_profile'),) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
