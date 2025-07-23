from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import EmailVerification, DogProfile, CustomUser
from .serializers import (
    UserCreateSerializer, LoginSerializer,
    EmailVerificationSerializer, VerifyCodeSerializer,
    ResetPasswordWithCodeSerializer, DogProfileSerializer
)
from .utils import send_verification_email, generate_code
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied

User = get_user_model()

# =============================
# Register New User
# =============================
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        user = serializer.save()
        code = EmailVerification.objects.create(user=user, purpose='register')
        send_verification_email(user.email, code.code, purpose='register')

# =============================
# Login View
# =============================
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'is_verified': user.is_verified,
                'role': user.role
            }
        })

# =============================
# Send Verification Code (Register or Reset) — with debug
# =============================
class SendVerificationCodeView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        purpose = serializer.validated_data['purpose']

        user = get_object_or_404(User, email=email)
        EmailVerification.objects.filter(user=user, purpose=purpose).delete()

        code = EmailVerification.objects.create(user=user, purpose=purpose)
        print(f"✅ Stored code {code.code} with purpose '{purpose}' for {email}")

        send_verification_email(user.email, code.code, purpose=purpose)
        return Response({'message': f'Verification code sent to {email}'})

# =============================
# Verify Code View (no expiration check)
# =============================
class VerifyCodeView(generics.GenericAPIView):
    serializer_class = VerifyCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        purpose = serializer.validated_data['purpose']

        user = get_object_or_404(User, email=email)

        match = EmailVerification.objects.filter(
            user=user,
            code=code,
            purpose=purpose
        ).first()

        if not match:
            return Response({'error': 'Invalid or expired code.'}, status=400)

        if purpose == 'register':
            user.is_verified = True
            user.is_active = True
            user.save()
            match.delete()

        return Response({'message': 'Verification successful.'})

# =============================
# Reset Password with Code
# =============================
class ResetPasswordWithCodeView(generics.GenericAPIView):
    serializer_class = ResetPasswordWithCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        print("🔒 Incoming Reset Password Request Data:", request.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        user = get_object_or_404(User, email=email)
        match = EmailVerification.objects.filter(
            user=user,
            code=code,
            purpose='reset'
        ).first()

        if not match:
            print("❌ No matching verification code found.")
            return Response({'error': 'Invalid or expired code.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        match.delete()
        print("📄 Available reset codes:", EmailVerification.objects.filter(user=user, purpose='reset').values())

        return Response({'message': 'Password has been reset successfully.'})

# =============================
# Dog Profile View (Get/Update)
# =============================
class DogProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DogProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if user.role != 'customer':
            raise PermissionDenied("Only customers can access or modify their dog profile.")
        
        profile, created = DogProfile.objects.get_or_create(owner=user)
        return profile

# =============================
# Dog Profile Create View (New Users)
# =============================
class DogProfileCreateView(generics.CreateAPIView):
    serializer_class = DogProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.role != 'customer':
            raise PermissionDenied("Only customers can create dog profiles.")
        
        if DogProfile.objects.filter(owner=self.request.user).exists():
            raise PermissionDenied("Dog profile already exists.")

        serializer.save(owner=self.request.user)

# =============================
# Resend Verification Code
# =============================
class ResendVerificationCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        purpose = request.data.get('purpose', 'register')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            if user.is_verified and purpose == 'register':
                return Response({'message': 'Email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)

            code = generate_code()
            EmailVerification.objects.create(user=user, code=code, purpose=purpose)
            send_verification_email(email, code, purpose=purpose)

            return Response({'message': 'Verification code resent successfully.'}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

# =============================
# Admin Only: List All Users
# =============================
@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_users(request):
    users = User.objects.all().values('id', 'email', 'role', 'is_active')
    return Response(list(users))

# =============================
# Admin Only: Delete User
# =============================
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"message": "User deleted."}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# =============================
# Public: Create Superuser
# =============================
@api_view(['POST'])
@permission_classes([AllowAny])
def create_superuser_view(request):
    if User.objects.filter(is_superuser=True).exists():
        return Response({'message': 'Superuser already exists.'})

    user = User.objects.create_superuser(
        email='vincentgrey57@gmail.com',
        password='canineracks',
        is_verified=True
    )
    return Response({'message': 'Superuser created', 'email': user.email})
