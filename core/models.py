from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('enseignant', 'Enseignant'),
        ('etudiant', 'Étudiant'),
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='enseignant')
    matricule = models.CharField(max_length=11, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Formation(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=11, unique=True)
    description = models.TextField(blank=True, null=True)
    responsable = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'enseignant'}, related_name='formations_responsable')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']


class Salle(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    capacite = models.PositiveIntegerField()
    equipements = models.TextField(help_text="Description des équipements disponibles", blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} (capacité: {self.capacite})"

    class Meta:
        ordering = ['nom']


class TypeMateriel(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['nom']


class Materiel(models.Model):
    nom = models.CharField(max_length=100)
    type_materiel = models.ForeignKey('TypeMateriel', on_delete=models.CASCADE, related_name='materiels')
    numero_serie = models.CharField(max_length=100, unique=True, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} ({self.type_materiel.nom})"

    class Meta:
        ordering = ['type_materiel__nom', 'nom']


class CreneauHoraire(models.Model):
    # Créneaux fixes de 2h avec pauses
    CRENEAUX_CHOICES = [
        ('08:00-10:00', '08:00 - 10:00'),
        ('10:15-12:15', '10:15 - 12:15'),
        ('13:30-15:30', '13:30 - 15:30'),
        ('15:45-17:45', '15:45 - 17:45'),
    ]

    nom = models.CharField(max_length=20, choices=CRENEAUX_CHOICES, unique=True)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    def __str__(self):
        return self.nom

    def clean(self):
        if self.heure_debut >= self.heure_fin:
            raise ValidationError("L'heure de début doit être antérieure à l'heure de fin")

    class Meta:
        ordering = ['heure_debut']


class ReservationSalle(models.Model):
    enseignant = models.ForeignKey('User', on_delete=models.CASCADE, limit_choices_to={'user_type': 'enseignant'}, related_name='reservations_salles')
    salle = models.ForeignKey('Salle', on_delete=models.CASCADE, related_name='reservations')
    formation = models.ForeignKey('Formation', on_delete=models.CASCADE, related_name='reservations_salles')
    creneau = models.ForeignKey('CreneauHoraire', on_delete=models.CASCADE)
    date = models.DateField()
    sujet = models.CharField(max_length=200, null=True, blank=True)
    commentaires = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.salle.nom} - {self.date} {self.creneau.nom} - {self.enseignant}"

    def clean(self):
        # Vérifier que la date n'est pas dans le passé
        if self.date < timezone.now().date():
            raise ValidationError("Impossible de réserver une salle pour une date passée")

        # Vérifier qu'il n'y a pas de conflit de réservation
        conflits = ReservationSalle.objects.filter(
            salle=self.salle,
            date=self.date,
            creneau=self.creneau
        ).exclude(pk=self.pk)

        if conflits.exists():
            raise ValidationError(f"La salle {self.salle.nom} est déjà réservée pour ce créneau")

    class Meta:
        unique_together = ['salle', 'date', 'creneau']
        ordering = ['-date', 'creneau__heure_debut']


class ReservationMateriel(models.Model):
    enseignant = models.ForeignKey('User', on_delete=models.CASCADE, limit_choices_to={'user_type': 'enseignant'}, related_name='reservations_materiels')
    materiel = models.ForeignKey('Materiel', on_delete=models.CASCADE, related_name='reservations')
    formation = models.ForeignKey('Formation', on_delete=models.CASCADE, related_name='reservations_materiels')
    creneau = models.ForeignKey('CreneauHoraire', on_delete=models.CASCADE)
    date = models.DateField()
    commentaires = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.materiel.nom} - {self.date} {self.creneau.nom} - {self.enseignant}"

    def clean(self):
        # Vérifier que la date n'est pas dans le passé
        if self.date < timezone.now().date():
            raise ValidationError("Impossible de réserver du matériel pour une date passée")

        # Vérifier qu'il n'y a pas de conflit de réservation
        conflits = ReservationMateriel.objects.filter(
            materiel=self.materiel,
            date=self.date,
            creneau=self.creneau
        ).exclude(pk=self.pk)

        if conflits.exists():
            raise ValidationError(f"Le matériel {self.materiel.nom} est déjà réservé pour ce créneau")

    class Meta:
        unique_together = ['materiel', 'date', 'creneau']
        ordering = ['-date', 'creneau__heure_debut']


class RecapitulatifHoraire(models.Model):
    """Récapitulatif personnalisé par formation et enseignant"""
    formation = models.ForeignKey('Formation', on_delete=models.CASCADE, related_name='recapitulatifs')
    enseignant = models.ForeignKey('User', on_delete=models.CASCADE, limit_choices_to={'user_type': 'enseignant'}, related_name='recapitulatifs')
    date = models.DateField()
    creneau = models.ForeignKey('CreneauHoraire', on_delete=models.CASCADE)
    sujet = models.CharField(max_length=200, null=True, blank=True)
    salle_prevue = models.ForeignKey('Salle', on_delete=models.SET_NULL, null=True, blank=True)
    commentaires = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.formation.nom} - {self.enseignant} - {self.date} {self.creneau.nom}"

    class Meta:
        unique_together = ['formation', 'enseignant', 'date', 'creneau']
        ordering = ['formation', '-date', 'creneau__heure_debut']