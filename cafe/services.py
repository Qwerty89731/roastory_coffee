from decimal import Decimal

from django.db import transaction

from .models import (
    Order,
    OrderItem,
)


@transaction.atomic
def create_order(user, cart, cleaned_data):
    """
    Создает заказ из корзины.
    """

    subtotal = Decimal(cart.subtotal)

    delivery_type = cleaned_data["delivery_type"]

    # Самовывоз — доставка бесплатная.
    # Доставку пока считаем бесплатной.
    delivery_cost = Decimal("0")

    total = subtotal + delivery_cost

    order = Order.objects.create(
        user=user,
        status=Order.Status.NEW,
        delivery_type=delivery_type,
        payment_method=cleaned_data["payment_method"],
        customer_name=cleaned_data["customer_name"],
        phone=cleaned_data["phone"],
        address=cleaned_data.get("address", ""),
        entrance=cleaned_data.get("entrance", ""),
        comment=cleaned_data.get("comment", ""),
        subtotal=subtotal,
        delivery_cost=delivery_cost,
        bonuses_used=0,
        bonuses_earned=0,
        total=total,
    )

    for item in cart.items():
        product = item["product"]
        quantity = item["quantity"]

        OrderItem.objects.create(
            order=order,
            product=product,
            name=product.name,
            price=product.price,
            quantity=quantity,
        )

    cart.clear()

    return order
