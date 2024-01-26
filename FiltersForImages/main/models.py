from django.db import models
from django.utils import timezone

class Filters(models.Model):
    STATUS_CHOICES = [
        (1, 'Действует'),
        (2, 'Удалена'),
    ]

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.CharField(max_length=500, verbose_name="Описание")
    price = models.IntegerField(default=40, verbose_name="Цена")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(upload_to="filters", default="filters/default.jpg", verbose_name="Фото")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name="Фильтр"
        verbose_name_plural="Фильтры"

class Orders(models.Model):
    STATUS_CHOICES = [
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален'),
    ]

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(blank=True, null=True, verbose_name="Дата формирования")
    date_complete = models.DateTimeField(blank=True, null=True, verbose_name="Дата завершения")
    owner = models.ForeignKey("Users", on_delete=models.DO_NOTHING, blank=True, null=True, related_name="owner", verbose_name="Создатель")
    moderator = models.ForeignKey("Users", on_delete=models.DO_NOTHING, blank=True, null=True, related_name="moderator", verbose_name="Модератор")

    def __str__(self):
        return "Заказ №" + str(self.pk)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class Users(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    login = models.CharField(max_length=50, verbose_name="Логин")
    password = models.CharField(max_length=50, verbose_name="Пароль")
    email = models.CharField(max_length=50, verbose_name="Почта")
    role = models.BooleanField(default=False)

    def __str__(self):
        return self.login

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class FilterOrder(models.Model):
    filter = models.ForeignKey("Filters", on_delete=models.CASCADE)
    order = models.ForeignKey("Orders", on_delete=models.CASCADE)
    power = models.FloatField(verbose_name="Мощность")

    def __str__(self):
        return "Фильтр-Заказ №" + str(self.pk)