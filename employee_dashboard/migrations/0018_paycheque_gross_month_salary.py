# Generated by Django 4.2.3 on 2023-07-24 10:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("employee_dashboard", "0017_remove_paycheque_allowances_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="paycheque",
            name="gross_month_salary",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
