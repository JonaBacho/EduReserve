# EduReserve
# Système de Gestion de Réservations - Guide d'Installation

## 📋 Description

API REST complète pour la gestion des réservations de salles et de matériel pédagogique dans un établissement éducatif, développée avec Django et Django REST Framework.

## ✨ Fonctionnalités

### 🔐 Authentification et Permissions
- **Enseignants** : Peuvent effectuer des réservations
- **Étudiants** : Peuvent consulter le planning des salles
- **Responsables de formation** : Peuvent éditer les récapitulatifs horaires

### 📅 Gestion des Réservations
- Réservation de salles de cours
- Réservation de matériel pédagogique (ordinateurs, vidéoprojecteurs, etc.)
- Créneaux fixes de 2h avec pauses (8h-17h45)
- Vérification automatique des conflits

### 📊 Planning et Récapitulatifs
- Planning général des salles (accessible à tous)
- Récapitulatifs horaires par enseignant (enseignants uniquement)
- Statistiques d'utilisation
- API de vérification de disponibilité

## 🚀 Installation

### 1. Prérequis
```bash
Python 3.8+
PostgreSQL (ou SQLite pour le développement)
pip
virtualenv (recommandé)
```

### 2. Cloner et configurer le projet
```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration de la base de données

#### Option A: PostgreSQL (Production)
```bash
# Créer la base de données
createdb reservations_db

# Modifier settings.py pour PostgreSQL (déjà configuré)
```

#### Option B: SQLite (Développement)
```python
# Dans settings.py, remplacer la configuration DATABASES par:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 4. Migration et initialisation
```bash
# Créer et appliquer les migrations
python manage.py makemigrations reservations
python manage.py migrate

# Initialiser avec des données de test
python manage.py init_reservations

# Ou initialiser en supprimant les données existantes
python manage.py init_reservations --clear
```

### 5. Démarrer le serveur
```bash
python manage.py runserver
```

## 📚 Endpoints API

### 🔗 URLs principales
- **Admin Django** : `http://127.0.0.1:8000/admin/`
- **API Root** : `http://127.0.0.1:8000/api/`
- **API Documentation** : Les endpoints sont auto-documentés via DRF

### 🎯 Endpoints CRUD

#### Utilisateurs
- `GET /api/users/` - Liste des utilisateurs
- `GET /api/users/{id}/` - Détail utilisateur
- Paramètres: `?user_type=enseignant` ou `?user_type=etudiant`

#### Formations
- `GET/POST /api/formations/` - Liste/Créer formations
- `GET/PUT/PATCH/DELETE /api/formations/{id}/` - Détail formation

#### Salles
- `GET/POST /api/salles/` - Liste/Créer salles
- `GET/PUT/PATCH/DELETE /api/salles/{id}/` - Détail salle
- `GET /api/salles/{id}/planning/` - Planning d'une salle

#### Matériels
- `GET/POST /api/materiels/` - Liste/Créer matériels
- `GET/PUT/PATCH/DELETE /api/materiels/{id}/` - Détail matériel
- `GET /api/materiels/{id}/planning/` - Planning d'un matériel
- Paramètres: `?type_materiel={id}`

#### Réservations Salles
- `GET/POST /api/reservations-salles/` - Liste/Créer réservations
- `GET/PUT/PATCH/DELETE /api/reservations-salles/{id}/` - Détail réservation
- Paramètres: `?date=YYYY-MM-DD`, `?salle={id}`, `?formation={id}`

#### Réservations Matériels
- `GET/POST /api/reservations-materiels/` - Liste/Créer réservations
- `GET/PUT/PATCH/DELETE /api/reservations-materiels/{id}/` - Détail réservation
- Paramètres: `?date=YYYY-MM-DD`, `?materiel={id}`, `?formation={id}`

#### Récapitulatifs Horaires
- `GET/POST /api/recapitulatifs/` - Liste/Créer récapitulatifs
- `GET/PUT/PATCH/DELETE /api/recapitulatifs/{id}/` - Détail récapitulatif
- Paramètres: `?formation={id}`, `?enseignant={id}`, `?date=YYYY-MM-DD`

