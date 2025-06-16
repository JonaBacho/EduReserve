from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from core.models import ReservationSalle, ReservationMateriel
from core.serializers import DisponibiliteSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class DisponibiliteView(generics.GenericAPIView):
    """Vue pour vérifier la disponibilité d'une ressource"""
    permission_classes = [permissions.IsAuthenticated]


    @swagger_auto_schema(
        operation_summary="Vérifier la disponibilité",
        operation_description="Vérifie la disponibilité d'une ressource (salle ou matériel) pour une date et un créneau donnés",
        request_body=DisponibiliteSerializer,
        responses={
            200: openapi.Response(
                description="Disponibilité vérifiée avec succès",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'type_ressource': openapi.Schema(type=openapi.TYPE_STRING),
                        'ressource_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                        'creneau_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'disponible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'conflit': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description="Message de conflit si non disponible")
                    }
                )
            ),
            400: openapi.Response(
                description="Données invalides"
            )
        },
        tags=["Disponibilité"]
    )
    def post(self, request, *args, **kwargs):
        serializer = DisponibiliteSerializer(data=request.data)
        if serializer.is_valid():
            type_ressource = serializer.validated_data['type_ressource']
            ressource_id = serializer.validated_data['ressource_id']
            date = serializer.validated_data['date']
            creneau_id = serializer.validated_data['creneau_id']

            disponible = True
            conflit = None

            if type_ressource == 'salle':
                conflit_reservation = ReservationSalle.objects.filter(
                    salle_id=ressource_id,
                    date=date,
                    creneau_id=creneau_id
                ).first()

                if conflit_reservation:
                    disponible = False
                    conflit = f"Réservée par {conflit_reservation.enseignant} pour {conflit_reservation.formation.nom}"

            elif type_ressource == 'materiel':
                conflit_reservation = ReservationMateriel.objects.filter(
                    materiel_id=ressource_id,
                    date=date,
                    creneau_id=creneau_id
                ).first()

                if conflit_reservation:
                    disponible = False
                    conflit = f"Réservé par {conflit_reservation.enseignant} pour {conflit_reservation.formation.nom}"

            response_data = serializer.validated_data.copy()
            response_data['disponible'] = disponible
            if conflit:
                response_data['conflit'] = conflit

            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)