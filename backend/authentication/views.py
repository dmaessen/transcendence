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
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
# from django.contrib.auth.decorators import login_required
# from django_otp.plugins.otp_totp.models import TOTPDevice
from authentication.models import CustomTOTPDevice
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.exceptions import InvalidToken
# from google.oauth2 import id_token as google_id_token
# from google.auth.transport import requests as google_requests
from django.views.decorators.csrf import csrf_exempt
import google.oauth2.id_token
import google.auth.transport.requests
# import google.oauth2 
import requests
import qrcode
import io
import base64
import pyotp
# from passlib.totp import TOTP
import sys
from django.core.cache import cache
from django.conf import settings


# @otp_required
def login_2fa_required(request):
    return redirect("game_server")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_2fa(request):
	user = request.user
	try:

		CustomTOTPDevice.objects.filter(customUser=user, confirmed=False).exclude(name="default").delete()
		device = CustomTOTPDevice.objects.filter(customUser=user, confirmed=False).first()

		if not device:
			device = CustomTOTPDevice(customUser=user, name="default")
			otp_secret = pyotp.random_base32()
			device.key = otp_secret
			device.confirmed = False
			device.save()
		else:
			otp_secret = device.key
		
		print("[DEBUG] All TOTP devices for user(in registration):")
		for d in CustomTOTPDevice.objects.filter(customUser=user):
			print(f"  - name: {d.name}, key: {d.key}, confirmed: {d.confirmed}")
		print(f"[DEBUG] Generated secret: {otp_secret}")
		print(f"[DEBUG] Device key saved: {device.key}")
		# print(f"Stored OTP Secret: {otp_secret}") 

		if not isinstance(otp_secret, str) or len(otp_secret) < 16:
			return JsonResponse({"error": "Invalid OTP secret generated"}, status=500)


		# device = CustomTOTPDevice.objects.filter(customUser=user).first()

		totp = pyotp.TOTP(device.key)
		otp_uri = totp.provisioning_uri(name=user.email, issuer_name="transcendence")
		print("OTP URI:", otp_uri)
		qr = qrcode.make(otp_uri)
		stream = io.BytesIO()
		qr.save(stream, format="PNG")
		qr_data = base64.b64encode(stream.getvalue()).decode("utf-8")

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

		if not email or not password:
			return JsonResponse({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

		print(f"login data received: {request.data}", file=sys.stderr)
		try:
			user = CustomUser.objects.get(email=email)
		except CustomUser.DoesNotExist:
			return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

		if not user.check_password(password):
			return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

		device = CustomTOTPDevice.objects.filter(customUser=user).first()

		if user.two_factor_enabled:
			print("[DEBUG] All TOTP devices for user(in login):")
			for d in CustomTOTPDevice.objects.filter(customUser=user):
				print(f"  - name: {d.name}, key: {d.key}, confirmed: {d.confirmed}")
			if not device:
				return JsonResponse({'error': '2FA is enabled but no secret is set'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			if not otp_token:
				return JsonResponse({'error': '2FA required'}, status=status.HTTP_403_FORBIDDEN)
			otp_secret = device.key
			totp = pyotp.TOTP(otp_secret)

			print(f"[DEBUG] Device used for verification: name={device.name}, key={otp_secret}")
			if not totp.verify(otp_token, valid_window=1):
				print(f"totp current: {totp.now()}", file=sys.stderr)
				print(f"OTP verification failed. Token: {otp_token}, Secret: {otp_secret}", file=sys.stderr)
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
		try:
			# Count devices before deletion
			initial_count = CustomTOTPDevice.objects.filter(customUser=user).count()
			print(f"Initial device count: {initial_count}")

			with transaction.atomic():
				# Delete all devices associated with the user
				deleted_count, _ = CustomTOTPDevice.objects.filter(customUser=user).delete()
				print(f"Deleted {deleted_count} device(s).")

				# Count devices after deletion
				final_count = CustomTOTPDevice.objects.filter(customUser=user).count()
				print(f"Final device count: {final_count}")

				# Optionally, delete the user account
				user.delete()
				print(f"[DeleteAccountView] Before deletion: {initial_count} 2FA device(s) found for user {user.email}")
				print(f"[DeleteAccountView] Deleted {deleted_count} 2FA device(s) for user {user.email}")
				print(f"[DeleteAccountView] After deletion: {final_count} 2FA device(s) remaining for user {user.email}")

			return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			print(f"Error deleting account: {str(e)}")  # Debugging line
			return Response({"error": "Failed to delete account", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sign_out(request):
	user = request.user
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

@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt
def google_login(request):
	# from google.auth.transport import requests as google_requests
	# from google.oauth2 import id_token as google_id_token
	client_id = settings.GOOGLE_CLIENT_ID
	print(f"google client id: [", client_id, "]", file=sys.stderr)
	if not client_id:
		return JsonResponse({'error': 'no client id'}, status=status.HTTP_403_FORBIDDEN)
	if client_id != "517456269488-9cioqmptmcqvl54r3jh1ti36a579gvts.apps.googleusercontent.com":
		print(f"[WARNING] Unrecognized client ID received: {client_id}")
	
	body = json.loads(request.body)
	token = body.get("id_token")
	if not token:
		return Response({"error": "Missing id_token"}, status=400)
	
	try:
		request_adapter = google.auth.transport.requests.Request()
		idinfo = google_id_token.verify_oauth2_token(token, request_adapter, client_id)
		email = idinfo.get("email")
		if not email:
			return JsonResponse({"error":"no email in response token"}, status=status.HTTP_400_BAD_REQUEST)
		username = idinfo.get("name", email.split("@")[0])
		if not username:
			return JsonResponse({"error":"no name in response token"}, status=status.HTTP_400_BAD_REQUEST)
		print("response from google, email: ", email, " ,name: ", username)
		
		user, created = CustomUser.objects.get_or_create(email=email, defaults={"username": username})
		if created:
			user.set_unusable_password()
			user.save()

		refresh = RefreshToken.for_user(user)
		return Response({
			"refresh": str(refresh),
			"access": str(refresh.access_token),
			"message": "Google login successful"
		})
	except ValueError as e:
		return Response({"error": "Invalid ID token", "details": str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "two_factor_enabled": hasattr(user, 'totp_device') and user.totp_device.confirmed,
    })

def login_42_redirect(request):
    base_url = "https://api.intra.42.fr/oauth/authorize"
    return redirect(
        f"{base_url}?client_id={settings.FT_CLIENT_ID}"
        f"&redirect_uri={settings.FT_REDIRECT_URI}"
        f"&response_type=code"
    )

def login_42_callback(request):
	code = request.GET.get("code")
	if not code:
		return JsonResponse({"error": "No code provided"}, status=400)

	# Exchange code for token
	token_response = requests.post("https://api.intra.42.fr/oauth/token", data={
		"grant_type": "authorization_code",
		"client_id": settings.FT_CLIENT_ID,
		"client_secret": settings.FT_CLIENT_SECRET,
		"code": code,
		"redirect_uri": settings.FT_REDIRECT_URI,
	})

	if token_response:
		return JsonResponse({"data returned from 42 api:": token_response}, status=200)
	else:
		return JsonResponse({"error": "no token response"})

	token_data = token_response.json()
	access_token = token_data.get("access_token")
	if not access_token:
		return JsonResponse({"error": "Failed to retrieve access token"}, status=400)

    # Use token to get user info
	user_response = requests.get("https://api.intra.42.fr/v2/me", headers={
		"Authorization": f"Bearer {access_token}"
	})

	profile = user_response.json()
	email = profile.get("email")
	username = profile.get("login")

	print(f"regestering user with email: ", email, "and username:", username)
	# Register or log in the user
	user, created = CustomUser.objects.create(email=email, defaults={"username": username})
	if created:
		user.save()
	else:
		return JsonResponse({"error": "Failed to create user"})

	# Issue your JWT tokens (or login session)
	refresh = RefreshToken.for_user(user)
	return JsonResponse({
		"access": str(refresh.access_token),
		"refresh": str(refresh)
	})

