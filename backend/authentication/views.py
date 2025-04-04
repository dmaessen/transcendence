from data.models import CustomUser, CustomUserManager
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django_otp.decorators import otp_required
from .forms import LoginForm, RegisterForm
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
# from django.contrib.auth.decorators import login_required
# from django_otp.plugins.otp_totp.models import TOTPDevice
from authentication.models import CustomTOTPDevice
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.exceptions import InvalidToken
import qrcode
import io
import base64
import pyotp
import sys

# @otp_required
def login_2fa_required(request):
    return redirect("game_server")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_2fa(request):
	user = request.user
	try:
		CustomTOTPDevice.objects.filter(customUser=user).delete() # possibly delete this later, allows reregistration.

		device, created= CustomTOTPDevice.objects.get_or_create(customUser=user, name="default")

		# print(f"Device Created: {created}, Device Confirmed: {getattr(device, 'confirmed', None)}")
		
		if not created and device.confirmed:
			return JsonResponse({"error": "2FA is already enabled"}, status=400)

		otp_secret = pyotp.random_base32()

		byte_key = base64.b32decode(otp_secret)  # Convert from Base32 to raw bytes
		base32_key = base64.b32encode(byte_key).decode().rstrip("=")
		
		device.key = base32_key
		device.confirmed = False
		print(f"OTP Secret before saving: {otp_secret}")
		device.save()
		
		print(f"Stored OTP Secret: {otp_secret}") 

		if not isinstance(otp_secret, str) or len(otp_secret) < 16:
			return JsonResponse({"error": "Invalid OTP secret generated"}, status=500)


		device = CustomTOTPDevice.objects.filter(customUser=user).first()

		totp = pyotp.TOTP(device.key)
		otp_uri = totp.provisioning_uri(name=user.email, issuer_name="transcendence")
		print("OTP URI:", otp_uri)
		qr = qrcode.make(otp_uri)
		stream = io.BytesIO()
		qr.save(stream, format="PNG")
		qr_data = base64.b64encode(stream.getvalue()).decode("utf-8")

		# user.two_factor_enabled = True
		# user.save()
		return JsonResponse({"qr_code": f"data:image/png;base64,{qr_data}", "otp_secret": otp_secret})
	except Exception as e:
		print(f"Error in register_2fa: {str(e)}")  # Debugging output
		return JsonResponse({"error": "Failed to register 2FA", "details": str(e)}, status=400)

class RegisterView(APIView):
	def post(self, request, *args, **kwargs):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()

			#check if user exists in db by email
			if not CustomUser.objects.filter(email=user.email).exists():
				return Response({'error': 'User was not created'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
			#return token
			refresh = RefreshToken.for_user(user)
			return Response(
				{
				'refresh': str(refresh),
				'access': str(refresh.access_token),
				'message': 'user created successfully!'
				},
				status=status.HTTP_201_CREATED,
			)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class UserTOTPDevice(TOTPDevice):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         if not self.user.two_factor_enabled:
#             self.user.two_factor_enabled = True
#             self.user.save(update_fields=["two_factor_enabled"])

class LoginView(APIView):
	def post(self, request):
		email = request.data.get('email')
		password = request.data.get('password')
		otp_token = request.data.get('otp_token', None)
		# device = CustomTOTPDevice.objects.filter(customUser=user).first()

		if not email or not password:
			return JsonResponse({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			user = CustomUser.objects.get(email=email)
		except CustomUser.DoesNotExist:
			return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

		if not user.check_password(password):
			return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

		device = CustomTOTPDevice.objects.filter(customUser=user).first()

		if user.two_factor_enabled:
			if not device:
				return JsonResponse({'error': '2FA is enabled but no secret is set'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			if not otp_token:
				return JsonResponse({'error': '2FA required'}, status=status.HTTP_403_FORBIDDEN)
			print(f"Received OTP Token: '{otp_token}' (Length: {len(otp_token)})", file=sys.stderr)
			otp_secret = device.key
			print(f"Stored OTP Secret (Base32): {otp_secret}", file=sys.stderr)
			# print(f"Decoded OTP Secret: {base64.b32decode(otp_secret)}")
			totp = pyotp.TOTP(otp_secret)
			print(f"totp: {totp}", file=sys.stderr)
			if not totp.verify(otp_token, valid_window=2):
				print(f"OTP verification failed. Token: {otp_token}, Secret: {otp_secret}")
				return JsonResponse({'error': 'Invalid 2FA code'}, status=status.HTTP_401_UNAUTHORIZED)
		try:
			refresh = RefreshToken.for_user(user)
			access_token = str(refresh.access_token)
		except Exception as e:
			return JsonResponse({'error': f'Token generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		return JsonResponse({
			'refresh': str(refresh),
			'access': access_token,
			'message': 'Login successful'
		})

User = get_user_model()

class DeleteAccountView(APIView):
	permission_classes = [permissions.IsAuthenticated]
	def delete(self, request):
		user = request.user
		print(f"Auth Header: {request.headers.get('Authorization')}")
		print(f"Deleting user: {request.user}")
		try:
			print(f"Deleting user: {user.email}")
			
			CustomTOTPDevice.objects.filter(customUser=user).delete()
			user.delete()
			return Response({"message": "Account deleted sucessfully"}, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			print(f"Error deleting account: {str(e)}")  # Debugging line
			return Response({"error": "Failed to delete account", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sign_out(request):
	logout(request)
	messages.success(request,f'You have been logged out')
	return HttpResponse("you have been signed out")
	# return redirect('sign_in')

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
	user = request.user
	device = CustomTOTPDevice.objects.filter(customUser=user).first()

	if not device:
		return Response({"error": "No 2FA device found for this user"}, status=400)

	device.confirmed = True
	device.save()
	user.two_factor_enabled = True
	user.save()

	return Response({"message": "2FA has been enabled succesfully"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
	user = request.user
	device = CustomTOTPDevice.objects.filter(customUser=user).first()
	if not device:
		return Response({"error": "2FA is not enabled for this user."}, status=400)

	device.delete()
	user.two_factor_enabled = False
	user.save()

	return Response({"message": "2FA has been disabled successfully."}, status=200)

@api_view(["POST"])
@permission_classes([AllowAny]) 
def refresh_token(request):
    re = request.data.get("refresh_token")

    if not re:
        return Response({"error": "Refresh token is required"}, status=400)

    try:
        refresh = RefreshToken(re)
        ac_token = str(refresh.access_token)
        re_token = str(refresh) 

        return Response({
            "access_token": ac_token,
            "refresh_token": re_token
        })
    except InvalidToken:
        return Response({"error": "Invalid refresh token"}, status=401)

def home(request):
	return render(request, 'base.html')