### 🔧 Endpoints spéciaux

#### Planning Général
```http
GET /api/planning/?date=2024-01-15
```

#### Mes Réservations
```http
GET /api/mes-reservations/?date_debut=2024-01-01&date_fin=2024-01-31
```

#### Planning d'un Enseignant
```http
GET /api/planning-enseignant/{enseignant_id}/?date_debut=2024-01-01&date_fin=2024-01-31
```

#### Vérification de Disponibilité
```http
POST /api/disponibilite/
{
    "type_ressource": "salle",
    "ressource_id": 1,
    "date": "2024-01-15",
    "creneau_id": 1
}
```

#### Statistiques
```http
GET /api/statistiques/
```

## 👤 Comptes de test

Après l'initialisation, vous pouvez utiliser ces comptes :

- **Admin** : `admin` / `admin123`
- **Enseignant** : `prof.martin` / `password123`
- **Étudiant** : `etudiant1` / `password123`

## 🔒 Permissions

### Matrice des permissions

| Action | Enseignant | Étudiant | Responsable Formation |
|--------|------------|----------|----------------------|
| Voir planning salles | ✅ | ✅ | ✅ |
| Voir récapitulatifs | ✅ | ❌ | ✅ |
| Créer réservations | ✅ | ❌ | ✅ |
| Modifier ses réservations | ✅ | ❌ | ✅ |
| Modifier récapitulatifs | ❌ | ❌ | ✅ (sa formation) |

## 📋 Créneaux Horaires

Le système utilise des créneaux fixes de 2h :

- **08:00 - 10:00** (Pause 15min)
- **10:15 - 12:15** (Grande pause déjeuner)
- **13:30 - 15:30** (Pause 15min)
- **15:45 - 17:45**

## 🧪 Tests et Validation

### Validation automatique
- Les réservations ne peuvent pas être faites dans le passé
- Vérification automatique des conflits de réservation
- Validation des créneaux horaires
- Permissions strictes selon le type d'utilisateur

### Tests manuels recommandés
1. Créer une réservation de salle
2. Tenter de créer une réservation en conflit
3. Vérifier les permissions étudiants vs enseignants
4. Tester la modification des récapitulatifs par les responsables

## 🔧 Configuration Avancée

### Variables d'environnement (optionnel)
```bash
# Créer un fichier .env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/reservations_db
```

### Production
```bash
# Collecter les fichiers statiques
python manage.py collectstatic

# Déployer avec Gunicorn
gunicorn myproject.wsgi:application
```

## 📈 Fonctionnalités Avancées

### Pagination
Toutes les listes sont paginées (20 éléments par page par défaut)
- Paramètre: `?page=2&page_size=50`

### Filtrage et Recherche
- Filtres par date, formation, enseignant
- Recherche textuelle sur les noms/descriptions

### Sérialisation Complète
- Tous les objets liés sont inclus dans les réponses
- Relations détaillées (ex: `enseignant_detail`, `salle_detail`)

## 🚨 Limitations et Considérations

1. **Timezone** : Configuré pour Europe/Paris
2. **Jours ouvrables** : Tous les jours sont considérés ouvrables
3. **Créneaux fixes** : Pas de créneaux personnalisables
4. **Pas de notifications** : Le système ne gère pas les notifications automatiques

## 🔄 Maintenance

### Commandes utiles
```bash
# Sauvegarder les données
python manage.py dumpdata reservations > backup.json

# Restaurer les données
python manage.py loaddata backup.json

# Nettoyer les réservations passées (à programmer en cron)
python manage.py shell -c "
from reservations.models import ReservationSalle, ReservationMateriel
from django.utils import timezone
ReservationSalle.objects.filter(date__lt=timezone.now().date()).delete()
ReservationMateriel.objects.filter(date__lt=timezone.now().date()).delete()
"
```

## 🎯 Prochaines Étapes

1. Intégrer un système de notifications par email
2. Ajouter une interface web (React/Vue.js)
3. Implémenter des créneaux personnalisables
4. Ajouter la gestion des récurrences
5. Système de validation par responsable

---

**🎉 Votre système de réservations est prêt à être utilisé !**
