from rest_framework import viewsets
from core.models import TypeMateriel
from core.serializers import TypeMaterielSerializer
from core.permissions import IsEnseignantOrReadOnly

class TypeMaterielViewSet(viewsets.ModelViewSet):
    queryset = TypeMateriel.objects.all()
    serializer_class = TypeMaterielSerializer
    permission_classes = [IsEnseignantOrReadOnly]