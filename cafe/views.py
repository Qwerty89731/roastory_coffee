from django.shortcuts import render


def home(request):
    return render(request, "cafe/home.html")


def menu(request):
    return render(request, "cafe/menu.html")


def reviews(request):
    return render(request, "cafe/reviews.html")


def cart(request):
    return render(request, "cafe/cart.html")


def profile(request):
    return render(request, "cafe/profile.html")

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Avg
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import (
    CheckoutForm,
    LoginForm,
    ReviewForm,
    SignUpForm,
)
from .models import (
    BonusTransaction,
    Category,
    Order,
    Product,
    Review,
)
from .services import create_order


def home(request):
    featured = (
        Product.objects
        .filter(
            is_available=True,
            is_featured=True,
        )
        .select_related("category")[:6]
    )

    reviews = (
        Review.objects
        .filter(is_approved=True)
        .select_related("user")[:3]
    )

    rating = (
        Review.objects
        .filter(is_approved=True)
        .aggregate(value=Avg("rating"))["value"]
        or 5
    )

    context = {
        "featured": featured,
        "reviews": reviews,
        "rating": rating,
    }

    return render(
        request,
        "cafe/home.html",
        context,
    )


def menu(request):
    categories = Category.objects.prefetch_related(
        "products"
    )

    active = request.GET.get("category", "")

    products = (
        Product.objects
        .filter(is_available=True)
        .select_related("category")
    )

    if active:
        products = products.filter(
            category__slug=active
        )

    context = {
        "categories": categories,
        "products": products,
        "active": active,
    }

    return render(
        request,
        "cafe/menu.html",
        context,
    )


class CafeLoginView(LoginView):
    """Страница входа."""

    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(
            self.request,
            "Вы вошли в личный кабинет.",
        )

        return super().form_valid(form)


class CafeLogoutView(LogoutView):
    """Выход из аккаунта."""

    pass


def signup(request):
    """Регистрация нового пользователя."""

    if request.user.is_authenticated:
        return redirect("profile")

    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()

        BonusTransaction.objects.create(
            profile=user.profile,
            amount=300,
            description="Приветственные бонусы",
        )

        login(request, user)

        messages.success(
            request,
            (
                "Добро пожаловать! Мы уже начислили "
                "вам 300 приветственных бонусов."
            ),
        )

        return redirect("profile")

    return render(
        request,
        "registration/signup.html",
        {"form": form},
    )


def cart_detail(request):
    cart = Cart(request)

    subtotal = cart.subtotal

    delivery_cost = (
        0
        if subtotal >= 1500 or subtotal == 0
        else 199
    )

    free_delivery_left = max(
        0,
        Decimal("1500") - subtotal,
    )

    context = {
        "cart_items": cart.items(),
        "subtotal": subtotal,
        "delivery_cost": delivery_cost,
        "free_delivery_left": free_delivery_left,
    }

    return render(
        request,
        "cafe/cart.html",
        context,
    )


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_available=True,
    )

    try:
        quantity = int(
            request.POST.get("quantity", 1)
        )
    except (TypeError, ValueError):
        quantity = 1

    Cart(request).add(
        product.pk,
        quantity,
    )

    messages.success(
        request,
        f"«{product.name}» добавлен в корзину",
    )

    next_url = request.POST.get("next", "")

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
    ):
        return redirect(next_url)

    return redirect("menu")


@require_POST
def cart_update(request, product_id):
    try:
        quantity = int(
            request.POST.get("quantity", 1)
        )
    except (TypeError, ValueError):
        quantity = 1

    Cart(request).update(
        product_id,
        quantity,
    )

    return redirect("cart")


@require_POST
def cart_remove(request, product_id):
    Cart(request).update(product_id, 0)

    return redirect("cart")


@login_required
def checkout(request):
    cart = Cart(request)

    if not cart.items():
        messages.info(
            request,
            "Сначала добавьте что-нибудь из меню",
        )

        return redirect("menu")

    initial = {
        "customer_name": (
            request.user.first_name
            or request.user.username
        ),
        "phone": request.user.profile.phone,
        "delivery_type": (
            Order.DeliveryType.DELIVERY
        ),
        "payment_method": Order.Payment.CARD,
    }

    form = CheckoutForm(
        request.POST or None,
        initial=initial,
    )

    if request.method == "POST" and form.is_valid():
        order = create_order(
            user=request.user,
            cart=cart,
            cleaned_data=form.cleaned_data.copy(),
        )

        messages.success(
            request,
            "Заказ принят — начинаем готовить!",
        )

        return redirect(
            "order_success",
            order_id=order.pk,
        )

    subtotal = cart.subtotal

    max_bonus = min(
        request.user.profile.bonus_balance,
        int(subtotal * Decimal("0.30")),
    )

    context = {
        "form": form,
        "cart_items": cart.items(),
        "subtotal": subtotal,
        "max_bonus": max_bonus,
    }

    return render(
        request,
        "cafe/checkout.html",
        context,
    )


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
        user=request.user,
    )

    return render(
        request,
        "cafe/order_success.html",
        {"order": order},
    )


@login_required
def profile(request):
    orders = (
        request.user.orders
        .prefetch_related("items")[:10]
    )

    transactions = (
        request.user.profile
        .bonus_transactions.all()[:8]
    )

    context = {
        "orders": orders,
        "transactions": transactions,
    }

    return render(
        request,
        "cafe/profile.html",
        context,
    )


def reviews(request):
    published = (
        Review.objects
        .filter(is_approved=True)
        .select_related("user")
    )

    form = (
        ReviewForm()
        if request.user.is_authenticated
        else None
    )

    context = {
        "reviews": published,
        "form": form,
    }

    return render(
        request,
        "cafe/reviews.html",
        context,
    )


@login_required
@require_POST
def review_add(request):
    form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.save()

        messages.success(
            request,
            (
                "Спасибо! Отзыв появится после "
                "проверки администратором."
            ),
        )
    else:
        messages.error(
            request,
            "Проверьте оценку и текст отзыва",
        )

    return redirect("reviews")
