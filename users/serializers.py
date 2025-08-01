from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Role

User = get_user_model()

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name']

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'address',
            'village', 'state', 'district', 'taluka', 'profile_picture',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name','role_id',
            'phone_number', 'address', 'village', 'state', 'district', 'taluka',
        ]

    def create(self, validated_data):
        role = validated_data.pop('role', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        if role:
            user.role = role
        user.set_password(password)
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        required=False
    )

    class Meta:
        model = User
        fields = [
            'email','first_name', 'last_name', 'role_id', 'phone_number', 'address',
            'village', 'state', 'district', 'taluka', 'profile_picture',
        ]
        read_only_fields = ['email']

class ChangePasswordSerializer(serializers.Serializer):
    old_password     = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords must match.")
        return data
