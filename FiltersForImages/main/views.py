import uuid
import requests
from django.db.models import Q
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from .permissions import *
from django.http import JsonResponse
import json

key = "ndscL3Jwp9kMNjknk12"

class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    model_class = Users

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsModerator]
        return [permission() for permission in permission_classes]

    def create(self, request):
        if self.model_class.objects.filter(login=request.data['login']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(login=serializer.data['login'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     role=serializer.data['role'],
                                     first_name=serializer.data['first_name'],
                                     last_name=serializer.data['last_name'],
                                     email=serializer.data['email'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

@swagger_auto_schema(
    request_body=UsersSerializer,
    method='POST',
    operation_summary="Регистрация пользователя в системе",
    operation_description="Сервер отправляет сессию пользователя в виде cookies",
    responses={
        200: 'Успешная регистрация',
        400: 'Неверный логин или пароль'
    })
@authentication_classes([])
@api_view(['POST'])
@permission_classes([IsAnon])
def login_view(request):
    login_value = request.data["login"]
    password = request.data["password"]
    user = authenticate(request, login=login_value, password=password)
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, login_value)
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "login": user.login,
            "password": user.password,
            "email": user.email,
            "role": user.role,
        }
        response = Response(user_data, status=status.HTTP_200_OK)
        response.set_cookie("session_id", random_key)
        return response
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='POST',
    operation_summary="Выход из системы",
    operation_description="Удаления данных из Redis и Cookie",
    responses={
        200: 'Сеанс Завершен',
        400: 'Bad Request'
    })
@api_view(['POST'])
@permission_classes([IsAuth])
def logout_view(request):
    ssid = request.COOKIES.get("session_id")
    if ssid is not None:
        if session_storage.exists(ssid):
            session_storage.delete(ssid)
            response = Response({'detail': 'Сеанс завершен'}, status=status.HTTP_200_OK)
            response.delete_cookie("session_id")
            return response
    return Response({'detail': 'Bad Request'}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='GET',
    operation_summary="Фильтры",
    operation_description="Список неудаленных фильтров по поиску. Также выводится id черновой заявки, если пользователь авторизован. Доступно всем посетителям сайта",
    responses={
        200: 'Успех'
    })
@api_view(['GET'])
@permission_classes([AllowAny])
def filters_list(request):                          # список неудаленных фильтров
    input_text = request.GET.get('search-filter')
    filters = Filters.objects.filter(name__icontains=input_text).filter(status=1) if input_text else Filters.objects.filter(status=1)
    ssid = request.COOKIES.get("session_id", None)
    if ssid is not None:
        user_name = session_storage.get(ssid).decode('utf-8')
        user_object = Users.objects.get(login=user_name)
        order = Orders.objects.filter(Q(status=1) & Q(owner=user_object)).first()
    else:
        order = False

    serializer = FiltersSerializer(filters, many=True)

    res = {
        "filters": serializer.data,
        "draft_order": order.id if order else None,
    }

    return Response(res, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='GET',
    operation_summary="Фильтр по id",
    operation_description="Выбранный фильтр. Доступно всем посетителям сайта",
    responses={
        200: 'Успех',
        404: 'Фильтр не найден'
    })
@api_view(['GET'])
@permission_classes([AllowAny])
def one_filter(request, id):                        # получение одного фильтра по id
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    if filter.status == 2:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = FiltersSerializer(filter)

    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    request_body=FiltersSerializer,
    method='POST',
    operation_summary="Создание фильтра",
    operation_description="Доступно только модератору",
    responses={
        201: 'Успех',
        400: 'Неверные данные'
    })
@api_view(['POST'])
@permission_classes([IsModerator])
def create_filter(request):                         # создание фильтра
    serializer = FiltersSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        filters = Filters.objects.filter(status=1)
        serializer = FiltersSerializer(filters, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    request_body=FiltersSerializer,
    method='PUT',
    operation_summary="Изменение фильтра",
    operation_description="Неизмененные данные сохраняются. Доступно только модератору",
    responses={
        200: 'Успех',
        400: 'Неверные данные',
        404: 'Фильтр не найден'
    })
