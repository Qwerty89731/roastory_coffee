from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('reviews/', views.reviews, name='reviews'),
    path('cart/', views.cart, name='cart'),
    path('profile/', views.profile, name='profile'),
]