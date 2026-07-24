from django.contrib import admin

from .models import (
    BonusTransaction,
    Category,
    Order,
    OrderItem,
    Product,
    Profile,
    Review,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "is_available",
        "is_featured",
    )

    list_filter = (
        "category",
        "is_available",
        "is_featured",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "order",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "name",
        "price",
        "quantity",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "status",
        "delivery_type",
        "total",
        "created_at",
    )

    list_filter = (
        "status",
        "delivery_type",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "phone",
        "address",
    )

    inlines = (
        OrderItemInline,
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "rating",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "is_approved",
        "rating",
    )

    actions = (
        "approve",
    )

    @admin.action(
        description="Опубликовать выбранные отзывы"
    )
    def approve(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
        "bonus_balance",
    )

    search_fields = (
        "user__username",
        "phone",
    )


@admin.register(BonusTransaction)
class BonusTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "amount",
        "description",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

