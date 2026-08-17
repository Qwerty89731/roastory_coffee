from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),
    path(
        "menu/",
        views.menu,
        name="menu",
    ),

    path(
        "cart/",
        views.cart_detail,
        name="cart",
    ),
    path(
        "cart/add/<int:product_id>/",
        views.cart_add,
        name="cart_add",
    ),
    path(
        "cart/update/<int:product_id>/",
        views.cart_update,
        name="cart_update",
    ),
    path(
        "cart/remove/<int:product_id>/",
        views.cart_remove,
        name="cart_remove",
    ),

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),
    path(
        "orders/<int:order_id>/success/",
        views.order_success,
        name="order_success",
    ),

    path(
        "account/",
        views.profile,
        name="profile",
    ),

    path(
        "reviews/",
        views.reviews,
        name="reviews",
    ),
    path(
        "reviews/add/",
        views.review_add,
        name="review_add",
    ),

    path(
        "signup/",
        views.signup,
        name="signup",
    ),
    path(
        "login/",
        views.CafeLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        views.CafeLogoutView.as_view(),
        name="logout",
    ),
]
