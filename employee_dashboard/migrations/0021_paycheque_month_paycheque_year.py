# Generated by Django 4.2.3 on 2023-07-25 06:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("employee_dashboard", "0020_alter_paycheque_employee"),
    ]

    operations = [
        migrations.AddField(
            model_name="paycheque",
            name="month",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="paycheque",
            name="year",
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
