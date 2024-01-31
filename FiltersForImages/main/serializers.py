from rest_framework import serializers
from .models import *

class FiltersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filters
        fields = "__all__"

class FilterOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterOrder
        fields = "__all__"

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('login', 'email', 'id')

class OrdersSerializer(serializers.ModelSerializer):
    owner = UsersSerializer(read_only=True)
    moderator = UsersSerializer(read_only=True)
    class Meta:
        model = Orders
        fields = "__all__"