@api_view(['PUT'])
@permission_classes([IsModerator])
def update_filter(request, id):                     # обновление данных о фильтре
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    if filter.status == 2:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = FiltersSerializer(filter, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Удаление фильтра",
    operation_description="Доступно только модератору",
    responses={
        200: 'Успех',
        404: 'Фильтр не найден'
    })
@api_view(['DELETE'])
@permission_classes([IsModerator])
def delete_filter(request, id):                         # удаление фильтра
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    filter.status = 2
    filter.save()

    filters = Filters.objects.filter(status=1)
    serializer = FiltersSerializer(filters, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='POST',
    operation_summary="Добавление фильтра в заявку",
    operation_description="Доступно только обычному пользователю",
    responses={
        200: 'Успех',
        404: 'Фильтр не найден',
        409: 'Конфликт'
    })
@api_view(['POST'])
@permission_classes([IsUser])
def add_to_order(request, id):                          # добавление фильтра в заявку
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    ssid = request.COOKIES.get("session_id", None)
    filter = Filters.objects.get(id=id)
    user_name = session_storage.get(ssid).decode('utf-8')
    user = Users.objects.get(login=user_name)
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

    return Response(about_order, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='GET',
    operation_summary="Список заявок",
    operation_description="Получение всех заявок, кроме удаленный и черновых. Фильтрация по статусу и дате создания. Доступно только авторизованным пользователям",
    responses={
        200: 'Успех'
    })
@api_view(['GET'])
@permission_classes([IsAuth])
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

    ssid = request.COOKIES.get("session_id", None)
    user_name = session_storage.get(ssid).decode('utf-8')
    user_object = Users.objects.get(login=user_name)

    if user_object.role == False:
        orders = orders.filter(owner=user_object)
    serializers = OrdersSerializer(orders, many=True)

    return Response(serializers.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='GET',
    operation_summary="Заявка по id",
    operation_description="Получение выбранной заявки. Доступно только авторизованным пользователям. Обычный пользователь получает все срзданные им заявки, модератор все существующие заявки, кроме черновика",
    responses={
        200: 'Успех',
        404: 'Заявка не найдена'
    })
@api_view(['GET'])
@permission_classes([IsAuth])
def one_order(request, id):                                 # заявка по id + ее услуги
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)

    ssid = request.COOKIES.get("session_id", None)
    user_name = session_storage.get(ssid).decode('utf-8')
    user_object = Users.objects.get(login=user_name)

    if user_object.role == False:
        if order.owner != user_object:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        if order.status == 1:
            return Response(status=status.HTTP_404_NOT_FOUND)

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

@swagger_auto_schema(
    method='PUT',
    operation_summary="Формирование заявки",
    operation_description="Сформировать можно только черновую заявку. Доступно только обычному пользователю",
    responses={
        200: 'Успех',
        403: 'Ошибка доступа',
        404: 'Фильтр не найден',
        409: 'Конфликт'
    })
@api_view(["PUT"])
@permission_classes([IsUser])
def update_status_owner(request, id):                           # формирование заявки
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)

    if order.status != 1:
        return Response(status=status.HTTP_409_CONFLICT)

    ssid = request.COOKIES.get("session_id", None)
    user_name = session_storage.get(ssid).decode('utf-8')
    user_object = Users.objects.get(login=user_name)

    if order.owner != user_object:
        return Response(status=status.HTTP_403_FORBIDDEN)

    order.status = 2
    order.date_formation = timezone.now()

    if 'image' in request.FILES:
        order.image = request.FILES['image']

    order.save()

    response = requests.post('http://localhost:8080/edit_image/', data={'id': id, 'key': key})

    serializer = OrdersSerializer(order)

    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    request_body=OrdersSerializer,
    method='PUT',
    operation_summary="Одобрение/отказ заявки",
    operation_description="Выполнить можно только для сформированой заявки. Доступно только модератору",
    responses={
        200: 'Успех',
        403: 'Ошибка доступа',
        404: 'Фильтр не найден',
        409: 'Конфликт'
    })
