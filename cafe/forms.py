from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from .models import Order, Review


class StyledFormMixin:
    """Добавляет CSS-класс всем полям формы."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(
                field.widget,
                (forms.CheckboxInput, forms.RadioSelect),
            ):
                continue

            field.widget.attrs.setdefault(
                "class",
                "form-control",
            )


class SignUpForm(StyledFormMixin, UserCreationForm):
    """Форма регистрации пользователя."""

    first_name = forms.CharField(
        label="Имя",
        max_length=80,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "given-name",
                "placeholder": "Например, Анна",
            }
        ),
    )

    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "name@example.com",
            }
        ),
    )

    phone = forms.CharField(
        label="Телефон",
        max_length=24,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "tel",
                "inputmode": "tel",
                "placeholder": "+7 999 000-00-00",
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User

        fields = (
            "first_name",
            "email",
            "phone",
            "username",
            "password1",
            "password2",
        )

        labels = {
            "username": "Логин",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "autocomplete": "username",
                "placeholder": "Придумайте логин",
            }
        )

        self.fields["password1"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "placeholder": "Не менее 8 символов",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "placeholder": "Повторите пароль",
            }
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "Аккаунт с таким e-mail уже существует."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            user.profile.phone = self.cleaned_data["phone"]

            user.profile.save(
                update_fields=["phone"]
            )

        return user


class LoginForm(StyledFormMixin, AuthenticationForm):
    """Форма входа пользователя."""

    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
                "placeholder": "Ваш логин",
            }
        ),
    )

    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": "Ваш пароль",
            }
        ),
    )


class CheckoutForm(StyledFormMixin, forms.ModelForm):
    """Форма оформления заказа."""

    use_bonus = forms.BooleanField(
        label="Списать доступные бонусы",
        required=False,
    )

    class Meta:
        model = Order

        fields = (
            "delivery_type",
            "customer_name",
            "phone",
            "address",
            "entrance",
            "payment_method",
            "comment",
        )

        widgets = {
            "delivery_type": forms.RadioSelect,
            "payment_method": forms.RadioSelect,
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Убираем пустой вариант Django "---------"
        # чтобы не появлялся лишний самовывоз
        self.fields["delivery_type"].choices = (
            ("delivery", "Доставка"),
            ("pickup", "Самовывоз"),
        )

    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data.get("delivery_type")
            == Order.DeliveryType.DELIVERY
            and not cleaned_data.get("address")
        ):
            self.add_error(
                "address",
                "Укажите адрес доставки",
            )

        return cleaned_data


class ReviewForm(StyledFormMixin, forms.ModelForm):
    """Форма отзыва."""

    rating = forms.TypedChoiceField(
        label="Оценка",
        choices=[
            (5, "5 — великолепно"),
            (4, "4 — хорошо"),
            (3, "3 — нормально"),
            (2, "2 — плохо"),
            (1, "1 — ужасно"),
        ],
        coerce=int,
    )

    class Meta:
        model = Review

        fields = (
            "rating",
            "text",
        )

        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": (
                        "Расскажите о впечатлениях…"
                    ),
                }
            )
        }