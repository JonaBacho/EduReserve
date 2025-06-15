from rest_framework import viewsets
from core.models import Formation
from core.serializers import FormationSerializer
from core.permissions import IsEnseignantOrReadOnly
from core.paginations import StandardResultsSetPagination

class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    permission_classes = [IsEnseignantOrReadOnly]
    pagination_class = StandardResultsSetPagination