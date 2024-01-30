from rest_framework import serializers
from .models import *

class FiltersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filters
        fields = "__all__"

class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = "__all__"

class FilterOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterOrder
        fields = "__all__"