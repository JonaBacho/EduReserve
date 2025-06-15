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

User = get_user_model()


class PlanningEnseignantView(generics.ListAPIView):
    """Vue pour voir le planning d'un enseignant (récapitulatif horaire)"""
    permission_classes = [CanViewRecapitulatifHoraire]
    pagination_class = StandardResultsSetPagination

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
