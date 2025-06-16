from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from core.serializers import SalleSerializer, ReservationSalleSerializer
from core.models import Salle, ReservationSalle
from core.permissions import IsEnseignantOrReadOnly
from datetime import datetime, timedelta
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator


tags = ["salle"]
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
        operation_summary="Liste des salles",
        operation_description="Récupère la liste de toutes les salles actives",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Détails d'une salle",
        operation_description="Récupère les détails d'une salle spécifique",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="Créer une salle",
        operation_description="Crée une nouvelle salle (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier une salle",
        operation_description="Modifie complètement une salle (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_summary="Modifier partiellement une salle",
        operation_description="Modifie partiellement une salle(réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="Supprimer une salle",
        operation_description="Supprime une salle (réservé aux enseignants)",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.filter(active=True)
    serializer_class = SalleSerializer
    permission_classes = [IsEnseignantOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Planning d'une salle",
        operation_description="Récupère le planning d'une salle pour une période donnée",
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
            )
        ],
        responses={
            200: openapi.Response(
                description="Planning récupéré avec succès",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'salle': openapi.Schema(type=openapi.TYPE_OBJECT),
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
        """Récupère le planning d'une salle pour une période donnée"""
        salle = self.get_object()
        date_debut = request.query_params.get('date_debut', timezone.now().date())
        date_fin = request.query_params.get('date_fin', timezone.now().date() + timedelta(days=7))

        if isinstance(date_debut, str):
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        if isinstance(date_fin, str):
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()

        reservations = ReservationSalle.objects.filter(
            salle=salle,
            date__range=[date_debut, date_fin]
        ).select_related('enseignant', 'formation', 'creneau')

        serializer = ReservationSalleSerializer(reservations, many=True)
        return Response({
            'salle': SalleSerializer(salle).data,
            'periode': {'debut': date_debut, 'fin': date_fin},
            'reservations': serializer.data
        })