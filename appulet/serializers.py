from rest_framework import serializers
from appulet.models import *


class MapSerializer(serializers.ModelSerializer):
    map_file_name = serializers.Field()

    class Meta:
        model = Map
        fields = ('route', 'type', 'last_modified', 'created', 'map_file_name')


class RouteMapSerializer(serializers.ModelSerializer):
    map_file_name = serializers.Field()

    class Meta:
        model = Map
        fields = ('last_modified', 'created', 'map_file_name')


class HighlightSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id')
    media_name = serializers.Field()
    average_rating = serializers.Field()
    total_ratings = serializers.Field()

    class Meta:
        model = Highlight
        fields = ('server_id', 'average_rating', 'total_ratings', 'created_by', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'long_text_oc', 'long_text_es', 'long_text_ca', 'long_text_fr', 'long_text_en', 'radius', 'type', 'media_name', 'last_modified')


class UserHighlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Highlight
        exclude = ('created_by',)
        read_only_fields = ('id',)


class BoxSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id')

    class Meta:
        model = Box
        exclude = ('id',)


class ReferenceSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id')

    class Meta:
        model = Reference
        exclude = ("id",)


class RouteReferenceSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id')

    class Meta:
        model = Reference
        exclude = ("id", "highlight", "general")


class HighlightReferenceSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id')

    class Meta:
        model = Reference
        exclude = ("id", "highlight", "general")


class InteractiveImageSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id')

    class Meta:
        model = InteractiveImage


class InteractiveImageNestedSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id')
    boxes = BoxSerializer(many=True)
    original_height = serializers.Field()
    original_width = serializers.Field()
    image_name = serializers.Field()

    class Meta:
        model = InteractiveImage
        fields = ('server_id', 'image_file', 'image_name', 'original_height', 'original_width', 'boxes', 'last_modified')


class HighlightNestedSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id')
    interactive_images = InteractiveImageNestedSerializer(many=True)
    references = HighlightReferenceSerializer(many=True)
    media_name = serializers.Field()
    average_rating = serializers.Field()
    total_ratings = serializers.Field()

    class Meta:
        model = Highlight
        fields = ('server_id', 'average_rating', 'total_ratings', 'created_by', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'long_text_oc', 'long_text_es', 'long_text_ca', 'long_text_fr', 'long_text_en', 'radius', 'type', 'interactive_images', 'references', 'media_name', 'last_modified')


class StepSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Step

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer


class StepNestedSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id', read_only=True)
    highlights = HighlightNestedSerializer(many=True)

    class Meta:
        model = Step
        fields = ('server_id', 'absolute_time', 'order', 'latitude', 'longitude', 'altitude', 'precision', 'highlights', 'last_modified')


class UserStepNestedSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id', read_only=True)
    highlights = HighlightSerializer(many=True)

    class Meta:
        model = Step
        fields = ('server_id', 'absolute_time', 'order', 'latitude', 'longitude', 'altitude', 'precision', 'highlights', 'last_modified')


class TrackSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Track


class TrackNestedSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id', read_only=True)
    steps = StepNestedSerializer(many=True)

    class Meta:
        model = Track
        fields = ('server_id', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'steps', 'last_modified')


class RouteSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id', read_only=True)
    owner = serializers.Field(source='created_by.username')

    class Meta:
        model = Route
        fields = ('owner', 'server_id', 'official', 'last_modified', 'created_by')


class RouteNestedSerializer(serializers.ModelSerializer):
    track = TrackNestedSerializer(many=False)
    reference = RouteReferenceSerializer(many=False)
    map = RouteMapSerializer(many=False)
    created_by = serializers.RelatedField(many=False)
    server_id = serializers.IntegerField(source='id', read_only=True)
    average_rating = serializers.Field()
    total_ratings = serializers.Field()
    top_five_user_highlights = serializers.SerializerMethodField('get_top_five_user_highlights')
    owner = serializers.Field(source='created_by.username')

    class Meta:
        model = Route
        fields = ('owner', 'top_five_user_highlights', 'server_id', 'official', 'average_rating', 'total_ratings', 'id_route_based_on', 'map', 'description_oc', 'description_es', 'description_ca', 'description_fr', 'description_en', 'short_description_oc', 'short_description_es', 'short_description_ca', 'short_description_fr', 'short_description_en', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'reference', 'track', 'created', 'last_modified')

    def get_top_five_user_highlights(self, obj):
        obj.get_top_five_user_highlights()


class RatingSerializer(serializers.ModelSerializer):
    server_id = serializers.IntegerField(source='id', read_only=True)
    owner = serializers.Field(source='user.username')

    class Meta:
        model = Rating
        exclude = ('user',)



