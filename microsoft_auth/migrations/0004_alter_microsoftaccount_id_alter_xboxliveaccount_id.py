# Generated by Django 4.1.7 on 2023-03-08 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('microsoft_auth', '0003_microsoft_id_openid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='microsoftaccount',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='xboxliveaccount',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
