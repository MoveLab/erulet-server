from rest_framework import serializers
from appulet.models import *


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference


class InteractiveImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveImage


class InteractiveImageNestedSerializer(serializers.ModelSerializer):
    boxes = BoxSerializer(many=True)
    original_height = serializers.Field()
    original_width = serializers.Field()

    class Meta:
        model = InteractiveImage
        fields = ('id', 'image_file', 'original_height', 'original_width', 'boxes')


class HighlightNestedSerializer(serializers.ModelSerializer):
    interactive_images = InteractiveImageNestedSerializer(many=True)
    references = ReferenceSerializer(many=True)

    class Meta:
        model = Highlight
        fields = ('id', 'created_by', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'long_text_oc', 'long_text_es', 'long_text_ca', 'long_text_fr', 'long_text_en', 'radius', 'type', 'interactive_images', 'references')


class StepSerializer(serializers.ModelSerializer):

    class Meta:
        model = Step


class StepNestedSerializer(serializers.ModelSerializer):
    highlights = HighlightNestedSerializer(many=True)

    class Meta:
        model = Step
        fields = ('id', 'absolute_time', 'order', 'latitude', 'longitude', 'altitude', 'precision', 'highlights')


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track


class TrackNestedSerializer(serializers.ModelSerializer):
    steps = StepNestedSerializer(many=True)

    class Meta:
        model = Track
        fields = ('id', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'steps')


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route


class RouteNestedSerializer(serializers.ModelSerializer):
    track = TrackNestedSerializer(many=False)
    reference = ReferenceSerializer(many=False)
    local_carto_name = serializers.Field()

    class Meta:
        model = Route
        fields = ('id', 'id_route_based_on', 'created_by', 'description_oc', 'description_es', 'description_ca', 'description_fr', 'description_en', 'short_description_oc', 'short_description_es', 'short_description_ca', 'short_description_fr', 'short_description_en', 'local_carto', 'local_carto_name', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'reference', 'track')


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating



