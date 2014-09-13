from rest_framework import serializers
from appulet.models import *


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight


class HighlightNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight
        fields = ('id', 'uuid', 'created_by', 'name', 'long_text', 'radius', 'type', 'step')


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box


class InteractiveImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveImage


class InteractiveImageNestedSerializer(serializers.ModelSerializer):
    box = BoxSerializer(many=True)

    class Meta:
        model = InteractiveImage
        fields = ('id', 'uuid', 'image_file', 'original_height', 'original_width', 'box')


class StepSerializer(serializers.ModelSerializer):

    class Meta:
        model = Step


class StepNestedSerializer(serializers.ModelSerializer):
    highlight = HighlightNestedSerializer(many=False)
    interactive_image = InteractiveImageNestedSerializer(many=False)

    class Meta:
        model = Step
        fields = ('id', 'uuid', 'absolute_time', 'order', 'latitude', 'longitude', 'altitude', 'precision', 'highlight', 'interactive_image')


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track


class TrackNestedSerializer(serializers.ModelSerializer):
    steps = StepNestedSerializer(many=True)

    class Meta:
        model = Track
        fields = ('id', 'uuid', 'name', 'steps')


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
        fields = ('id', 'uuid', 'id_route_based_on', 'description', 'local_carto', 'name', 'track')


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating



