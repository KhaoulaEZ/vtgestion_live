from django.db import models

# Create your models here.


class Proprietaire(models.Model):
    nom = models.CharField(max_length=500)  # dans l'affichage
    prenom = models.CharField(max_length=500)  # dans l'affichage
    nom_c = models.CharField(max_length=500)
    Cin = models.CharField(max_length=500)  # dans l'affichage
    ville = models.CharField(max_length=500)
    quartier = models.CharField(max_length=500)
    Tele = models.CharField(max_length=500)  # dans l'affichage

    def __str__(self):
        return f"{self.nom} {self.prenom}"