@api_view(["PUT"])
@permission_classes([IsModerator])
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

    ssid = request.COOKIES.get("session_id", None)
    moder_name = session_storage.get(ssid).decode('utf-8')
    moderator = Users.objects.get(login=moder_name)
    order.moderator = moderator
    order.date_complete = timezone.now()
    order.status = request_status
    order.save()

    serializer = OrdersSerializer(order)

    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Удаление заявки",
    operation_description="Выполнить можно только для черновой заявки. Доступно только обычному пользователю и только ее владельцу",
    responses={
        200: 'Успех',
        403: 'Ошибка доступа',
        404: 'Заявка не найдена'
    })
@api_view(["DELETE"])
@permission_classes([IsUser])
def delete_order(request, id):                          # удаление черновой заявки
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)

    if order.status != 1:
        return Response(status=status.HTTP_403_FORBIDDEN)

    ssid = request.COOKIES.get("session_id", None)
    user_name = session_storage.get(ssid).decode('utf-8')
    user_object = Users.objects.get(login=user_name)

    if order.owner != user_object:
        return Response(status=status.HTTP_403_FORBIDDEN)

    order.status = 5
    order.save()

    return Response(status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='DELETE',
    operation_summary="Удаление заявки",
    operation_description="Выполнить можно только для черновой заявки. Доступно только обычному пользователю",
    responses={
        200: 'Успех',
        403: 'Ошибка доступа',
        404: 'Заявка не найдена'
    })
@api_view(["DELETE"])
@permission_classes([IsUser])
def delete_filter_from_order(request, filter_id, order_id):                     # удаление фильтра из черновой заявки
    if not FilterOrder.objects.filter(filter_id=filter_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=order_id)

    ssid = request.COOKIES.get("session_id", None)
    user_name = session_storage.get(ssid).decode('utf-8')
    user_object = Users.objects.get(login=user_name)

    if order.owner != user_object:
        return Response(status=status.HTTP_403_FORBIDDEN)

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

    return Response(about_order, status=status.HTTP_200_OK)

@swagger_auto_schema(
    request_body=FilterOrderSerializer,
    method='PUT',
    operation_summary="Изменение мощности",
    operation_description="Выполнить можно только для черновой заявки. Доступно только обычному пользователю и ее создателю",
    responses={
        200: 'Успех',
        400: 'Неверные данные',
        403: 'Ошибка доступа',
        404: 'Заявка не найдена'
    })
@api_view(["PUT"])
@permission_classes([IsUser])
def update_order_filter(request, order_id, filter_id):              # изменение мощности
    if not FilterOrder.objects.filter(filter_id=filter_id, order_id=order_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=order_id)

    ssid = request.COOKIES.get("session_id", None)
    user_name = session_storage.get(ssid).decode('utf-8')
    user_object = Users.objects.get(login=user_name)

    if order.owner != user_object:
        return Response(status=status.HTTP_403_FORBIDDEN)

    if order.status != 1:
        return Response(status=status.HTTP_403_FORBIDDEN)

    item = FilterOrder.objects.get(filter_id=filter_id, order_id=order_id)

    serializer = FilterOrderSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='GET',
    operation_summary="Изображение фильтра",
    operation_description="Доступно всем пользователям",
    responses={
        200: 'Успех',
        404: 'Фильтр не найден'
    })
@api_view(["GET"])
@permission_classes([AllowAny])
def get_image(request, id):
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)

    return HttpResponse(filter.image, content_type="image/png")

@swagger_auto_schema(
    method='PUT',
    operation_summary="Изменение изображения",
    operation_description="Доступно только модератору",
    responses={
        200: 'Успех',
        404: 'Фильтр не найден'
    })
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_image(request, id):
    if not Filters.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    filter = Filters.objects.get(id=id)
    serializer = FiltersSerializer(filter, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return HttpResponse(filter.image, content_type="image/png")

@api_view(["GET"])
def get_order_image(request, id):
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)

    return HttpResponse(order.image, content_type="image/png")

@api_view(["PUT"])
def update_order_image(request, id):
    if not Orders.objects.filter(id=id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    getKey = request.data['key']
    if getKey != key:
        return Response(status=status.HTTP_404_NOT_FOUND)

    order = Orders.objects.get(id=id)
    order.image = request.FILES['image']
    order.save()

    return HttpResponse(order.image, content_type="image/png")