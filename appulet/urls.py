from django.conf.urls import patterns, url, include
from rest_framework import routers
from appulet import views


router = routers.DefaultRouter()
router.register(r'interactive_images', views.InteractiveImageViewSet)
router.register(r'tracks', views.TrackViewSet)
router.register(r'nested_tracks', views.TrackNestedViewSet)
router.register(r'routes', views.RouteViewSet)
router.register(r'nested_routes', views.RouteNestedViewSet)
router.register(r'steps', views.StepViewSet)
router.register(r'references', views.ReferenceViewSet)
router.register(r'boxes', views.BoxViewSet)
router.register(r'ratings', views.RatingViewSet)
router.register(r'highlights', views.HighlightViewSet)


urlpatterns = patterns('appulet.views',
    url(r'^media/$', 'post_media'),
    url(r'^gpx_track/$', 'upload_gpx'),
    url(r'^success/$', 'upload_success', name='show_upload_success'),
    url(r'^', include(router.urls)),
)