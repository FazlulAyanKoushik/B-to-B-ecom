from rest_framework import serializers


class GlobalLoginOTPSerializer(serializers.Serializer):
    otp = serializers.IntegerField(write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
