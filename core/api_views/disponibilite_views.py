from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from core.models import ReservationSalle, ReservationMateriel
from core.serializers import DisponibiliteSerializer


class DisponibiliteView(generics.GenericAPIView):
    """Vue pour vérifier la disponibilité d'une ressource"""
    permission_classes = [permissions.IsAuthenticated]

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