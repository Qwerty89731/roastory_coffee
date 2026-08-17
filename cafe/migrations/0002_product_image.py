from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "cafe",
            "0001_initial",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True,
                default="products/default.webp",
                help_text=(
                    "Лучше использовать квадратное фото "
                    "размером от 900 × 900 px."
                ),
                upload_to="products/",
                verbose_name="Фотография",
            ),
        ),
    ]
