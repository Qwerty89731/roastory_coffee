from decimal import Decimal

from .models import Product


class Cart:
    """
    Корзина пользователя на основе Django session.
    """

    SESSION_KEY = "cart"

    def __init__(self, request):
        self.session = request.session

        cart = self.session.get(self.SESSION_KEY)

        if cart is None:
            cart = self.session[self.SESSION_KEY] = {}

        self.cart = cart

    def add(self, product_id, quantity=1):
        product_id = str(product_id)

        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity

        self.save()

    def update(self, product_id, quantity):
        product_id = str(product_id)

        if quantity > 0:
            self.cart[product_id] = quantity
        else:
            self.cart.pop(product_id, None)

        self.save()

    def remove(self, product_id):
        product_id = str(product_id)

        self.cart.pop(product_id, None)

        self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True

    def items(self):
        """
        Возвращает товары корзины.
        """

        products = Product.objects.filter(
            id__in=self.cart.keys()
        )

        items = []

        for product in products:
            quantity = self.cart[str(product.id)]

            items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "total_price": (
                        product.price
                        * quantity
                    ),
                }
            )

        return items

    @property
    def subtotal(self):
        total = Decimal("0")

        for item in self.items():
            total += item["total_price"]

        return total