from rest_framework import viewsets
from core.models import ReservationSalle
from core.permissions import IsEnseignant, IsOwnerOrReadOnly
from core.paginations import LargeResultsSetPagination
from core.serializers import ReservationSalleSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator


tags = ["Réservations Salles"]
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
    operation_summary="Liste des réservations de salles",
        operation_description="Récupère la liste des réservations de salles avec filtres optionnels",
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Filtrer par date (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'salle',
                openapi.IN_QUERY,
                description="Filtrer par ID de salle",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'formation',
                openapi.IN_QUERY,
                description="Filtrer par ID de formation",
                type=openapi.TYPE_INTEGER
            ),
            auth_header_param
        ],
        tags = tags
    )
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Détails d'une réservation de salle",
        operation_description="Récupère les détails d'une réservation de salle spécifique",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Créer une réservation de salle",
        operation_description="Crée une nouvelle réservation de salle pour l'enseignant connecté",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier une réservation de salle",
        operation_description="Modifie complètement une réservation de salle (propriétaire uniquement)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier partiellement une réservation de salle",
        operation_description="Modifie partiellement une réservation de salle (propriétaire uniquement)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Supprimer une réservation de salle",
        operation_description="Supprime une réservation de salle (propriétaire uniquement)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
class ReservationSalleViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSalleSerializer
    permission_classes = [IsEnseignant, IsOwnerOrReadOnly]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):

        # cas de swagger
        if getattr(self, 'swagger_fake_view', False):
            return ReservationSalle.objects.none()
            
        queryset = ReservationSalle.objects.select_related(
            'enseignant', 'salle', 'formation', 'creneau'
        )

        # Filtrer par enseignant pour les utilisateurs non-admin
        if not self.request.user.is_superuser:
            if self.action in ['list', 'retrieve']:
                # Pour la lecture, tout le monde peut voir les réservations
                pass
            else:
                # Pour les autres actions, seulement ses propres réservations
                queryset = queryset.filter(enseignant=self.request.user)

        # Filtres optionnels
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date=date)

        salle = self.request.query_params.get('salle', None)
        if salle:
            queryset = queryset.filter(salle=salle)

        formation = self.request.query_params.get('formation', None)
        if formation:
            queryset = queryset.filter(formation=formation)

        return queryset

    def perform_create(self, serializer):
        serializer.save(enseignant=self.request.user)
