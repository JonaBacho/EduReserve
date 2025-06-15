from rest_framework import viewsets
from rest_framework import permissions
from core.models import CreneauHoraire
from core.serializers import CreneauHoraireSerializer


class CreneauHoraireViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CreneauHoraire.objects.all()
    serializer_class = CreneauHoraireSerializer
    permission_classes = [permissions.IsAuthenticated]