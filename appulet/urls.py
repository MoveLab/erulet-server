from django.conf.urls import patterns, url, include
from rest_framework import routers
from appulet.views import *


router = routers.DefaultRouter()
router.register(r'holet_routes', RouteViewSet)
router.register(r'my_routes', UserRouteViewSet)
router.register(r'holet_routes_nested', RouteNestedViewSet)
router.register(r'my_routes_nested', UserRouteNestedViewSet)
router.register(r'my_steps_nested', UserStepNestedViewSet)
router.register(r'all_ratings', RatingViewSet)
router.register(r'my_ratings', UserRatingViewSet)
router.register(r'holet_highlights', HighlightViewSet)
router.register(r'my_highlights', UserHighlightViewSet)


urlpatterns = patterns('appulet.views',
    url(r'^media/$', 'post_media', name='post_media'),
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