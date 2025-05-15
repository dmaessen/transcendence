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
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .serializers import UserSerializer
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
# from django.contrib.auth.decorators import login_required
# from django_otp.plugins.otp_totp.models import TOTPDevice
from authentication.models import CustomTOTPDevice
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken
# from google.oauth2 import id_token as google_id_token
# from google.auth.transport import requests as google_requests
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import google.oauth2.id_token as google_id_token
import google.auth.transport.requests
from django.views.decorators.csrf import ensure_csrf_cookie
from urllib.parse import urlencode
# import google.oauth2 
import json
import requests
import qrcode
import io
import base64
import pyotp
import sys
from django.core.cache import cache
from django.conf import settings
import logging
from django.middleware.csrf import get_token


logger = logging.getLogger(__name__)
logger.info("This is a test log from authentication.views")


# @otp_required
def login_2fa_required(request):
    return redirect("/")

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
		
		for d in CustomTOTPDevice.objects.filter(customUser=user):
			print(f"  - name: {d.name}, key: {d.key}, confirmed: {d.confirmed}")

		if not isinstance(otp_secret, str) or len(otp_secret) < 16:
			return JsonResponse({"error": "Invalid OTP secret generated"}, status=500)

		totp = pyotp.TOTP(device.key)
		otp_uri = totp.provisioning_uri(name=user.email, issuer_name="transcendence")
		print("OTP URI:", otp_uri)
		qr = qrcode.make(otp_uri)
		stream = io.BytesIO()
		qr.save(stream, format="PNG")
		qr_data = base64.b64encode(stream.getvalue()).decode("utf-8")

		return JsonResponse({"qr_code": f"data:image/png;base64,{qr_data}", "otp_secret": otp_secret})
	except Exception as e:
		return JsonResponse({"error": "Failed to register 2FA", "details": str(e)}, status=400)

