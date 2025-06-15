from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from .models import (
    Formation, Salle, TypeMateriel, Materiel, CreneauHoraire,
    ReservationSalle, ReservationMateriel, RecapitulatifHoraire
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'user_type', 'matricule']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'matricule', 'password', 'first_name', 'last_name', 'user_type']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        user = User.objects.filter(email=identifier).first() or User.objects.filter(matricule=identifier).first()

        if user and user.check_password(password):
            return user
        raise serializers.ValidationError("Identifiants invalides")

class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value


class FormationSerializer(serializers.ModelSerializer):
    responsable_detail = UserSerializer(source='responsable', read_only=True)

    class Meta:
        model = Formation
        fields = ['id', 'nom', 'description', 'responsable', 'responsable_detail', 'created_at']
        read_only_fields = ['id', 'created_at']


class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = ['id', 'nom', 'capacite', 'equipements', 'active']
        read_only_fields = ['id']


class TypeMaterielSerializer(serializers.ModelSerializer):
    materiels_count = serializers.SerializerMethodField()

    class Meta:
        model = TypeMateriel
        fields = ['id', 'nom', 'description', 'materiels_count']
        read_only_fields = ['id', 'materiels_count']

    def get_materiels_count(self, obj):
        return obj.materiels.filter(active=True).count()


class MaterielSerializer(serializers.ModelSerializer):
    type_materiel_detail = TypeMaterielSerializer(source='type_materiel', read_only=True)

    class Meta:
        model = Materiel
        fields = ['id', 'nom', 'type_materiel', 'type_materiel_detail', 'numero_serie', 'active']
        read_only_fields = ['id']


class CreneauHoraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreneauHoraire
        fields = ['id', 'nom', 'heure_debut', 'heure_fin']
        read_only_fields = ['id']


class ReservationSalleSerializer(serializers.ModelSerializer):
    enseignant_detail = UserSerializer(source='enseignant', read_only=True)
    salle_detail = SalleSerializer(source='salle', read_only=True)
    formation_detail = FormationSerializer(source='formation', read_only=True)
    creneau_detail = CreneauHoraireSerializer(source='creneau', read_only=True)

    class Meta:
        model = ReservationSalle
        fields = [
            'id', 'enseignant', 'enseignant_detail', 'salle', 'salle_detail',
            'formation', 'formation_detail', 'creneau', 'creneau_detail',
            'date', 'sujet', 'commentaires', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Impossible de réserver une salle pour une date passée")
        return value

    def validate(self, data):
        # Vérifier les conflits de réservation
        salle = data.get('salle')
        date = data.get('date')
        creneau = data.get('creneau')

        if salle and date and creneau:
            conflits = ReservationSalle.objects.filter(
                salle=salle,
                date=date,
                creneau=creneau
            )

            # Exclure l'instance actuelle lors de la mise à jour
            if self.instance:
                conflits = conflits.exclude(pk=self.instance.pk)

            if conflits.exists():
                raise serializers.ValidationError({
                    'non_field_errors': [f"La salle {salle.nom} est déjà réservée pour ce créneau"]
                })
        return data


class ReservationMaterielSerializer(serializers.ModelSerializer):
    enseignant_detail = UserSerializer(source='enseignant', read_only=True)
    materiel_detail = MaterielSerializer(source='materiel', read_only=True)
    formation_detail = FormationSerializer(source='formation', read_only=True)
    creneau_detail = CreneauHoraireSerializer(source='creneau', read_only=True)

    class Meta:
        model = ReservationMateriel
        fields = [
            'id', 'enseignant', 'enseignant_detail', 'materiel', 'materiel_detail',
            'formation', 'formation_detail', 'creneau', 'creneau_detail',
            'date', 'commentaires', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Impossible de réserver du matériel pour une date passée")
        return value

    def validate(self, data):
        # Vérifier les conflits de réservation
        materiel = data.get('materiel')
        date = data.get('date')
        creneau = data.get('creneau')

        if materiel and date and creneau:
            conflits = ReservationMateriel.objects.filter(
                materiel=materiel,
                date=date,
                creneau=creneau
            )

            # Exclure l'instance actuelle lors de la mise à jour
            if self.instance:
                conflits = conflits.exclude(pk=self.instance.pk)

            if conflits.exists():
                raise serializers.ValidationError({
                    'non_field_errors': [f"Le matériel {materiel.nom} est déjà réservé pour ce créneau"]
                })

        return data


class RecapitulatifHoraireSerializer(serializers.ModelSerializer):
    formation_detail = FormationSerializer(source='formation', read_only=True)
    enseignant_detail = UserSerializer(source='enseignant', read_only=True)
    creneau_detail = CreneauHoraireSerializer(source='creneau', read_only=True)
    salle_prevue_detail = SalleSerializer(source='salle_prevue', read_only=True)

    class Meta:
        model = RecapitulatifHoraire
        fields = [
            'id', 'formation', 'formation_detail', 'enseignant', 'enseignant_detail',
            'date', 'creneau', 'creneau_detail', 'sujet', 'salle_prevue',
            'salle_prevue_detail', 'commentaires', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# Serializers pour les statistiques et rapports
class StatistiquesSerializer(serializers.Serializer):
    total_reservations_salles = serializers.IntegerField()
    total_reservations_materiels = serializers.IntegerField()
    salles_les_plus_reservees = serializers.ListField()
    materiels_les_plus_reserves = serializers.ListField()


class PlanningJournalierSerializer(serializers.Serializer):
    date = serializers.DateField()
    reservations = serializers.ListField()


class DisponibiliteSerializer(serializers.Serializer):
    """Serializer pour vérifier la disponibilité d'une salle ou d'un matériel"""
    type_ressource = serializers.ChoiceField(choices=['salle', 'materiel'])
    ressource_id = serializers.IntegerField()
    date = serializers.DateField()
    creneau_id = serializers.IntegerField()
    disponible = serializers.BooleanField(read_only=True)
    conflit = serializers.CharField(read_only=True, required=False)