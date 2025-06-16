# management/commands/init_reservations.py
import os
import random
import string
from django.utils.text import slugify
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, time, date, timedelta
from core.models import (
    Formation, Salle, TypeMateriel, Materiel, CreneauHoraire,
    ReservationSalle, ReservationMateriel, RecapitulatifHoraire
)


User = get_user_model()


class Command(BaseCommand):
    help = 'Initialise la base de données avec des données de test pour le système de réservations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime toutes les données existantes avant l\'initialisation',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Suppression des données existantes...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Initialisation des données...'))

        # 1. Créer les créneaux horaires
        self.create_creneaux()

        # 2. Créer les utilisateurs
        self.create_users()

        # 3. Créer les formations
        self.create_formations()

        # 4. Créer les salles
        self.create_salles()

        # 5. Créer les types de matériel et matériels
        self.create_materiels()

        # 6. Créer quelques réservations de test
        self.create_reservations()

        # 7. Créer quelques récapitulatifs horaires
        self.create_recapitulatifs()

        self.stdout.write(self.style.SUCCESS('✅ Initialisation terminée avec succès!'))
        self.print_summary()

    def generate_matricule(self, prefix, user_type):
        """Génère un matricule unique sous forme PREFIX000000XX"""
        count = User.objects.filter(user_type=user_type).count() + 1
        while True:
            matricule = f"{prefix}{count:08d}"
            if not User.objects.filter(matricule=matricule).exists():
                return matricule
            count += 1

    def clear_data(self):
        """Supprime toutes les données existantes"""
        RecapitulatifHoraire.objects.all().delete()
        ReservationMateriel.objects.all().delete()
        ReservationSalle.objects.all().delete()
        Materiel.objects.all().delete()
        TypeMateriel.objects.all().delete()
        Salle.objects.all().delete()
        Formation.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        CreneauHoraire.objects.all().delete()

    def create_creneaux(self):
        """Crée les créneaux horaires fixes"""
        creneaux_data = [
            ('08:00-10:00', time(8, 0), time(10, 0)),
            ('10:15-12:15', time(10, 15), time(12, 15)),
            ('13:30-15:30', time(13, 30), time(15, 30)),
            ('15:45-17:45', time(15, 45), time(17, 45)),
        ]

        for nom, debut, fin in creneaux_data:
            creneau, created = CreneauHoraire.objects.get_or_create(
                nom=nom,
                defaults={'heure_debut': debut, 'heure_fin': fin}
            )
            if created:
                self.stdout.write(f'Créneau créé: {nom}')

    def create_users(self):
        """Crée les utilisateurs de test"""
        # Créer un superutilisateur admin
        if not User.objects.filter(username='admin').exists():
            matricule_admin = self.generate_matricule('ENS', 'enseignant')
            User.objects.create_superuser(
                matricule=matricule_admin,
                username='admin',
                email='admin@ecole.fr',
                password='admin123',
                first_name='Admin',
                last_name='Système',
                user_type='enseignant'
            )
            self.stdout.write('Superutilisateur admin créé')

        # Créer des enseignants
        enseignants_data = [
            ('prof.martin', 'martin@ecole.fr', 'Pierre', 'Martin'),
            ('prof.durand', 'durand@ecole.fr', 'Marie', 'Durand'),
            ('prof.bernard', 'bernard@ecole.fr', 'Jean', 'Bernard'),
            ('prof.petit', 'petit@ecole.fr', 'Sophie', 'Petit'),
            ('prof.moreau', 'moreau@ecole.fr', 'Lucas', 'Moreau'),
        ]

        for username, email, prenom, nom in enseignants_data:
            if not User.objects.filter(username=username).exists():
                matricule = self.generate_matricule('ENS', 'enseignant')
                User.objects.create_user(
                    matricule=matricule,
                    username=username,
                    email=email,
                    password='password123',
                    first_name=prenom,
                    last_name=nom,
                    user_type='enseignant'
                )
                self.stdout.write(f'Enseignant créé: {prenom} {nom}')

        # Créer des étudiants
        etudiants_data = [
            ('etudiant1', 'etudiant1@ecole.fr', 'Alice', 'Dupont'),
            ('etudiant2', 'etudiant2@ecole.fr', 'Bob', 'Leroy'),
            ('etudiant3', 'etudiant3@ecole.fr', 'Clara', 'Roux'),
            ('etudiant4', 'etudiant4@ecole.fr', 'David', 'Blanc'),
        ]

        for username, email, prenom, nom in etudiants_data:
            if not User.objects.filter(username=username).exists():
                matricule = self.generate_matricule('ETU', 'etudiant')
                User.objects.create_user(
                    matricule=matricule,
                    username=username,
                    email=email,
                    password='password123',
                    first_name=prenom,
                    last_name=nom,
                    user_type='etudiant'
                )
                self.stdout.write(f'Étudiant créé: {prenom} {nom}')

    def generate_unique_code(self, prefix, max_length=11):
        """Génère un code unique avec un préfixe basé sur le nom de la formation"""
        base = slugify(prefix).upper().replace('-', '')[:6]  # max 6 chars
        while True:
            suffix = ''.join(random.choices(string.digits, k=max_length - len(base)))
            code = f"{base}{suffix}"
            if not Formation.objects.filter(code=code).exists():
                return code

    def create_formations(self):
        """Crée les formations avec leurs responsables"""
        formations_data = [
            ('Informatique - Licence 1', 'Formation en informatique niveau L1', 'prof.martin'),
            ('Informatique - Licence 2', 'Formation en informatique niveau L2', 'prof.durand'),
            ('Informatique - Licence 3', 'Formation en informatique niveau L3', 'prof.bernard'),
            ('Mathématiques - Master 1', 'Formation en mathématiques niveau M1', 'prof.petit'),
            ('Physique - Master 2', 'Formation en physique niveau M2', 'prof.moreau'),
        ]

        for nom, description, responsable_username in formations_data:
            responsable = User.objects.get(username=responsable_username)
            formation, created = Formation.objects.get_or_create(
                nom=nom,
                defaults={
                    'description': description,
                    'responsable': responsable,
                    'code': self.generate_unique_code(nom)
                }
            )
            if created:
                self.stdout.write(f'Formation créée: {nom}')

    def create_salles(self):
        """Crée les salles de cours"""
        salles_data = [
            ('A101', 30, 'Tableau blanc, vidéoprojecteur'),
            ('A102', 25, 'Tableau blanc'),
            ('A201', 40, 'Tableau blanc, vidéoprojecteur, système audio'),
            ('A202', 35, 'Tableau blanc, écran tactile'),
            ('B101', 20, 'Laboratoire informatique, 20 postes'),
            ('B102', 15, 'Salle de réunion, écran TV'),
            ('C301', 50, 'Amphithéâtre, vidéoprojecteur, sonorisation'),
            ('C302', 45, 'Amphithéâtre, équipement multimédia'),
        ]

        for nom, capacite, equipements in salles_data:
            salle, created = Salle.objects.get_or_create(
                nom=nom,
                defaults={
                    'capacite': capacite,
                    'equipements': equipements
                }
            )
            if created:
                self.stdout.write(f'✓ Salle créée: {nom}')

    def create_materiels(self):
        """Crée les types de matériel et les matériels"""
        # Créer les types de matériel
        types_data = [
            ('Ordinateur portable', 'Ordinateurs portables pour enseignement'),
            ('Vidéoprojecteur', 'Vidéoprojecteurs mobiles'),
            ('Micro-ordinateur', 'Micro-ordinateurs type Raspberry Pi'),
            ('Tablette', 'Tablettes tactiles éducatives'),
        ]

        for nom, description in types_data:
            type_materiel, created = TypeMateriel.objects.get_or_create(
                nom=nom,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'✓ Type de matériel créé: {nom}')

        # Créer les matériels
        ordinateur_type = TypeMateriel.objects.get(nom='Ordinateur portable')
        videoproj_type = TypeMateriel.objects.get(nom='Vidéoprojecteur')
        micro_type = TypeMateriel.objects.get(nom='Micro-ordinateur')
        tablette_type = TypeMateriel.objects.get(nom='Tablette')

        materiels_data = [
            ('Laptop Dell 01', ordinateur_type, 'DELL001'),
            ('Laptop Dell 02', ordinateur_type, 'DELL002'),
            ('Laptop HP 01', ordinateur_type, 'HP001'),
            ('Laptop HP 02', ordinateur_type, 'HP002'),
            ('Projecteur Epson 01', videoproj_type, 'EPSON001'),
            ('Projecteur Epson 02', videoproj_type, 'EPSON002'),
            ('Projecteur BenQ 01', videoproj_type, 'BENQ001'),
            ('Raspberry Pi 01', micro_type, 'RPI001'),
            ('Raspberry Pi 02', micro_type, 'RPI002'),
            ('iPad 01', tablette_type, 'IPAD001'),
            ('iPad 02', tablette_type, 'IPAD002'),
        ]

        for nom, type_materiel, numero_serie in materiels_data:
            materiel, created = Materiel.objects.get_or_create(
                nom=nom,
                defaults={
                    'type_materiel': type_materiel,
                    'numero_serie': numero_serie
                }
            )
            if created:
                self.stdout.write(f'✓ Matériel créé: {nom}')

    def create_reservations(self):
        """Crée des réservations de test pour les prochains jours"""
        # Récupérer les objets nécessaires
        enseignants = User.objects.filter(user_type='enseignant')
        salles = Salle.objects.all()
        materiels = Materiel.objects.all()
        formations = Formation.objects.all()
        creneaux = CreneauHoraire.objects.all()

        # Dates de test (semaine prochaine)
        aujourd_hui = date.today()
        dates_test = [aujourd_hui + timedelta(days=i) for i in range(1, 6)]  # 5 jours

        # Réservations de salles
        reservations_salles_data = [
            (0, 0, 0, 0, 'Cours d\'algorithmique', 'Introduction aux algorithmes'),
            (1, 1, 1, 1, 'Cours de base de données', 'Modélisation relationnelle'),
            (2, 2, 2, 2, 'Cours de mathématiques', 'Algèbre linéaire'),
            (0, 3, 0, 3, 'TP Informatique', 'Travaux pratiques Python'),
            (1, 4, 1, 0, 'Cours de physique', 'Mécanique quantique'),
        ]

        for i, (ens_idx, salle_idx, form_idx, cren_idx, sujet, commentaire) in enumerate(reservations_salles_data):
            if i < len(dates_test):
                ReservationSalle.objects.get_or_create(
                    enseignant=enseignants[ens_idx % len(enseignants)],
                    salle=salles[salle_idx % len(salles)],
                    formation=formations[form_idx % len(formations)],
                    creneau=creneaux[cren_idx % len(creneaux)],
                    date=dates_test[i],
                    defaults={
                        'sujet': sujet,
                        'commentaires': commentaire
                    }
                )
                self.stdout.write(f'✓ Réservation salle créée: {sujet}')

        # Réservations de matériel
        reservations_materiels_data = [
            (0, 0, 0, 0, 'Pour démonstration'),
            (1, 1, 1, 1, 'TP étudiants'),
            (2, 2, 2, 2, 'Présentation cours'),
            (0, 3, 0, 3, 'Projet étudiant'),
        ]

        for i, (ens_idx, mat_idx, form_idx, cren_idx, commentaire) in enumerate(reservations_materiels_data):
            if i < len(dates_test):
                ReservationMateriel.objects.get_or_create(
                    enseignant=enseignants[ens_idx % len(enseignants)],
                    materiel=materiels[mat_idx % len(materiels)],
                    formation=formations[form_idx % len(formations)],
                    creneau=creneaux[cren_idx % len(creneaux)],
                    date=dates_test[i],
                    defaults={'commentaires': commentaire}
                )
                self.stdout.write(f'✓ Réservation matériel créée')

    def create_recapitulatifs(self):
        """Crée des récapitulatifs horaires de test"""
        formations = Formation.objects.all()
        enseignants = User.objects.filter(user_type='enseignant')
        salles = Salle.objects.all()
        creneaux = CreneauHoraire.objects.all()

        # Dates de test
        aujourd_hui = date.today()
        dates_test = [aujourd_hui + timedelta(days=i) for i in range(1, 8)]  # 7 jours

        recaps_data = [
            (0, 0, 0, 'Cours magistral - Algorithmique', 0),
            (1, 1, 1, 'TD - Base de données', 1),
            (2, 2, 2, 'TP - Programmation', 2),
            (0, 0, 3, 'Cours - Structures de données', 3),
            (1, 1, 0, 'Examen - Mathématiques', 4),
        ]

        for i, (form_idx, ens_idx, cren_idx, sujet, salle_idx) in enumerate(recaps_data):
            if i < len(dates_test):
                RecapitulatifHoraire.objects.get_or_create(
                    formation=formations[form_idx % len(formations)],
                    enseignant=enseignants[ens_idx % len(enseignants)],
                    date=dates_test[i],
                    creneau=creneaux[cren_idx % len(creneaux)],
                    defaults={
                        'sujet': sujet,
                        'salle_prevue': salles[salle_idx % len(salles)],
                        'commentaires': f'Récapitulatif pour {sujet}'
                    }
                )
                self.stdout.write(f'✓ Récapitulatif créé: {sujet}')

    def print_summary(self):
        """Affiche un résumé des données créées"""
        self.stdout.write(self.style.SUCCESS('\n📊 RÉSUMÉ DES DONNÉES CRÉÉES:'))
        self.stdout.write(f'Utilisateurs: {User.objects.count()}')
        self.stdout.write(f'   - Enseignants: {User.objects.filter(user_type="enseignant").count()}')
        self.stdout.write(f'   - Étudiants: {User.objects.filter(user_type="etudiant").count()}')
        self.stdout.write(f'Formations: {Formation.objects.count()}')
        self.stdout.write(f'Salles: {Salle.objects.count()}')
        self.stdout.write(f'Types de matériel: {TypeMateriel.objects.count()}')
        self.stdout.write(f'Matériels: {Materiel.objects.count()}')
        self.stdout.write(f'Créneaux horaires: {CreneauHoraire.objects.count()}')
        self.stdout.write(f'Réservations salles: {ReservationSalle.objects.count()}')
        self.stdout.write(f'Réservations matériels: {ReservationMateriel.objects.count()}')
        self.stdout.write(f'Récapitulatifs horaires: {RecapitulatifHoraire.objects.count()}')

        self.stdout.write(self.style.SUCCESS('\n INFORMATIONS DE CONNEXION:'))
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Enseignant exemple: prof.martin / password123')
        self.stdout.write('Étudiant exemple: etudiant1 / password123')
