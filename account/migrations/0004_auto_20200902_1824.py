# Generated by Django 2.2 on 2020-09-02 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_remove_user_is_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='syllabus',
            field=models.FileField(blank=True, null=True, upload_to='syllabus/'),
        ),
    ]