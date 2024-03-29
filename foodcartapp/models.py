from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum
from django.core.validators import MinValueValidator


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
        orders = self.annotate(sum=Sum('items__order_position_total_cost'))
        return orders

    def find_available_restaurans(self, restaurants_menu):
        orders = self
        for order in orders:
            available_restaurants_in_order = []
            pending_order_items = order.items.all()
            pending_order_producs = [
                pending_order_item.product
                for pending_order_item in pending_order_items
                ]
            for product in pending_order_producs:
                available_restaurants_for_product = [
                    menu_item.restaurant
                    for menu_item in restaurants_menu
                    if menu_item.product == product
                ]
                available_restaurants_in_order.append(
                    set(available_restaurants_for_product)
                    )
            order.available_restaurants = list(
                available_restaurants_in_order[0].intersection(
                    *available_restaurants_in_order[1:]
                    )
                )
        return orders


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
    phonenumber = PhoneNumberField(verbose_name="номер телефона")
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
        max_length=150,
        choices=CHOICES_PAYMENT_METHOD,
        verbose_name="способ оплаты",
        db_index=True,
        default='Не выбран'
        )
    registration_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата и время регистрации'
    )
    call_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name='дата и время звонка'
    )
    delivery_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name='дата и время доставки'
    )
    fulfilling_restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="ресторан выполняющий заказ",
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
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
        )
    order_position_total_cost = models.DecimalField(
        decimal_places=2,
        max_digits=6,
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
    lon = models.FloatField(verbose_name="долгота", blank=True, null=True)
    lat = models.FloatField(verbose_name="широта", blank=True, null=True)

    class Meta:
        verbose_name = 'координаты адресов заказов'
        verbose_name_plural = 'координаты адреса заказа'
        unique_together = [
            ['lon', 'lat']
        ]

    def __str__(self):
        return f"{self.address}[{self.lon}, {self.lat}]"
