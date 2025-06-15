from rest_framework import viewsets
from core.models import ReservationSalle
from core.permissions import IsEnseignant, IsOwnerOrReadOnly
from core.paginations import LargeResultsSetPagination
from core.serializers import ReservationSalleSerializer

class ReservationSalleViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSalleSerializer
    permission_classes = [IsEnseignant, IsOwnerOrReadOnly]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
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