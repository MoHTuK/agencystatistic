# Generated by Django 4.2.6 on 2023-10-05 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Lady_ID', models.IntegerField()),
                ('Man_ID', models.IntegerField()),
                ('Sum', models.FloatField()),
                ('Operation_type', models.CharField(max_length=255)),
                ('Date', models.CharField(max_length=255)),
            ],
        ),
    ]
