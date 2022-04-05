from datetime import date
from django.db import models
# from Visite.models import Visite
# Create your models here.


class Facture(models.Model):
    Narsa = models.IntegerField(default=30)
    taxe_paiment = models.FloatField(default=0)
    taxe_fiscale = models.IntegerField(default=30)
    taxe_communale = models.IntegerField(default=50)
    paiment = models.CharField(max_length=100)  # dans l'affichage
    numero = models.CharField(max_length=100)  # dans l'affichage
    montant_net = models.IntegerField(default=200)
    montant_total = models.FloatField()  # dans l'affichage