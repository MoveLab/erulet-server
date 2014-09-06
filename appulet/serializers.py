from rest_framework import serializers
from appulet.models import *


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track


class InteractiveImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractiveImage


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route


class HighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Highlight


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating



