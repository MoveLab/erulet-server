from django.conf.urls import patterns, url, include
from rest_framework import routers
from appulet.views import *


router = routers.DefaultRouter()
router.register(r'interactive_images', InteractiveImageViewSet)
router.register(r'tracks', TrackViewSet)
router.register(r'routes', RouteViewSet)
router.register(r'steps', StepViewSet)
router.register(r'references', ReferenceViewSet)
router.register(r'boxes', BoxViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'highlights', HighlightViewSet)
router.register(r'nested_tracks', TrackNestedViewSet)
router.register(r'nested_routes', RouteNestedViewSet)


urlpatterns = patterns('appulet.views',
    url(r'^media/$', 'post_media'),
    url(r'^general_references/$', get_general_reference_files, name='get_general_reference_files'),
    url(r'^general_references/(?P<max_width>[0-9]+)/$', get_general_reference_files, name='get_general_reference_files_width'),
    url(r'^general_references/(?P<max_width>[0-9]+)/(?P<last_updated_unix_time_utc>[0-9]+)/$', get_general_reference_files, name='get_general_reference_files_width_last_updated'),
    url(r'^route_content/(?P<route_id>[0-9]+)/$', get_route_content_files, name='get_route_content_files'),
    url(r'^route_content/(?P<route_id>[0-9]+)/(?P<max_width>[0-9]+)/$', get_route_content_files, name='get_route_content_files_width'),
    url(r'^route_content/(?P<route_id>[0-9]+)/(?P<max_width>[0-9]+)/(?P<last_updated_unix_time_utc>[0-9]+)/$', get_route_content_files, name='get_route_content_files_width_last_updated'),
    url(r'^route_map/(?P<route_id>[0-9]+)/$', get_route_map, name='get_route_map'),
    url(r'^route_map/(?P<route_id>[0-9]+)/(?P<last_updated_unix_time_utc>[0-9]+)/$', get_route_map, name='get_route_map_last_updated'),
    url(r'^general_map/$', get_general_map, name='get_general_map'),
    url(r'^general_map/(?P<last_updated_unix_time_utc>[0-9]+)/$', get_general_map, name='get_general_map_last_updated'),
    url(r'^', include(router.urls)),
)