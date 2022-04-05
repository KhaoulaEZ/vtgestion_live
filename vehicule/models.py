from django.db import models
from proprietaire.models import Proprietaire
# Create your models here.


class Vehicule(models.Model):
    proprietaire = models.ForeignKey(Proprietaire, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=200)  # dans l'affichage
    marque = models.CharField(max_length=50)  # dans l'affichage
    type = models.CharField(max_length=50, default='VL')  # dans l'affichage
    puissance_fiscale = models.IntegerField()

    def __str__(self):
        return f"{self.pk}:{self.matricule}"