from django.db import models
from django_otp.plugins.otp_totp.models import TOTPDevice
from data.models import CustomUser
from django.conf import settings
from django.contrib.auth.models import User

class CustomTOTPDevice(TOTPDevice):
    customUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="costum_totp_devices", blank=True, null=True)
    extra_field = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Ensure the 'user' field of TOTPDevice is set from 'customUser'
        before saving.
        """
        if self.customUser:
            self.user = self.customUser
        super().save(*args, **kwargs)

    def clean(self):
        """
        Ensure that 'user' is properly set if 'customUser' exists.
        """
        if self.customUser and not self.user:
            self.user = self.customUser
        super().clean()