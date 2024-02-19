from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        FilterOrder.objects.all().delete()
        Orders.objects.all().delete()
        Filters.objects.all().delete()
        Users.objects.all().delete()