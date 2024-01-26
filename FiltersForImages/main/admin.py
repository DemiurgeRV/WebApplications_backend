from django.contrib import admin
from .models import *

admin.site.register(Filters)
admin.site.register(Orders)
admin.site.register(Users)
admin.site.register(FilterOrder)