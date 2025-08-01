from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField
from django.contrib.auth import get_user_model

from .models import (
    SoilType,
    CropType,
    Farm,
    Plot,
    FarmImage,
    FarmSensor,
    FarmIrrigation,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class SoilTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoilType
        fields = ['id', 'name', 'description', 'properties']


class CropTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropType
        fields = ['id', 'crop_type', 'plantation_type', 'planting_method']


class PlotSerializer(serializers.ModelSerializer):
    # Replace read-only method fields with writeable GeometryFields
    location = GeometryField(required=False, allow_null=True)
    boundary = GeometryField(required=False, allow_null=True)

    class Meta:
        model = Plot
        fields = [
            'id',
            'gat_number',
            'plot_number',
            'village',
            'taluka',
            'district',
            'state',
            'country',
            'pin_code',
            'location',
            'boundary',
        ]


class FarmImageSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = FarmImage
        fields = [
            'id',
            'farm',
            'title',
            'image',
            'capture_date',
            'notes',
            'uploaded_by',
            'uploaded_at',
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at']

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class FarmSensorSerializer(serializers.ModelSerializer):
    location = GeometryField(required=False, allow_null=True)

    class Meta:
        model = FarmSensor
        fields = [
            'id',
            'farm',
            'name',
            'sensor_type',
            'location',
            'installation_date',
            'last_maintenance',
            'status',
        ]


class FarmIrrigationSerializer(serializers.ModelSerializer):
    location = GeometryField()

    class Meta:
        model = FarmIrrigation
        fields = [
            'id',
            'farm',
            'irrigation_type',
            'irrigation_source',
            'location',
            'installation_date',
            'last_maintenance',
            'status',
        ]


class FarmSerializer(serializers.ModelSerializer):
    farm_owner = UserSerializer(read_only=True)
    farm_owner_id = serializers.PrimaryKeyRelatedField(
        source='farm_owner',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    created_by = UserSerializer(read_only=True)

    soil_type = SoilTypeSerializer(read_only=True)
    soil_type_id = serializers.PrimaryKeyRelatedField(
        source='soil_type',
        queryset=SoilType.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    crop_type = CropTypeSerializer(read_only=True)
    crop_type_id = serializers.PrimaryKeyRelatedField(
        source='crop_type',
        queryset=CropType.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    plot = PlotSerializer(read_only=True)
    plot_id = serializers.PrimaryKeyRelatedField(
        source='plot',
        queryset=Plot.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Farm
        fields = [
            'id',
            'farm_uid',
            'farm_owner',
            'farm_owner_id',
            'created_by',
            'plot',
            'plot_id',
            'address',
            'area_size',
            'soil_type',
            'soil_type_id',
            'crop_type',
            'crop_type_id',
            'farm_document',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['farm_uid', 'farm_owner', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user

        # If field officer, ensure farm_owner is passed
        if getattr(user, 'role', None) == 'fieldofficer':
            if 'farm_owner' not in validated_data:
                raise serializers.ValidationError({'farm_owner_id': 'This field is required.'})

        # Default to the request user if farm_owner is not specified
        validated_data.setdefault('farm_owner', user)
        # created_by will be set in the view perform_create
        return super().create(validated_data)


class FarmDetailSerializer(FarmSerializer):
    images      = FarmImageSerializer(many=True, read_only=True)
    sensors     = FarmSensorSerializer(many=True, read_only=True)
    irrigations = FarmIrrigationSerializer(many=True, read_only=True)

    class Meta(FarmSerializer.Meta):
        fields = FarmSerializer.Meta.fields + [
            'images',
            'sensors',
            'irrigations',
        ]


class PlotGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Plot
        geo_field = 'boundary'
        fields = [
            'id',
            'gat_number',
            'plot_number',
            'village',
            'taluka',
            'district',
            'state',
            'country',
            'pin_code',
            'boundary',
        ]


class FarmGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Farm
        geo_field = 'plot__boundary'
        fields = [
            'id',
            'farm_uid',
            'address',
            'area_size',
            'soil_type',
            'crop_type',
            'created_at',
            'updated_at',
        ]
