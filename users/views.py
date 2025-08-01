from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random
import string
from datetime import timedelta
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)
from .permissions import IsSuperAdmin, IsAdmin, IsManager, IsOwner

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        # Open endpoints
        if self.action in ['create', 'destroy', 'send_otp', 'verify_otp']:
            return [AllowAny()]

        # Change or view own password/profile
        if self.action in ['update', 'partial_update', 'change_password', 'me']:
            return [IsAuthenticated()]

        # List and retrieve controlled by roles
        user = self.request.user
        if self.action in ['list', 'retrieve']:
            # Super Admin
            if user.is_superuser or user.has_role('admin'):
                return [IsSuperAdmin()]
            if user.has_role('manager'):
                return [IsManager()]
            if user.has_role('owner'):
                return [IsOwner()]
        # Default
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # Super Admin can see all users
        if user.is_superuser or user.has_role('admin'):
            return User.objects.all()
        # Manager sees agronomists, quality control, field officers, farmers
        if user.has_role('manager'):
            return User.objects.filter(role__name__in=['agronomist', 'qualitycontrol', 'fieldofficer', 'farmer'])
        # Owner only sees self
        if user.has_role('owner'):
            return User.objects.filter(id=user.id)
        # Default: only own record
        return User.objects.filter(id=user.id)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk=None):
        user_obj = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user_obj.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Wrong password.'}, status=status.HTTP_400_BAD_REQUEST)

        user_obj.set_password(serializer.validated_data['new_password'])
        user_obj.save()
        return Response({'status': 'password changed'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def send_otp(self, request):
        email = request.data.get('email') or None
        username = request.data.get('username') or None
        if not email and not username:
            return Response({'detail': 'Email or username required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email) if email else User.objects.get(username=username)
            email = user.email
            if not email:
                raise User.DoesNotExist
        except User.DoesNotExist:
            return Response({'detail': 'User not found or no registered email'}, status=status.HTTP_404_NOT_FOUND)

        # Generate and store OTP
        otp = ''.join(random.choices(string.digits, k=6))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        print(f"OTP for {email}: {otp}")

        # Send email (silent fail)
        try:
            send_mail(
                'Your OTP for Login',
                f'Your OTP is: {otp}. Expires in 10 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
        except Exception:
            pass

        return Response({'detail': 'OTP sent successfully'})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_otp(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        if not email or not otp:
            return Response({'detail': 'Email and OTP required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if not user.otp_created_at or timezone.now() - user.otp_created_at > timedelta(minutes=10):
            return Response({'detail': 'OTP expired or not found'}, status=status.HTTP_400_BAD_REQUEST)

        if str(user.otp) != str(otp):
            return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP and issue tokens
        user.otp = None
        user.otp_created_at = None
        user.save()
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})
