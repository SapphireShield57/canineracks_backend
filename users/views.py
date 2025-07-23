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

        # ✅ Delete previous codes for that user and purpose
        EmailVerification.objects.filter(user=user, purpose=purpose).delete()

        # ✅ Generate new code and save with correct purpose
        code = EmailVerification.objects.create(user=user, purpose=purpose)
        print(f"✅ Stored code {code.code} with purpose '{purpose}' for {email}")  # DEBUG

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
            user.is_active = True  # ✅ Activate user after email is verified
            user.save()
            match.delete()

        return Response({'message': 'Verification successful.'})



# =============================
# Reset Password with Code (no expiration check)
# =============================
class ResetPasswordWithCodeView(generics.GenericAPIView):
    serializer_class = ResetPasswordWithCodeSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        print("🔒 Incoming Reset Password Request Data:", request.data)  # DEBUG

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
            print("❌ No matching verification code found.")  # DEBUG
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
        profile, created = DogProfile.objects.get_or_create(owner=self.request.user)
        return profile


# =============================
# Resend Verification Code (Register or Reset)
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


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_users(request):
    User = get_user_model()
    users = User.objects.all().values('id', 'email', 'role', 'is_active')
    return Response(list(users))



@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ This makes it accessible without login
def create_superuser_view(request):
    if User.objects.filter(is_superuser=True).exists():
        return Response({'message': 'Superuser already exists.'})

    user = User.objects.create_superuser(
        email='vincentgrey57@gmail.com',
        password='canineracks',
        is_verified=True  # If using is_verified
    )
    return Response({'message': 'Superuser created', 'email': user.email})
