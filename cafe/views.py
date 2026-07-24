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