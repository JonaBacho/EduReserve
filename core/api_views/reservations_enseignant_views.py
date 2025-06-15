from rest_framework import generics
from datetime import datetime, timedelta
from rest_framework.response import Response
from core.models import ReservationSalle, ReservationMateriel
from core.serializers import ReservationSalleSerializer, ReservationMaterielSerializer
from core.permissions import IsEnseignant
from core.paginations import StandardResultsSetPagination

class MesReservationsView(generics.ListAPIView):
    """Vue pour voir ses propres réservations"""
    permission_classes = [IsEnseignant]
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        # Récupérer les réservations de salles
        reservations_salles = ReservationSalle.objects.filter(
            enseignant=request.user
        ).select_related('salle', 'formation', 'creneau')

        # Récupérer les réservations de matériel
        reservations_materiels = ReservationMateriel.objects.filter(
            enseignant=request.user
        ).select_related('materiel', 'formation', 'creneau')

        # Filtrer par date si spécifiée
        date_debut = request.query_params.get('date_debut', None)
        date_fin = request.query_params.get('date_fin', None)

        if date_debut:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            reservations_salles = reservations_salles.filter(date__gte=date_debut)
            reservations_materiels = reservations_materiels.filter(date__gte=date_debut)

        if date_fin:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            reservations_salles = reservations_salles.filter(date__lte=date_fin)
            reservations_materiels = reservations_materiels.filter(date__lte=date_fin)

        return Response({
            'reservations_salles': ReservationSalleSerializer(reservations_salles, many=True).data,
            'reservations_materiels': ReservationMaterielSerializer(reservations_materiels, many=True).data
        })