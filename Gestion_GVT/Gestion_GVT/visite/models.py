from django.db import models
from users.models import Users
from vehicule.models import Vehicule
from facture.models import Facture
from datetime import date

# Create your models here.
import datetime




class Visite(models.Model):
    vehicule = models.OneToOneField(Vehicule, on_delete=models.CASCADE)
    Users = models.ForeignKey(Users, on_delete=models.CASCADE)
    facture = models.OneToOneField(Facture, on_delete=models.CASCADE)
    observation = models.TextField(blank=True)
    date_visite = models.DateTimeField()  # dans l'affichage
    date_expiration = models.DateTimeField()
    prix = models.FloatField()  # dans l'affichage
    paiment = models.CharField(max_length=20)  # dans l'affichage
    type = models.CharField(max_length=10)  # dans l'affichage
    resultat = models.CharField(max_length=100)

    def __str__(self):
        return f"id={self.pk}:{self.vehicule}"

    class Meta:
        ordering = ['-pk']
