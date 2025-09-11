from rest_framework import serializers
from project.models import Collect, Payment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'collect',
            'amount',
            'timestamp'
        ]

class CollectSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    participants = serializers.IntegerField(read_only=True)
    limit_status = serializers.SerializerMethodField()
    
    def get_limit_status(self, obj):
        if obj.target_amount is None:
            return 'Unlimited'
        return f'Target: {obj.target_amount}'

    class Meta:
        model = Collect
        fields = [
            'id', 'author', 'title', 'purpose',
            'description', 'target_amount', 'current_amount',
            'participants', 'created_at', 'ended_at', 'image',
            'limit_status', 'payments'
        ]

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password_confirm'
        ]

    def validate(self, data):
        if data['password']!=data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user