# Generated by Django 3.1.3 on 2020-11-30 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal', '0003_auto_20201129_1629'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='matrix',
            options={'ordering': ['matrix_name']},
        ),
        migrations.AlterModelOptions(
            name='matrixgroup',
            options={'ordering': ['category_name']},
        ),
        migrations.RemoveField(
            model_name='matrix',
            name='matrix_category',
        ),
        migrations.AddField(
            model_name='matrixgroup',
            name='matrices',
            field=models.ManyToManyField(to='personal.Matrix'),
        ),
    ]