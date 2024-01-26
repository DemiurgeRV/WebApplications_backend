from django.shortcuts import render
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
