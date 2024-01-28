from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *


@api_view(['GET'])
def filters_list(request):                          # список неудаленных фильтров
    input_text = request.GET.get('search-filter', '')
    filters = Filters.objects.filter(name__icontains=input_text).filter(status=1) if input_text else Filters.objects.filter(status=1)
    serializer = FiltersSerializer(filters, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def one_filter(request, id):                        # получение одного фильтра по id
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    serializer = FiltersSerializer(filter)

    return Response(serializer.data)

@api_view(['POST'])
def create_filter(request):                         # создание фильтра
    serializer = FiltersSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        filters = Filters.objects.filter(status=1)
        serializer = FiltersSerializer(filters, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_filter(request, id):                     # обновление данных о фильтре
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    serializer = FiltersSerializer(filter, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        filters = Filters.objects.filter(status=1)
        serializer = FiltersSerializer(filters, many=True)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_filter(request, id):                         # удаление фильтра
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    filter.status = 2
    filter.save()

    filters = Filters.objects.filter(status=1)
    serializer = FiltersSerializer(filters, many=True)
    return Response(serializer.data)




# from django.db import connection
# from django.shortcuts import render, redirect
#
#
# from .models import *
#
# def getFilters(request):
#     input_text = request.GET.get('search-filter')
#     filters = Filters.objects.filter(name__icontains=input_text).filter(status=1) if input_text else Filters.objects.filter(status=1)
#
#     return render(request, 'main/AllFilters.html', { 'data' : { 'filters' : filters,
#                                                                 'input' : input_text if input_text else ''
#                                                                     }
#                                                          })
#
# def getFilter(request, id):
#     filter = Filters.objects.filter(id=id)
#     return render(request, 'main/OneFilter.html', {'filter': filter[0]})
#
# def delete_filter(request, id):
#     filter = Filters.objects.get(id=id)
#     with connection.cursor() as cursor:
#         cursor.execute("UPDATE main_filters SET status = 2 WHERE id = %s", [filter.pk])
#     return redirect('/home')