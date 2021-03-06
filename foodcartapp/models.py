from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    lon = models.FloatField(verbose_name="долгота")
    lat = models.FloatField(verbose_name="широта")

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class CustomQuerySet(models.QuerySet):
    def calculate_total_cost_of_order_items(self):
        order = self.annotate(summa=Sum('items__cost'))
        return order


class Order(models.Model):
    CHOICES_STATUS_ORDER = [
        ('Необработанный', 'Необработанный'),
        ('Сборка', 'Сборка'),
        ('Доставка', 'Доставка'),
        ('Завершен', 'Завершен')

    ]
    CHOICES_PAYMENT_METHOD = [
        ('Электронно', 'Электронно'),
        ('Наличностью', 'Наличностью'),
    ]
    status = models.CharField(
        max_length=50,
        choices=CHOICES_STATUS_ORDER,
        verbose_name='статус',
        default='Необработанный',
        db_index=True
    )
    firstname = models.CharField(
        max_length=200,
        verbose_name="имя",
        db_index=True
        )
    lastname = models.CharField(
        max_length=200,
        verbose_name="фамилия",
        db_index=True
        )
    phonenumber = PhoneNumberField()
    address = models.CharField(
        max_length=500,
        verbose_name="адрес доставки",
        db_index=True
        )
    comment = models.TextField(
        blank=True,
        verbose_name="комментарий"
    )
    payment_method = models.CharField(
        max_length=500,
        choices=CHOICES_PAYMENT_METHOD,
        verbose_name="способ оплаты",
        db_index=True,
        default='Электронно'
        )
    registration_time = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата и время регистрации'
    )
    call_time = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name='дата и время звонка'
    )
    delivery_time = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name='дата и время доставки'
    )
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    custom_manager = CustomQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"Заказ №{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='номер заказа',
        db_index=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='позиция в заказе',
    )
    quantity = models.IntegerField(default=1)
    cost = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="стоимость"
        )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'
        unique_together = [
            ['order', 'product']
        ]

    def __str__(self):
        return f"Заказ №{self.order.id} - {self.product.name}"


class GeoPositionAddress(models.Model):
    address = models.CharField(
        max_length=500,
        verbose_name="адрес доставки",
        db_index=True,
        unique=True
        )
    lon = models.FloatField(verbose_name="долгота")
    lat = models.FloatField(verbose_name="широта")

    class Meta:
        verbose_name = 'координаты адресов заказов'
        verbose_name_plural = 'координаты адреса заказа'
        unique_together = [
            ['lon', 'lat']
        ]

    def __str__(self):
        return f"{self.address}[{self.lon}, {self.lat}]"
