# Generated by Django 3.0.2 on 2020-06-30 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0008_auto_20200630_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='elementdata',
            name='alias',
            field=models.TextField(null=True),
        ),
    ]
