# Generated by Django 4.2.3 on 2023-07-20 16:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0018_user_is_backend_user_is_frontend_user_is_hr_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FailedLoginAttempt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("attempt_count", models.PositiveIntegerField(default=1)),
                ("last_attempt_time", models.DateTimeField(auto_now_add=True)),
                ("block_after_attempts", models.PositiveIntegerField(default=3)),
                ("is_blocked", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
