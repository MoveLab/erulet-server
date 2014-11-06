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
    (r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include('appulet.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns('',
    url(r'^home/', show_home, name='show_home'),
    url(r'^survey/(?P<mob>\w+)/(?P<survey_name>\w+)/$', show_survey),
    url(r'^survey/(?P<mob>\w+)/(?P<survey_name>\w+)/(?P<route_id>[0-9]+)/$', show_survey),
    url(r'^survey_submitted/(?P<mob>\w+)/(?P<response_code>\w+)/$', show_survey_submitted, name='show_survey_submitted'),
    url(r'^about/$', show_about, name='show_about'),
    url(r'^about/(?P<mob>\w+)/$', show_about),
    url(r'^before_leaving/$', show_before_leaving, name='show_before_leaving'),
    url(r'^before_leaving/(?P<mob>\w+)/$', show_before_leaving),
    url(r'^manual/$', show_manual, name='show_manual'),
    url(r'^manual/(?P<mob>\w+)/$', show_manual),
    url(r'^show_general_references/$', show_general_references, name='show_general_references'),
    url(r'^new_general_reference/$', make_new_general_reference, name='new_general_reference'),
    url(r'^edit_general_reference/(?P<reference_id>[0-9]+)/$', edit_general_reference, name='edit_general_reference'),
    url(r'^delete_general_reference/(?P<reference_id>[0-9]+)/$', delete_general_reference, name='delete_general_reference'),
    url(r'^create_ii/(?P<highlight_id>[0-9]+)/$', create_ii, name='create_ii'),
    url(r'^edit_ii/(?P<ii_id>[0-9]+)/$', edit_ii, name='edit_ii'),
    url(r'^create_ii_box/(?P<ii_id>[0-9]+)/$', create_ii_box, name='create_ii_box'),
    url(r'^view_ii/(?P<ii_id>[0-9]+)/$', view_ii, name='view_ii'),
    url(r'^delete_ii/(?P<ii_id>[0-9]+)/$', delete_ii, name='delete_ii'),
    url(r'^edit_ii_box/(?P<ii_id>[0-9]+)/(?P<box_id>[0-9]+)/$', edit_ii_box, name='edit_ii_box'),
    url(r'^map/', show_map, name='show_map'),
    url(r'^edit_profile/', edit_profile, name='edit_profile'),
    url(r'^edit_highlight/(?P<route_id>[0-9]+)/(?P<highlight_id>[0-9]+)/$', edit_highlight, name='edit_highlight'),
    url(r'^translate_highlights/$', translate_highlights),
    url(r'^translate_highlights/(?P<lang>\w+)/$', translate_highlights, name='translate_highlights'),
    url(r'^translate_routes/$', translate_routes),
    url(r'^translate_routes/(?P<lang>\w+)/$', translate_routes, name='translate_routes'),
    url(r'^new_route/', make_new_route, name='make_new_route'),
    url(r'^edit_route/(?P<id>[0-9]+)/$', edit_route, name='edit_route'),
    url(r'^new_route_ref/(?P<route_id>[0-9]+)/$', make_new_route_reference, name='make_new_route_reference'),
    url(r'^edit_route_ref/(?P<route_id>[0-9]+)/$', edit_route_reference, name='edit_route_reference'),
    url(r'^delete_route_ref/(?P<route_id>[0-9]+)/$', delete_route_reference, name='delete_route_reference'),
    url(r'^delete_route/(?P<route_id>[0-9]+)/$', delete_route, name='delete_route'),
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
    url(r'^register/mob/$', RegisterFromApp.as_view(), name='auth_register_mob'),
    url(r'^accounts/profile/token=(?P<token>\w+),username=(?P<username>\w+)$', show_profile_mob, name='show_profile_mob'),
    url('^accounts/profile/$', show_profile, name='show_profile'),)