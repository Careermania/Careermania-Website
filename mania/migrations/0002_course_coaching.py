# Generated by Django 2.2 on 2020-09-28 08:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mania', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='coaching',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='mania.Coaching'),
            preserve_default=False,
        ),
    ]