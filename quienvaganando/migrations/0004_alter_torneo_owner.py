# Generated by Django 3.2.25 on 2024-05-19 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quienvaganando', '0003_alter_torneo_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='torneo',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quienvaganando.user'),
        ),
    ]
