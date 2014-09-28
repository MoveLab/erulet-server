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
    url(r'^route_content/(?P<route_id>[0-9]+)/$', get_route_content_files, name='get_route_content_files'),
    url(r'^', include(router.urls)),
)