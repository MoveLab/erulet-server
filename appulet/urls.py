from django.conf.urls import patterns, url, include
import routers
from appulet.views import *


router = routers.OrderedDefaultRouter()
router.register(r'routes', RouteViewSet, base_name='route')
router.register(r'my_routes', UserRouteViewSet, base_name='my_route')
router.register(r'nested_routes', RouteNestedViewSet, base_name='nested_route')
router.register(r'my_nested_routes', UserRouteNestedViewSet, base_name='my_nested_route')
router.register(r'ratings', RatingViewSet, base_name='rating')
router.register(r'my_ratings', UserRatingViewSet, base_name='my_rating')
router.register(r'highlights', HighlightViewSet, base_name='highlight')
router.register(r'my_highlights', UserHighlightViewSet, base_name='my_highlight')
router.register(r'maps', MapViewSet, base_name='map')

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
    url(r'^file_download_endpoint/(?P<view>\w+)/$', show_file_download_endpoint, name='show_file_download_endpoint'),
    url(r'^mobile_pages/$', show_mobile_pages_help, name='show_mobile_pages'),
    url(r'^', include(router.urls)),
)