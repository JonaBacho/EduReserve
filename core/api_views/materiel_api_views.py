from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Materiel, ReservationMateriel
from core.serializers import MaterielSerializer, ReservationMaterielSerializer
from core.permissions import IsEnseignantOrReadOnly
from core.paginations import StandardResultsSetPagination

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
