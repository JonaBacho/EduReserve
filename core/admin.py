# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import (
    Formation, Salle, TypeMateriel, Materiel, CreneauHoraire,
    ReservationSalle, ReservationMateriel, RecapitulatifHoraire
)

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('matricule', 'username', 'first_name', 'last_name', 'email', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('matricule', 'username', 'first_name', 'last_name', 'email')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('user_type',)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {'fields': ('user_type',)}),
    )


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'responsable', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('nom', 'description')
    autocomplete_fields = ('responsable',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('responsable')


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'capacite', 'active')
    list_filter = ('active',)
    search_fields = ('nom', 'equipements')
    list_editable = ('active',)


@admin.register(TypeMateriel)
class TypeMaterielAdmin(admin.ModelAdmin):
    list_display = ('nom', 'get_materiels_count')
    search_fields = ('nom', 'description')

    def get_materiels_count(self, obj):
        return obj.materiels.filter(active=True).count()

    get_materiels_count.short_description = 'Nombre de matériels'


@admin.register(Materiel)
class MaterielAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_materiel', 'numero_serie', 'active')
    list_filter = ('type_materiel', 'active')
    search_fields = ('nom', 'numero_serie')
    list_editable = ('active',)
    autocomplete_fields = ('type_materiel',)


@admin.register(CreneauHoraire)
class CreneauHoraireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'heure_debut', 'heure_fin')
    ordering = ('heure_debut',)
    search_fields = ('nom',)


@admin.register(ReservationSalle)
class ReservationSalleAdmin(admin.ModelAdmin):
    list_display = ('salle', 'enseignant', 'formation', 'date', 'creneau', 'sujet')
    list_filter = ('date', 'creneau', 'salle', 'formation')
    search_fields = ('enseignant__username', 'enseignant__first_name', 'enseignant__last_name', 'sujet')
    autocomplete_fields = ('enseignant', 'salle', 'formation', 'creneau')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'enseignant', 'salle', 'formation', 'creneau'
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Limiter les enseignants aux utilisateurs de type 'enseignant'
        if 'enseignant' in form.base_fields:
            form.base_fields['enseignant'].queryset = User.objects.filter(user_type='enseignant')
        return form


@admin.register(ReservationMateriel)
class ReservationMaterielAdmin(admin.ModelAdmin):
    list_display = ('materiel', 'enseignant', 'formation', 'date', 'creneau')
    list_filter = ('date', 'creneau', 'materiel__type_materiel', 'formation')
    search_fields = ('enseignant__username', 'enseignant__first_name', 'enseignant__last_name')
    autocomplete_fields = ('enseignant', 'materiel', 'formation', 'creneau')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'enseignant', 'materiel', 'formation', 'creneau'
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Limiter les enseignants aux utilisateurs de type 'enseignant'
        if 'enseignant' in form.base_fields:
            form.base_fields['enseignant'].queryset = User.objects.filter(user_type='enseignant')
        return form


@admin.register(RecapitulatifHoraire)
class RecapitulatifHoraireAdmin(admin.ModelAdmin):
    list_display = ('formation', 'enseignant', 'date', 'creneau', 'sujet', 'salle_prevue')
    list_filter = ('date', 'creneau', 'formation')
    search_fields = ('enseignant__username', 'enseignant__first_name', 'enseignant__last_name', 'sujet')
    autocomplete_fields = ('formation', 'enseignant', 'creneau', 'salle_prevue')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'formation', 'enseignant', 'creneau', 'salle_prevue'
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Limiter les enseignants aux utilisateurs de type 'enseignant'
        if 'enseignant' in form.base_fields:
            form.base_fields['enseignant'].queryset = User.objects.filter(user_type='enseignant')
        return form

    def has_change_permission(self, request, obj=None):
        # Seuls les responsables de formation peuvent modifier
        if obj and not request.user.is_superuser:
            return obj.formation.responsable == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Seuls les responsables de formation peuvent supprimer
        if obj and not request.user.is_superuser:
            return obj.formation.responsable == request.user
        return super().has_delete_permission(request, obj)


# Configuration de l'interface admin
admin.site.site_header = "Administration - Système de Réservations"
admin.site.site_title = "Réservations Admin"
admin.site.index_title = "Gestion des réservations"
