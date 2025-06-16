from rest_framework import viewsets
from core.models import RecapitulatifHoraire
from core.serializers import RecapitulatifHoraireSerializer
from core.permissions import IsResponsableFormationOrReadOnly
from core.paginations import LargeResultsSetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator


tags = ["Récapitulatif horaire"]
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
    operation_summary="Liste des récapitulatifs horaires",
        operation_description="Récupère la liste des récapitulatifs horaires avec filtres optionnels",
        manual_parameters=[
            openapi.Parameter(
                'formation',
                openapi.IN_QUERY,
                description="Filtrer par ID de formation",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'enseignant',
                openapi.IN_QUERY,
                description="Filtrer par ID d'enseignant",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Filtrer par date (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            auth_header_param
        ],
        tags = tags
    )
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Détails d'un récapitulatif horaire",
        operation_description="Récupère les détails d'un récapitulatif horaire spécifique",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Créer un récapitulatif horaire",
        operation_description="Crée un nouveau récapitulatif horaire (responsables de formation uniquement)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier un récapitulatif horaire",
        operation_description="Modifie complètement un récapitulatif horaire (responsables de formation uniquement)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier partiellement un récapitulatif horaire",
        operation_description="Modifie partiellement un récapitulatif horaire (responsables de formation uniquement)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Supprimer un récapitulatif horaire",
        operation_description="Supprime un récapitulatif horaire (responsables de formation uniquement)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
class RecapitulatifHoraireViewSet(viewsets.ModelViewSet):
    serializer_class = RecapitulatifHoraireSerializer
    permission_classes = [IsResponsableFormationOrReadOnly]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = RecapitulatifHoraire.objects.select_related(
            'formation', 'enseignant', 'creneau', 'salle_prevue'
        )

        # Filtrer par formation si l'utilisateur est responsable
        formation = self.request.query_params.get('formation', None)
        if formation:
            queryset = queryset.filter(formation=formation)

        # Filtrer par enseignant
        enseignant = self.request.query_params.get('enseignant', None)
        if enseignant:
            queryset = queryset.filter(enseignant=enseignant)

        # Filtrer par date
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date=date)

        return queryset
