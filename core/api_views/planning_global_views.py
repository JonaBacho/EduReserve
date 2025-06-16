from rest_framework import generics
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.utils import timezone
from core.models import ReservationSalle, ReservationMateriel, CreneauHoraire
from core.serializers import ReservationMaterielSerializer, ReservationSalleSerializer, CreneauHoraireSerializer
from core.permissions import CanViewPlanningDetails
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PlanningGeneralView(generics.ListAPIView):
    """Vue pour consulter le planning général des salles et des materiels"""
    permission_classes = [CanViewPlanningDetails]

    @swagger_auto_schema(
        operation_summary="Planning général",
        operation_description="Récupère le planning général des salles et matériels pour une date donnée, organisé par créneaux horaires",
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Date du planning (format: YYYY-MM-DD). Par défaut: aujourd'hui",
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
                        'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                        'planning': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'creneaux': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                   items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            )
        },
        tags=["Planning"]
    )
    def get(self, request, *args, **kwargs):
        date = request.query_params.get('date', timezone.now().date())
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()

        # Récupérer toutes les réservations pour la date donnée
        reservations_salles = ReservationSalle.objects.filter(date=date).select_related(
            'salle', 'enseignant', 'formation', 'creneau'
        )
        reservations_materiels = ReservationMateriel.objects.filter(date=date).select_related(
            'materiel', 'enseignant', 'formation', 'creneau'
        )

        # Organiser par créneau
        creneaux = CreneauHoraire.objects.all()
        planning = {}

        for creneau in creneaux:
            # Récupérer la réservation de salle pour ce créneau (s'il y en a une)
            reservation_salle = reservations_salles.filter(creneau=creneau)
            salle_data = ReservationSalleSerializer(reservation_salle, many=True).data

            # Récupérer les réservations de matériel pour ce créneau
            reservations_mat = reservations_materiels.filter(creneau=creneau)
            materiels_data = ReservationMaterielSerializer(reservations_mat, many=True).data

            # Ajouter au planning
            planning[creneau.nom] = {
                'salle': salle_data,
                'materiels': materiels_data
            }

        return Response({
            'date': date,
            'planning': dict(planning),
            'creneaux': CreneauHoraireSerializer(creneaux, many=True).data
        })