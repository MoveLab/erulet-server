from rest_framework import serializers
from appulet.models import *


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box


class InteractiveImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveImage


class InteractiveImageNestedSerializer(serializers.ModelSerializer):
    box = BoxSerializer(many=True)
    original_height = serializers.Field()
    original_width = serializers.Field()

    class Meta:
        model = InteractiveImage
        fields = ('id', 'uuid', 'image_file', 'original_height', 'original_width', 'box')


class HighlightNestedSerializer(serializers.ModelSerializer):
    interactive_images = InteractiveImageNestedSerializer(many=True)

    class Meta:
        model = Highlight
        fields = ('id', 'uuid', 'created_by', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'long_text_oc', 'long_text_es', 'long_text_ca', 'long_text_fr', 'long_text_en', 'radius', 'type', 'interactive_images')


class StepSerializer(serializers.ModelSerializer):

    class Meta:
        model = Step


class StepNestedSerializer(serializers.ModelSerializer):
    highlights = HighlightNestedSerializer(many=True)

    class Meta:
        model = Step
        fields = ('id', 'uuid', 'absolute_time', 'order', 'latitude', 'longitude', 'altitude', 'precision', 'highlights')


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track


class TrackNestedSerializer(serializers.ModelSerializer):
    steps = StepNestedSerializer(many=True)

    class Meta:
        model = Track
        fields = ('id', 'uuid', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'steps')


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route


class RouteNestedSerializer(serializers.ModelSerializer):
    track = TrackNestedSerializer(many=False)

    class Meta:
        model = Route
        fields = ('id', 'uuid', 'id_route_based_on', 'created_by', 'description_oc', 'description_es', 'description_ca', 'description_fr', 'description_en', 'short_description_oc', 'short_description_es', 'short_description_ca', 'short_description_fr', 'short_description_en', 'local_carto', 'name_oc', 'name_es', 'name_ca', 'name_fr', 'name_en', 'reference', 'track')


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating



