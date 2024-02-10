from rest_framework import serializers
from .models import *
from collections import OrderedDict


class FiltersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filters
        fields = "__all__"

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

class FilterOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilterOrder
        fields = "__all__"

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields

class UsersSerializer(serializers.ModelSerializer):
    role = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    password = serializers.CharField()
    class Meta:
        model = Users
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('login', 'email', 'id')

class OrdersSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    moderator = UserSerializer(read_only=True)
    class Meta:
        model = Orders
        fields = "__all__"

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields