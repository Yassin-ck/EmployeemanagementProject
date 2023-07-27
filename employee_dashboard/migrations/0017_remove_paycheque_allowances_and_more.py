# Generated by Django 4.2.3 on 2023-07-24 09:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("employee_dashboard", "0016_notice_board_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paycheque",
            name="allowances",
        ),
        migrations.RemoveField(
            model_name="paycheque",
            name="base_salary",
        ),
        migrations.RemoveField(
            model_name="paycheque",
            name="bonus",
        ),
        migrations.RemoveField(
            model_name="paycheque",
            name="employer",
        ),
        migrations.RemoveField(
            model_name="paycheque",
            name="overtime_hours",
        ),
        migrations.RemoveField(
            model_name="paycheque",
            name="overtime_pay_rate",
        ),
        migrations.RemoveField(
            model_name="paycheque",
            name="salary",
        ),
        migrations.RemoveField(
            model_name="paycheque",
            name="user",
        ),
        migrations.AddField(
            model_name="paycheque",
            name="annual_income",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="employee_dashboard.userprofile",
            ),
        ),
        migrations.AddField(
            model_name="paycheque",
            name="employee",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="paycheque",
            name="incentives",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="paycheque",
            name="month_salary",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="paycheque",
            name="deductions",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
