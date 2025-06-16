from rest_framework import viewsets
from core.models import TypeMateriel
from core.serializers import TypeMaterielSerializer
from core.permissions import IsEnseignantOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator


tags = ["types-matériels"]
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
        operation_summary="Liste des types de matériel",
        operation_description="Récupère la liste de tous les types de matériel disponibles",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Détails d'un type de matériel",
        operation_description="Récupère les détails d'un type de matériel spécifique",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Créer un type de matériel",
        operation_description="Crée un nouveau type de matériel (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier un type de matériel",
        operation_description="Modifie complètement un type de matériel (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier partiellement un type de matériel",
        operation_description="Modifie partiellement un type de matériel (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Supprimer un type de matériel",
        operation_description="Supprime un type de matériel (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
class TypeMaterielViewSet(viewsets.ModelViewSet):
    queryset = TypeMateriel.objects.all()
    serializer_class = TypeMaterielSerializer
    permission_classes = [IsEnseignantOrReadOnly]