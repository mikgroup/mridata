# Generated by Django 3.2.4 on 2021-06-28 04:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mridata', '0029_auto_20181114_2317'),
    ]

    operations = [
        migrations.RenameField(
            model_name='geawsdata',
            old_name='ge_aws_file',
            new_name='ge_file',
        ),
    ]