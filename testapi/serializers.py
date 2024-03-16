from django.contrib.auth import get_user_model
from rest_framework import serializers
from testapi.models import ReferralCode

USER_MODEL = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = USER_MODEL
        fields = ('username', 'password', 'email')


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ['user', 'code', 'expiry_date', 'is_active']
