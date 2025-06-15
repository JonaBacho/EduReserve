from rest_framework import viewsets
from core.models import RecapitulatifHoraire
from core.serializers import RecapitulatifHoraireSerializer
from core.permissions import IsResponsableFormationOrReadOnly
from core.paginations import LargeResultsSetPagination

class RecapitulatifHoraireViewSet(viewsets.ModelViewSet):
    serializer_class = RecapitulatifHoraireSerializer
    permission_classes = [IsResponsableFormationOrReadOnly]
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = RecapitulatifHoraire.objects.select_related(
            'formation', 'enseignant', 'creneau', 'salle_prevue'
        )

        # Filtrer par formation si l'utilisateur est responsable
        formation = self.request.query_params.get('formation', None)
        if formation:
            queryset = queryset.filter(formation=formation)

        # Filtrer par enseignant
        enseignant = self.request.query_params.get('enseignant', None)
        if enseignant:
            queryset = queryset.filter(enseignant=enseignant)

        # Filtrer par date
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(date=date)

        return queryset
