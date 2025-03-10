from django.db import models
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.models import User

class UserTOTPDevice(TOTPDevice): 
    extra_field = models.CharField(max_length=100, blank=True, null=True)