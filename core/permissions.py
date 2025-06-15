# permissions.py
from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsEnseignant(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur est un enseignant
    """

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.user_type == 'enseignant'
        )


class IsEnseignantOrReadOnly(permissions.BasePermission):
    """
    Permission qui permet la lecture à tous les utilisateurs authentifiés
    mais l'écriture seulement aux enseignants
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
                request.user and
                request.user.is_authenticated and
                request.user.user_type == 'enseignant'
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre seulement aux propriétaires
    d'un objet de le modifier
    """

    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Permissions d'écriture seulement pour le propriétaire
        return obj.enseignant == request.user


class IsResponsableFormationOrReadOnly(permissions.BasePermission):
    """
    Permission pour les récapitulatifs horaires :
    - Lecture : tous les enseignants
    - Écriture : seulement le responsable de la formation
    """

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.user_type == 'enseignant'
        )

    def has_object_permission(self, request, view, obj):
        # Lecture pour tous les enseignants
        if request.method in permissions.SAFE_METHODS:
            return (
                    request.user and
                    request.user.is_authenticated and
                    request.user.user_type == 'enseignant'
            )

        # Écriture seulement pour le responsable de la formation
        return (
                request.user and
                request.user.is_authenticated and
                obj.formation.responsable == request.user
        )


class CanViewRecapitulatifHoraire(permissions.BasePermission):
    """
    Permission pour voir les récapitulatifs horaires : seulement les enseignants
    """

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.user_type == 'enseignant'
        )


class CanViewPlanningDetails(permissions.BasePermission):
    """
    Permission pour voir les détails du planning :
    - Planning des salles : tout le monde (enseignants et étudiants)
    - Récapitulatifs par enseignant : seulement enseignants
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsEnseignantOwner(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur est enseignant ET propriétaire de la réservation
    """

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.user_type == 'enseignant'
        )

    def has_object_permission(self, request, view, obj):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.user_type == 'enseignant' and
                obj.enseignant == request.user
        )