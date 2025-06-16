from rest_framework import viewsets
from rest_framework import permissions
from core.models import CreneauHoraire
from core.serializers import CreneauHoraireSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator


tags = ["créneau"]
auth_header_param = openapi.Parameter(
    name="Authorization",
    in_=openapi.IN_HEADER,
    description="Token JWT pour l'authentification (Bearer <token>)",
    type=openapi.TYPE_STRING,
    required=True
)

@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="Liste des créneaux horaires",
        operation_description="Récupère la liste de tous les créneaux horaires disponibles",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Détails d'un créneau horaire",
        operation_description="Récupère les détails d'un créneau horaire spécifique",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Créer un type de creneau",
        operation_description="Crée un nouveau type de creneau (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier un creneau",
        operation_description="Modifie complètement un creneau (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier partiellement un creneau",
        operation_description="Modifie partiellement un creneau (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Supprimer un creneau",
        operation_description="Supprime un creneau (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
class CreneauHoraireViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CreneauHoraire.objects.all()
    serializer_class = CreneauHoraireSerializer
    permission_classes = [permissions.IsAuthenticated]