from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
from drf_yasg.utils import swagger_auto_schema


@api_view(['GET'])
def filters_list(request):                          # список неудаленных фильтров
    input_text = request.GET.get('search-filter')
    filters = Filters.objects.filter(name__icontains=input_text).filter(status=1) if input_text else Filters.objects.filter(status=1)
    order = Orders.objects.filter(status=1).first()
    serializer = FiltersSerializer(filters, many=True)

    res = {
        "filters": serializer.data,
        "draft_order": order.id if order else None,
    }

    return Response(res)


@api_view(['GET'])
def one_filter(request, id):                        # получение одного фильтра по id
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    if filter.status == 2:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = FiltersSerializer(filter)

    return Response(serializer.data)

@swagger_auto_schema(method='post', request_body=FiltersSerializer)
@api_view(['POST'])
def create_filter(request):                         # создание фильтра
    serializer = FiltersSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        filters = Filters.objects.filter(status=1)
        serializer = FiltersSerializer(filters, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='put', request_body=FiltersSerializer)
@api_view(['PUT'])
def update_filter(request, id):                     # обновление данных о фильтре
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    if filter.status == 2:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = FiltersSerializer(filter, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

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

@swagger_auto_schema(method='post', request_body=OrdersSerializer)
@api_view(['POST'])
def add_to_order(request, id):                          # добавление фильтра в заявку
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    user_id = 2              # Заглушка
    user = Users.objects.get(id=user_id)
    order = Orders.objects.filter(status=1).filter(owner=user).first()

    if order is None:
        order = Orders.objects.create(owner=user)

    if FilterOrder.objects.filter(order=order, filter=filter):
        return Response(status=status.HTTP_409_CONFLICT)

    new_filterorder = FilterOrder.objects.create()
    new_filterorder.order = order
    new_filterorder.filter = filter
    new_filterorder.save()

    order_serializer = OrdersSerializer(order)
    about_order = order_serializer.data

    filters = []
    filterorder = FilterOrder.objects.filter(order=order.id)
    for i in filterorder:
        filters.append(i.filter_id)

    filters_list = Filters.objects.filter(id__in=filters)
    filters_serializer = FiltersSerializer(filters_list, many=True)
    about_order['Filters_in_Order'] = filters_serializer.data

    return Response(about_order)

@api_view(['GET'])
def orders_list(request):                               # список заявок c фильтром по дате и статусу
    orders = Orders.objects.exclude(status__in=[1, 5])
    date_start = request.GET.get("date_start")
    date_end = request.GET.get("date_end")
    order_status = request.GET.get("status", 0)

    if order_status != 0:
        orders = orders.filter(status=order_status)
    if date_start:
        orders = orders.filter(date_formation__gte=parse_datetime(date_start))
    if date_end:
        orders = orders.filter(date_formation__lte=parse_datetime(date_end))
    serializers = OrdersSerializer(orders, many=True)

    return Response(serializers.data)

@api_view(['GET'])
def one_order(request, id):                                 # заявка по id + ее услуги
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)

    if order.status == 5:
        return Response(status=status.HTTP_404_NOT_FOUND)

    order_serializer = OrdersSerializer(order)
    about_order = order_serializer.data

    filters = []
    filterorder = FilterOrder.objects.filter(order=id)
    for filter in filterorder:
        filters.append(filter.filter_id)

    filters_list = Filters.objects.filter(id__in=filters)
    filters_serializer = FiltersSerializer(filters_list, many=True)
    about_order['Filters_in_Order'] = filters_serializer.data

    return Response(about_order)

@swagger_auto_schema(method='put', request_body=OrdersSerializer)
@api_view(["PUT"])
def update_order(request, id):                                  # обновление заявки
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)
    serializer = OrdersSerializer(order, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='put', request_body=OrdersSerializer)
@api_view(["PUT"])
def update_status_owner(request, id):                           # формирование заявки
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)

    if order.status != 1:
        return Response(status=status.HTTP_409_CONFLICT)

    order.status = 2
    order.date_formation = timezone.now()
    order.save()

    serializer = OrdersSerializer(order)

    return Response(serializer.data)

@swagger_auto_schema(method='put', request_body=OrdersSerializer)
@api_view(["PUT"])
def update_status_moderator(request, id):               # одобрение/отказ заявки
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)
    order_status = order.status

    if order_status != 2:
        return Response(status=status.HTTP_403_FORBIDDEN)

    request_status = request.data.get('status')
    if request_status not in [3, 4]:
        return Response(status=status.HTTP_403_FORBIDDEN)

    moder_id = 1            # заглушка
    moderator = Users.objects.get(id=moder_id)
    order.moderator = moderator
    order.date_complete = timezone.now()
    order.status = request_status
    order.save()

    serializer = OrdersSerializer(order)

    return Response(serializer.data)

@api_view(["DELETE"])
def delete_order(request, id):                          # удаление черновой заявки
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)

    if order.status != 1:
        return Response(status=status.HTTP_403_FORBIDDEN)

    order.status = 5
    order.save()

    return Response(status=status.HTTP_200_OK)

@api_view(["DELETE"])
def delete_filter_from_order(request, filter_id, order_id):                     # удаление фильтра из черновой заявки
    if not FilterOrder.objects.filter(filter_id=filter_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=order_id)

    if order.status != 1:
        return Response(status=status.HTTP_403_FORBIDDEN)

    filter = FilterOrder.objects.get(filter_id=filter_id, order_id=order_id)
    filter.delete()

    order_serializer = OrdersSerializer(order)
    about_order = order_serializer.data

    filters = []
    filterorder = FilterOrder.objects.filter(order=order_id)
    for i in filterorder:
        filters.append(i.filter_id)

    filters_list = Filters.objects.filter(id__in=filters)
    filters_serializer = FiltersSerializer(filters_list, many=True)
    about_order['Filters_in_Order'] = filters_serializer.data

    return Response(about_order)

@swagger_auto_schema(method='put', request_body=FilterOrderSerializer)
@api_view(["PUT"])
def update_order_filter(request, order_id, filter_id):              # изменение мощности
    if not FilterOrder.objects.filter(filter_id=filter_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=order_id)

    if order.status != 1:
        return Response(status=status.HTTP_403_FORBIDDEN)

    item = FilterOrder.objects.get(filter_id=filter_id, order_id=order_id)

    serializer = FilterOrderSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_image(request, id):
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)

    return HttpResponse(filter.image, content_type="image/png")

@swagger_auto_schema(method='put', request_body=FiltersSerializer)
@api_view(["PUT"])
def update_image(request, id):
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    serializer = FiltersSerializer(filter, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return HttpResponse(filter.image, content_type="image/png")