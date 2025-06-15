from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from core.serializers import SalleSerializer, ReservationSalleSerializer
from core.models import Salle, ReservationSalle
from core.permissions import IsEnseignantOrReadOnly
from datetime import datetime, timedelta
from django.utils import timezone


class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.filter(active=True)
    serializer_class = SalleSerializer
    permission_classes = [IsEnseignantOrReadOnly]

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