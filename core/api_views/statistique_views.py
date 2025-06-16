from rest_framework import generics
from rest_framework.response import Response
from core.models import ReservationSalle, ReservationMateriel
from django.db.models import Q, Count
from core.serializers import StatistiquesSerializer
from core.permissions import IsEnseignant
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator

@swagger_auto_schema(
        operation_summary="Statistiques générales",
        operation_description="Récupère les statistiques générales des réservations (salles et matériels les plus réservés)",
        tags=["Statistiques"],
        responses={
            200: openapi.Response(
                description="Statistiques récupérées avec succès",
                schema=StatistiquesSerializer
            )
        }
    )
class StatistiquesView(generics.GenericAPIView):
    """Vue pour les statistiques générales"""
    permission_classes = [IsEnseignant]

    def get(self, request, *args, **kwargs):
        # Statistiques générales
        total_reservations_salles = ReservationSalle.objects.count()
        total_reservations_materiels = ReservationMateriel.objects.count()

        # Salles les plus réservées
        salles_populaires = ReservationSalle.objects.values(
            'salle__nom'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # Matériels les plus réservés
        materiels_populaires = ReservationMateriel.objects.values(
            'materiel__nom'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        data = {
            'total_reservations_salles': total_reservations_salles,
            'total_reservations_materiels': total_reservations_materiels,
            'salles_les_plus_reservees': list(salles_populaires),
            'materiels_les_plus_reserves': list(materiels_populaires)
        }

        serializer = StatistiquesSerializer(data)
        return Response(serializer.data)