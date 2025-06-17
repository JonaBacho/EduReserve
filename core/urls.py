# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.api_views.materiel_api_views import MaterielViewSet
from core.api_views.authentication_views import UserViewSet, RegisterView, LoginView, PasswordResetView, CurrentUserView
from core.api_views.disponibilite_views import DisponibiliteView
from core.api_views.formations_api_views import FormationViewSet
from core.api_views.planning_enseignant_views import PlanningEnseignantView
from core.api_views.planning_global_views import PlanningGeneralView
from core.api_views.recapitulatif_horaire_api_views import RecapitulatifHoraireViewSet
from core.api_views.reservation_salle_api_views import ReservationSalleViewSet
from core.api_views.reservation_materiel_api_views import ReservationMaterielViewSet
from core.api_views.reservations_enseignant_views import MesReservationsView
from core.api_views.salle_api_views import SalleViewSet
from core.api_views.statistique_views import StatistiquesView
from core.api_views.type_materiel_api_views import TypeMaterielViewSet
from core.api_views.creneau_api_views import CreneauHoraireViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'formations', FormationViewSet)
router.register(r'salles', SalleViewSet)
router.register(r'types-materiel', TypeMaterielViewSet)
router.register(r'materiels', MaterielViewSet)
router.register(r'creneaux', CreneauHoraireViewSet)
router.register(r'reservations-salles', ReservationSalleViewSet, basename='reservationsalle')
router.register(r'reservations-materiels', ReservationMaterielViewSet, basename='reservationmateriel')
router.register(r'recapitulatifs', RecapitulatifHoraireViewSet, basename='recapitulatifhoraire')

urlpatterns = [
    path('', include(router.urls)),
    path('planning/', PlanningGeneralView.as_view(), name='planning-general'),
    path('statistiques/', StatistiquesView.as_view(), name='statistiques'),
    path('disponibilite/', DisponibiliteView.as_view(), name='disponibilite'),
    path('mes-reservations/', MesReservationsView.as_view(), name='mes-reservations'),
    path('planning-enseignant/<int:enseignant_id>/', PlanningEnseignantView.as_view(), name='planning-enseignant'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
