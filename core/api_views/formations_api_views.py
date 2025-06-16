from rest_framework import viewsets
from core.models import Formation
from core.serializers import FormationSerializer
from core.permissions import IsEnseignantOrReadOnly
from core.paginations import StandardResultsSetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator


tags = ["Formations"]
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
        operation_summary="Liste des formations",
        operation_description="Récupère la liste de toutes les formations disponibles",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Détails d'une formation",
        operation_description="Récupère les détails d'une formation spécifique",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Créer une formation",
        operation_description="Crée une nouvelle formation (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier une formation",
        operation_description="Modifie complètement une formation (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier partiellement une formation",
        operation_description="Modifie partiellement une formation (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Supprimer une formation",
        operation_description="Supprime une formation (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    permission_classes = [IsEnseignantOrReadOnly]
    pagination_class = StandardResultsSetPagination