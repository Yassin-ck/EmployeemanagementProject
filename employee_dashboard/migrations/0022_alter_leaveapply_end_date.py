# Generated by Django 4.2.3 on 2023-07-25 16:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("employee_dashboard", "0021_paycheque_month_paycheque_year"),
    ]

    operations = [
        migrations.AlterField(
            model_name="leaveapply",
            name="end_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
