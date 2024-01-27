from django.db import connection
from django.shortcuts import render, redirect


from .models import *

def getFilters(request):
    input_text = request.GET.get('search-filter')
    filters = Filters.objects.filter(name__icontains=input_text).filter(status=1) if input_text else Filters.objects.filter(status=1)

    return render(request, 'main/AllFilters.html', { 'data' : { 'filters' : filters,
                                                                'input' : input_text if input_text else ''
                                                                    }
                                                         })

def getFilter(request, id):
    filter = Filters.objects.filter(id=id)
    return render(request, 'main/OneFilter.html', {'filter': filter[0]})

def delete_filter(request, id):
    filter = Filters.objects.get(id=id)
    with connection.cursor() as cursor:
        cursor.execute("UPDATE main_filters SET status = 2 WHERE id = %s", [filter.pk])
    return redirect('/home')