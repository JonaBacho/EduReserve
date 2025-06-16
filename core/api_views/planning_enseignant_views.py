from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from core.permissions import CanViewRecapitulatifHoraire
from core.models import RecapitulatifHoraire, ReservationMateriel, ReservationSalle
from core.paginations import StandardResultsSetPagination
from core.serializers import UserSerializer, RecapitulatifHoraireSerializer, ReservationMaterielSerializer, \
    ReservationSalleSerializer, MaterielSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


class PlanningEnseignantView(generics.ListAPIView):
    """Vue pour voir le planning d'un enseignant (récapitulatif horaire)"""
    permission_classes = [CanViewRecapitulatifHoraire]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_summary="Planning d'un enseignant",
        operation_description="Récupère le planning complet d'un enseignant avec ses récapitulatifs horaires et réservations",
        manual_parameters=[
            openapi.Parameter(
                'enseignant_id',
                openapi.IN_PATH,
                description="ID de l'enseignant",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'date_debut',
                openapi.IN_QUERY,
                description="Date de début du filtre (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            ),
            openapi.Parameter(
                'date_fin',
                openapi.IN_QUERY,
                description="Date de fin du filtre (format: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            )
        ],
        responses={
            200: openapi.Response(
                description="Planning de l'enseignant récupéré avec succès",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'enseignant': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'recapitulatifs': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                         items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'reservations_salles': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                              items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'reservation_materiels': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            404: openapi.Response(
                description="Enseignant non trouvé"
            )
        },
        tags=["Planning"]
    )
    def get(self, request, enseignant_id, *args, **kwargs):
        try:
            enseignant = User.objects.get(id=enseignant_id, user_type='enseignant')
        except User.DoesNotExist:
            return Response(
                {'error': 'Enseignant non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Récupérer les récapitulatifs horaires
        recapitulatifs = RecapitulatifHoraire.objects.filter(
            enseignant=enseignant
        ).select_related('formation', 'creneau', 'salle_prevue')

        # Filtrer par date si spécifiée
        date_debut = request.query_params.get('date_debut', None)
        date_fin = request.query_params.get('date_fin', None)

        if date_debut:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            recapitulatifs = recapitulatifs.filter(date__gte=date_debut)

        if date_fin:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            recapitulatifs = recapitulatifs.filter(date__lte=date_fin)

        # Récupérer aussi les réservations réelles pour comparaison
        reservations_salles = ReservationSalle.objects.filter(
            enseignant=enseignant
        ).select_related('salle', 'formation', 'creneau')

        reservations_materiels = ReservationMateriel.objects.filter(
            enseignant=enseignant
        ).select_related('salle', 'formation', 'creneau')

        if date_debut:
            reservations_salles = reservations_salles.filter(date__gte=date_debut)
            reservations_materiels = reservations_materiels.filter(date__gte=date_debut)
        if date_fin:
            reservations_salles = reservations_salles.filter(date__lte=date_fin)
            reservations_materiels = reservations_materiels.filter(date__lte=date_fin)

        return Response({
            'enseignant': UserSerializer(enseignant).data,
            'recapitulatifs': RecapitulatifHoraireSerializer(recapitulatifs, many=True).data,
            'reservations_salles': ReservationSalleSerializer(reservations_salles, many=True).data,
            'reservation_materiels': MaterielSerializer(reservations_materiels, many=True).data,
        })
