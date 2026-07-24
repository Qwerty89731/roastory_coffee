from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


class Profile(models.Model):
    """
    Дополнительная информация о пользователе.
    """

    user = models.OneToOneField(
            User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    phone = models.CharField(
        "Телефон",
        max_length=24,
        blank=True,
    )

    birthday = models.DateField(
        "Дата рождения",
        null=True,
        blank=True,
    )

    bonus_balance = models.PositiveIntegerField(
        "Бонусы",
        default=300,
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user.username}"


class Category(models.Model):
    """
    Категория меню: кофе, выпечка, завтраки и т. д.
    """

    name = models.CharField(
        "Название",
        max_length=80,
    )

    slug = models.SlugField(
        "Слаг",
        unique=True,
    )

    order = models.PositiveSmallIntegerField(
        "Порядок",
        default=0,
    )

    class Meta:
        ordering = ("order", "name")
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Товар из меню кофейни.
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    name = models.CharField(
        "Название",
        max_length=120,
    )

    slug = models.SlugField(
        "Слаг",
        unique=True,
    )

    description = models.TextField(
        "Описание",
        max_length=500,
    )

    price = models.DecimalField(
        "Цена",
        max_digits=8,
        decimal_places=2,
    )

    volume = models.CharField(
        "Объём или вес",
        max_length=30,
        blank=True,
    )
    
    emoji = models.CharField(
        "Эмодзи",
        max_length=8,
        default="☕",
    )

    accent = models.CharField(
        "Цвет",
        max_length=20,
        default="#dca15d",
    )

    is_featured = models.BooleanField(
        "Показывать на главной",
        default=False,
    )

    is_available = models.BooleanField(
        "В наличии",
        default=True,
    )

    class Meta:
        ordering = ("category__order", "name")
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Заказ пользователя.
    """

    class Status(models.TextChoices):
        NEW = "new", "Принят"
        COOKING = "cooking", "Готовится"
        ON_THE_WAY = "on_the_way", "В пути"
        COMPLETED = "completed", "Выполнен"
        CANCELLED = "cancelled", "Отменён"

    class DeliveryType(models.TextChoices):
        DELIVERY = "delivery", "Доставка"
        PICKUP = "pickup", "Самовывоз"

    
    class Payment(models.TextChoices):
        CARD = "card", "Картой при получении"
        CASH = "cash", "Наличными"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    delivery_type = models.CharField(
        "Способ получения",
        max_length=12,
        choices=DeliveryType.choices,
    )

    payment_method = models.CharField(
        "Способ оплаты",
        max_length=12,
        choices=Payment.choices,
    )

    customer_name = models.CharField(
        "Имя",
        max_length=120,
    )

    phone = models.CharField(
        "Телефон",
        max_length=24,
    )

    address = models.CharField(
        "Адрес",
        max_length=250,
        blank=True,
    )

    entrance = models.CharField(
        "Подъезд, этаж, квартира",
        max_length=80,
        blank=True,
    )

    comment = models.TextField(
        "Комментарий",
        max_length=500,
        blank=True,
    )

    subtotal = models.DecimalField(
        "Стоимость товаров",
        max_digits=10,
        decimal_places=2,
    )

    delivery_cost = models.DecimalField(
        "Стоимость доставки",
        max_digits=8,
        decimal_places=2,
        default=0,
    )

    bonuses_used = models.PositiveIntegerField(
        "Списано бонусов",
        default=0,
    )

    bonuses_earned = models.PositiveIntegerField(
        "Начислено бонусов",
        default=0,
    )

    total = models.DecimalField(
        "Итого",
        max_digits=10,
        decimal_places=2,
    )

    created_at = models.DateTimeField(
        "Создан",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


    def __str__(self):
        return f"Заказ №{self.pk}"


class OrderItem(models.Model):
    """
    Отдельная позиция внутри заказа.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )

    name = models.CharField(
        "Название",
        max_length=120,
    )

    price = models.DecimalField(
        "Цена",
        max_digits=8,
        decimal_places=2,
    )

    quantity = models.PositiveSmallIntegerField(
        "Количество",
    )

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.name} × {self.quantity}"


class BonusTransaction(models.Model):
    """
    История начисления и списания бонусов.
    """

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="bonus_transactions",
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    amount = models.IntegerField(
        "Изменение баланса",
    )

    description = models.CharField(
        "Описание",
        max_length=160,
    )

    created_at = models.DateTimeField(
        "Дата",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Бонусная операция"
        verbose_name_plural = "Бонусные операции"

    def __str__(self):
        return f"{self.description}: {self.amount}"


class Review(models.Model):
    """
    Отзыв пользователя.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    rating = models.PositiveSmallIntegerField(
        "Оценка",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    text = models.TextField(
        "Отзыв",
        max_length=1000,
    )

    is_approved = models.BooleanField(
        "Опубликован",
        default=False,
    )

    created_at = models.DateTimeField(
        "Дата",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return (
            f"Отзыв {self.user.username}: "
            f"{self.rating}/5"
        )



