from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),

    path('send-code/', views.SendVerificationCodeView.as_view(), name='send-code'),
    path('verify-code/', views.VerifyCodeView.as_view(), name='verify-code'),
    path('resend-code/', views.ResendVerificationCodeView.as_view(), name='resend-code'),

    path('reset-password/', views.ResetPasswordWithCodeView.as_view(), name='reset-password'),
    path('dog-profile/', views.DogProfileView.as_view(), name='dog-profile'),
    path('dog-profile/create/', views.DogProfileCreateView.as_view(), name='dog-profile-create'),

    path('create-superuser/', views.create_superuser_view),
    path('list/', views.list_users),
    path('delete/<int:user_id>/', views.delete_user),

]
