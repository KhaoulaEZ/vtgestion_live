# Generated by Django 4.0.3 on 2022-04-03 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Proprietaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=500)),
                ('prenom', models.CharField(max_length=500)),
                ('nom_c', models.CharField(max_length=500)),
                ('Cin', models.CharField(max_length=500)),
                ('ville', models.CharField(max_length=500)),
                ('quartier', models.CharField(max_length=500)),
                ('Tele', models.CharField(max_length=500)),
            ],
        ),
    ]
