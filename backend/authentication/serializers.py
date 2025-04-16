from data.models import CustomUser
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from authentication.models import CustomTOTPDevice

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    two_factor_enabled = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'username', 'email', 'password', 'two_factor_enabled']

    def create(self, validated_data):
        two_factor_enabled = validated_data.pop('two_factor_enabled', False)

        username = validated_data.get('username') or self.generate_username(validated_data.get('email'))

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            name=validated_data['name'],
            email=validated_data['email'],
        )
        password = validated_data.get('password')
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        if two_factor_enabled:
            CustomTOTPDevice.objects.create(user=user, confirmed=True)
            user.two_factor_enabled = True
            user.save(update_fields=["two_factor_enabled"])
            
        return user
    
    def generate_username(self, email):
        base = email.split('@')[0]
        username = base
        suffix = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base}_{suffix}"
            suffix += 1
        return username
