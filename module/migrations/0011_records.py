# Generated by Django 3.0.2 on 2020-07-07 22:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0010_auto_20200630_2307'),
    ]

    operations = [
        migrations.CreateModel(
            name='Records',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('progress', models.CharField(max_length=30)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='records', to='module.Experiment')),
            ],
        ),
    ]
