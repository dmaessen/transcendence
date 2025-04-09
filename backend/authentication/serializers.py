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

        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            name=validated_data['name'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

        if two_factor_enabled:
            CustomTOTPDevice.objects.create(user=user, confirmed=True)
            user.two_factor_enabled = True
            user.save(update_fields=["two_factor_enabled"])
        return user
