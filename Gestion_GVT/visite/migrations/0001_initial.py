# Generated by Django 4.0.3 on 2022-04-03 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('vehicule', '0001_initial'),
        ('facture', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observation', models.TextField(blank=True)),
                ('date_visite', models.DateTimeField()),
                ('date_expiration', models.DateTimeField()),
                ('prix', models.FloatField()),
                ('paiment', models.CharField(max_length=20)),
                ('type', models.CharField(max_length=10)),
                ('resultat', models.CharField(max_length=100)),
                ('Users', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.users')),
                ('facture', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='facture.facture')),
                ('vehicule', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='vehicule.vehicule')),
            ],
            options={
                'ordering': ['-pk'],
            },
        ),
    ]
