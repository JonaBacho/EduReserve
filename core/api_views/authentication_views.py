from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.tokens import RefreshToken
from core.serializers import UserSerializer, RegisterSerializer, PasswordResetSerializer, LoginSerializer
from core.paginations import StandardResultsSetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator

User = get_user_model()


tags = ["types-matériels"]
auth_header_param = openapi.Parameter(
    name="Authorization",
    in_=openapi.IN_HEADER,
    description="Token JWT pour l'authentification (Bearer <token>)",
    type=openapi.TYPE_STRING,
    required=True
)

@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_summary="Liste des utilisateurs",
        operation_description="Récupère la liste de tous les utilisateurs avec filtres optionnels",
        manual_parameters=[
            openapi.Parameter(
                'user_type',
                openapi.IN_QUERY,
                description="Filtrer par type d'utilisateur (enseignant, responsable_formation, etc.)",
                type=openapi.TYPE_STRING
            ),
            auth_header_param
        ],
        tags = tags
    )
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_summary="Détails d'un utilisateur",
        operation_description="Récupère les détails d'un utilisateur spécifique",
        manual_parameters=[auth_header_param],
        tags = tags
    )
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = User.objects.all()
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Créer un compte",
        operation_description="Crée un nouveau compte utilisateur",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Compte créé avec succès",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Données invalides"
            )
        },
        tags=["Authentification"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Se connecter",
        operation_description="Authentifie un utilisateur et retourne les tokens JWT",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Connexion réussie",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Identifiants invalides"
            )
        },
        tags=["Authentification"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })
        return Response(serializer.errors, status=400)


class PasswordResetView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Changer le mot de passe",
        operation_description="Modifie le mot de passe de l'utilisateur connecté",
        request_body=PasswordResetSerializer,
        responses={
            200: openapi.Response(
                description="Mot de passe modifié avec succès",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Données invalides ou ancien mot de passe incorrect"
            )
        },
        tags=["Authentification"]
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({"detail": "Ancien mot de passe incorrect"}, status=400)

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return Response({"detail": "Mot de passe mis à jour"})
        return Response(serializer.errors, status=400)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Utilisateur actuel",
        operation_description="Récupère les informations de l'utilisateur connecté",
        responses={
            200: openapi.Response(
                description="Informations utilisateur récupérées avec succès",
                schema=UserSerializer
            )
        },
        tags=["Authentification"]
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)