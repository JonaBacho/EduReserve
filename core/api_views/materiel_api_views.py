from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Materiel, ReservationMateriel
from core.serializers import MaterielSerializer, ReservationMaterielSerializer
from core.permissions import IsEnseignantOrReadOnly
from core.paginations import StandardResultsSetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator


tags = ["Matériels"]
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
        operation_summary="Liste du matériel",
        operation_description="Récupère la liste de tous le matériel actif",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Détails d'un matériel",
        operation_description="Récupère les détails d'un matériel spécifique",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Créer un matériel",
        operation_description="Crée une nouveau matériel (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier un matériel",
        operation_description="Modifie complètement un matériel(réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier partiellement un matériel",
        operation_description="Modifie partiellement un matériel(réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Supprimer un matériel",
        operation_description="Supprime un matériel (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
class MaterielViewSet(viewsets.ModelViewSet):
    queryset = Materiel.objects.filter(active=True)
    serializer_class = MaterielSerializer
    permission_classes = [IsEnseignantOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Materiel.objects.filter(active=True)
        type_materiel = self.request.query_params.get('type_materiel', None)
        if type_materiel:
            queryset = queryset.filter(type_materiel=type_materiel)
        return queryset

    @swagger_auto_schema(
        operation_summary="Planning d'un matériel",
        operation_description="Récupère le planning d'un matériel pour une période donnée",
        manual_parameters=[
            openapi.Parameter(
                'date_debut',
                openapi.IN_QUERY,
                description="Date de début (format: YYYY-MM-DD). Par défaut: aujourd'hui",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'date_fin',
                openapi.IN_QUERY,
                description="Date de fin (format: YYYY-MM-DD). Par défaut: dans 7 jours",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            auth_header_param
        ],
        responses={
            200: openapi.Response(
                description="Planning du matériel récupéré avec succès",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'materiel': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'periode': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'reservations': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                       items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            )
        },
        tags=tags
    )
    @action(detail=True, methods=['get'])
    def planning(self, request, pk=None):
        """Récupère le planning d'un matériel pour une période donnée"""
        materiel = self.get_object()
        date_debut = request.query_params.get('date_debut', timezone.now().date())
        date_fin = request.query_params.get('date_fin', timezone.now().date() + timedelta(days=7))

        if isinstance(date_debut, str):
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if isinstance(date_fin, str):
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()

        reservations = ReservationMateriel.objects.filter(
            materiel=materiel,
            date__range=[date_debut, date_fin]
        ).select_related('enseignant', 'formation', 'creneau')

        serializer = ReservationMaterielSerializer(reservations, many=True)
        return Response({
            'materiel': MaterielSerializer(materiel).data,
            'periode': {'debut': date_debut, 'fin': date_fin},
            'reservations': serializer.data
        })