class RegisterView(APIView):
	@csrf_exempt
	def post(self, request, *args, **kwargs):
		print(f"[DEBUG] register view")
		serializer = UserSerializer(data=request.data)
		print(f"[DEBUG] post serializer")
		if serializer.is_valid():
			user = serializer.save()

			#check if user exists in db by email
			if not CustomUser.objects.filter(email=user.email).exists():
				return Response({'error': 'User was not created'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
			
			#return token
			refresh = RefreshToken.for_user(user)
			access_token = refresh.access_token
			response = JsonResponse({
				'message': 'Login successful'
			})
			response.set_cookie(
				key="access_token",
				value=str(access_token),
				httponly=True,
				samesite='Lax',
				secure=False,  # [FLIP]set to True in production
				max_age=300
			)
			response.set_cookie(
				key="refresh_token",
				value=str(refresh),
				httponly=True,
				samesite='lax',
				secure=False, # [FLIP]set to True in production
				max_age=86400
			)
			print("register response: ", response)
			return response
		return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
	@csrf_exempt
	def post(self, request):
		email = request.data.get('email')
		password = request.data.get('password')
		otp_token = request.data.get('otp_token', None)
		logging.info(f"login data received: {request.data}")
		if not email or not password:
			return JsonResponse({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

		print(f"login data received: {request.data}", flush=True)
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

			if not totp.verify(otp_token, valid_window=1):
				return JsonResponse({'error': 'Invalid 2FA code'}, status=status.HTTP_401_UNAUTHORIZED)
		try:
			user = CustomUser.objects.get(email=email)
			print(f"[DEBUG] Found user: {user.email}")
		except CustomUser.DoesNotExist:
			print(f"[DEBUG] User not found: {email}")
			return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

		if not user.check_password(password):
			print(f"[DEBUG] Password check failed for user: {email}")
			return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
		try:
			refresh = RefreshToken.for_user(user)
			access_token = refresh.access_token
			print(f"[DEBUG] made access token: ", access_token)
		except Exception as e:
			return JsonResponse({'error': f'Token generation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		print(f"[DEBUG] going to return access token: ", access_token)
		response = JsonResponse({
			'message': 'Login successful'
		})
		response.set_cookie(
			key="access_token",
			value=str(access_token),
			httponly=True,
			samesite='Lax',
			secure=False,  # [FLIP]set to True in production
			max_age=300
		)
		response.set_cookie(
			key="refresh_token",
			value=str(refresh),
			httponly=True,
			samesite='Lax',
			secure=False, # [FLIP]set to True in production
			max_age=86400
		)
		return response

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

			return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
		except Exception as e:
			print(f"Error deleting account: {str(e)}")  # Debugging line
			return Response({"error": "Failed to delete account", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	

def perform_logout(request):
    logout(request)
    response = {
        "message": "you have been signed out"
    }
    return response

# @csrf_exempt
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def sign_out(request):
	# print(f">>>>>>>>>User: {request.user}")
	user = request.user
	perform_logout(request)
	messages.success(request, 'You have been logged out')
	response = JsonResponse({"message": "you have been signed out"})
	response.delete_cookie("access_token")
	response.delete_cookie("refresh_token")
	return response
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

class RefreshTokenView(APIView):
	def post(self, request):
		logging.info(f"!>!>!>!>!>!Request Cookies: {request.COOKIES}")
		# logging.info(f"!>!>!>!>!>!CSRF Token: {request.META}")

		refresh_token = request.COOKIES.get('refresh_token')
		logging.info(f"!>!>!>!>!>!Refresh token: {refresh_token}")
		if not refresh_token:
			return JsonResponse({"error": "no refresh token"})
			# raise AuthenticationFailed("No refresh token in cookies")
		try:
			token = RefreshToken(refresh_token)
			access_token = token.access_token
		except Exception as e:
			raise AuthenticationFailed("Invalid refresh token")

		if not access_token: 
			return JsonResponse({"error": "unable to refresh access token"})
		print(f"[DEBUG] going to send refreshed access token: ", access_token)
		response = JsonResponse({"message": "Token refreshed"})
		response.set_cookie(
			key="access_token",
			value=str(access_token),
			httponly=True,
			samesite="Lax",
			secure=False,
			max_age=300
		)
		return response

@ensure_csrf_cookie
def home(request):
	csrf_token = get_token(request)
	logging.info(f">>>>>>>>>>>>>>>>>>>>>>>CSRF Token: {csrf_token}")
	return render(request, 'base.html')

# @csrf_exempt
@api_view(["POST"])
def google_login(request):
	client_id = settings.GOOGLE_CLIENT_ID
	if not client_id:
		return JsonResponse({'error': 'no client id'}, status=status.HTTP_403_FORBIDDEN)
	try:
		body = json.loads(request.body)
		token = body.get("id_token")
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
	if not token:
		return Response({"error": "Missing id_token"}, status=400)
	
	try:
		request_adapter = google.auth.transport.requests.Request()
		idinfo = google_id_token.verify_oauth2_token(token, request_adapter, client_id)
		email = idinfo.get("email")
		if not email:
			print("no email", flush=True)
			return JsonResponse({"error":"no email in response token"}, status=status.HTTP_400_BAD_REQUEST)
		username = idinfo.get("name", email.split("@")[0])
		if not username:
			print("no username", flush=True)
			return JsonResponse({"error":"no name in response token"}, status=status.HTTP_400_BAD_REQUEST)
		print("response from google, email: ", email, " ,name: ", username, flush=True)
		
		user, created = CustomUser.objects.get_or_create(email=email, defaults={"username": username})
		if created:
			user.set_unusable_password()
			user.save()

		refresh = RefreshToken.for_user(user)
		access_token = refresh.access_token

		response = redirect("https://tranceanddance.com/")
		response.set_cookie(
			key="access_token",
			value=str(access_token),
			httponly=True,
			samesite='Lax',
			secure=False,  # [FLIP]set to True in production
			max_age=300
		)
		response.set_cookie(
			key="refresh_token",
			value=str(refresh),
			httponly=True,
			samesite='Lax',
			secure=False, # [FLIP]set to True in production
			max_age=86400
		)
		return response
	except ValueError as e:
		return Response({"error": "Invalid ID token", "details": str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
	user = request.user
	print("[DEBUG] me(user):", user, flush= True)
	# if (user.is_authenticated):
	return Response({
		"id": user.id,
		"username": user.username,
		"email": user.email,
		"two_factor_enabled": CustomTOTPDevice.objects.filter(customUser=user, confirmed=True).exists(),
	})
	# return Response({"error": "user not logged in"})

def login_42_redirect(request):
	base_url = "https://api.intra.42.fr/oauth/authorize"
	return redirect(
		f"{base_url}?client_id={settings.FT_CLIENT_ID}"
		f"&redirect_uri={settings.FT_REDIRECT_URI}"
		f"&response_type=code"
	)

@csrf_exempt
def login_42_callback(request):
	if request.method == "POST":
		body = json.loads(request.body)
		code = body.get("code")
	else:
		code = request.GET.get("code")
	
	if not code:
		return JsonResponse({"error": "No code provided"}, status=400)

	token_response = requests.post("https://api.intra.42.fr/oauth/token", data={
		"grant_type": "authorization_code",
		"client_id": settings.FT_CLIENT_ID,
		"client_secret": settings.FT_CLIENT_SECRET,
		"code": code,
		"redirect_uri": settings.FT_REDIRECT_URI,
	})

	# print("CLIENT_ID:", settings.FT_CLIENT_ID)
	# print("CLIENT_SECRET:", settings.FT_CLIENT_SECRET)
	# print("REDIRECT_URI:", settings.FT_REDIRECT_URI)
	# print("Token response status code:", token_response.status_code)
	# print("Token response content:", token_response.content)

	token_data = token_response.json() 
	access_token = token_data.get("access_token")
	print(f"42 receive access token: ", access_token)

	if not access_token:
		return JsonResponse({"error": "Failed to retrieve access token"}, status=400)

    # Use token to get user info
	user_response = requests.get("https://api.intra.42.fr/v2/me", headers={
		"Authorization": f"Bearer {access_token}"
	})

	profile = user_response.json()
	email = profile.get("email")
	username = profile.get("login")

	# Register or log in the user
	user, created = CustomUser.objects.get_or_create(email=email, defaults={"username": username})
	if created:
		user.set_unusable_password()
		user.save()

	refresh = RefreshToken.for_user(user)
	access = refresh.access_token

	response = JsonResponse({"message": "42 login successful"})
	response.set_cookie(
		key="access_token",
		value=str(access),
		httponly=True,
		samesite='Lax',
		secure=False,  # [FLIP]set to True in production
		max_age=300
	)
	response.set_cookie(
		key="refresh_token",
		value=str(refresh),
		httponly=True,
		samesite='Lax',
		secure=False, # [FLIP]set to True in production
		max_age=86400
	)
	return response

@csrf_exempt
def google_callback(request):
	code = request.GET.get('code')
	if not code:
		return JsonResponse({"error": "Missing authorization code"}, status=400)

	token_url = "https://oauth2.googleapis.com/token"
	redirect_uri = "https://tranceanddance.com/api/authentication/google/callback/"  # Must match your registered redirect URI
	client_id = settings.GOOGLE_CLIENT_ID
	client_secret = settings.GOOGLE_CLIENT_SECRET

	try:
		# Exchange authorization code for access and ID tokens
		token_response = requests.post(token_url, data={
			"code": code,
			"client_id": client_id,
			"client_secret": client_secret,
			"redirect_uri": redirect_uri,
			"grant_type": "authorization_code",
		})
		token_response.raise_for_status()
		token_data = token_response.json()
		id_token = token_data.get("id_token")
		access_token = token_data.get("access_token")

		if not id_token:
			return JsonResponse({"error": "Failed to retrieve ID token"}, status=400)

		request_adapter = google.auth.transport.requests.Request()
		idinfo = google_id_token.verify_oauth2_token(id_token, request_adapter, client_id)

		email = idinfo.get("email")
		username = idinfo.get("name", email.split("@")[0])

		if not email:
			return JsonResponse({"error": "No email found in ID token"}, status=400)

		# Register or log in the user
		user, created = CustomUser.objects.get_or_create(email=email, defaults={"username": username})
		if created:
			user.set_unusable_password()
			user.save()

		refresh = RefreshToken.for_user(user)
		access = refresh.access_token

		# print(f"[DEBUG] going to return access token: ", access_token)
		# response = JsonResponse({
		# 	'message': 'Login successful'
		# })
		response = redirect("https://tranceanddance.com//")
		response.set_cookie(
			key="access_token",
			value=str(access),
			httponly=True,
			samesite='Lax',
			secure=False,  # [FLIP]set to True in production
			max_age=300
		)
		response.set_cookie(
			key="refresh_token",
			value=str(refresh),
			httponly=True,
			samesite='Lax',
			secure=False, # [FLIP]set to True in production
			max_age=86400
		)
		return response

	except Exception as e:
		return JsonResponse({"error": "Failed to authenticate with Google", "details": str(e)}, status=500)

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def protected_user_data(request):
	logging.info(f"Protected user data endpoint hit by user: {request.user.username}")
	user = request.user
	if (user):
		return Response({
			"username": user.username,
			"email": user.email,
			"id": user.id,
			# "avatar": user.avatar,
			"is_active": user.is_active,
		})


# @api_view(['GET'])
# def me(request):
# 	user = request.user
# 	print("[DEBUG] me(user):", user, flush= True)
# 	if (user.is_authenticated):
# 		return Response({
# 			"username": user.username,
# 			"email": user.email,
# 			"id": user.id,
# 			# "avatar": user.avatar,
# 			"is_active": user.is_active,
# 		})
# 	return Response({"error": "User not Authenticated"})