# Generated by Django 4.2.3 on 2023-07-31 15:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("employee_dashboard", "0022_alter_leaveapply_end_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="profile_picture",
            field=models.ImageField(blank=True, null=True, upload_to="userprofile/"),
        ),
    ]
