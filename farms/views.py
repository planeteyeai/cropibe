from django.contrib.gis.geos import Point
from django.db.models import Q
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import (
    SoilType,
    CropType,
    Farm,
    Plot,
    FarmImage,
    FarmSensor,
    FarmIrrigation,
)
from .serializers import (
    SoilTypeSerializer,
    CropTypeSerializer,
    FarmSerializer,
    FarmDetailSerializer,
    FarmGeoSerializer,
    PlotSerializer,
    PlotGeoSerializer,
    FarmImageSerializer,
    FarmSensorSerializer,
    FarmIrrigationSerializer,
)


class IsOwnerOrAdminOrManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Farm object
        if isinstance(obj, Farm):
            return (
                obj.farm_owner == user
                or user.is_superuser
                or getattr(user, 'role', None) in ['admin', 'manager']
                or (getattr(user, 'role', None) == 'fieldofficer' and obj.created_by == user)
            )

        # Anything linked to Farm
        if hasattr(obj, 'farm'):
            farm = obj.farm
            return (
                farm.farm_owner == user
                or user.is_superuser
                or getattr(user, 'role', None) in ['admin', 'manager']
                or (getattr(user, 'role', None) == 'fieldofficer' and farm.created_by == user)
            )

        return False


class SoilTypeViewSet(viewsets.ModelViewSet):
    queryset = SoilType.objects.all()
    serializer_class = SoilTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class CropTypeViewSet(viewsets.ModelViewSet):
    queryset = CropType.objects.all()
    serializer_class = CropTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['soil_type', 'crop_type', 'farm_owner']
    search_fields = ['address', 'farm_owner__username']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FarmDetailSerializer
        if self.action == 'geojson':
            return FarmGeoSerializer
        return FarmSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdminOrManager()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # filter by owner id
        if owner_id := self.request.query_params.get('owner'):
            if owner_id.isdigit():
                qs = qs.filter(farm_owner_id=owner_id)

        # only my farms
        if self.request.query_params.get('my_farms') == 'true':
            qs = qs.filter(farm_owner=user)

        # geographic search
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius')
        if lat and lng and radius:
            try:
                lat, lng, km = float(lat), float(lng), float(radius)
                user_loc = Point(lng, lat, srid=4326)
                qs = (
                    qs.filter(plot__location__distance_lte=(user_loc, D(km=km)))
                      .annotate(distance=Distance('plot__location', user_loc))
                      .order_by('distance')
                )
            except ValueError:
                pass

        # text search
        if search := self.request.query_params.get('search'):
            qs = qs.filter(
                Q(address__icontains=search)
                | Q(farm_owner__username__icontains=search)
            )

        # field officer sees farms they created
        if getattr(user, 'role', None) == 'fieldofficer':
            qs = qs.filter(created_by=user)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        data = self.request.data
        # field officer must assign farm_owner
        if getattr(user, 'role', None) == 'fieldofficer' and not data.get('farm_owner'):
            raise ValidationError("Field Officer must assign a farm_owner.")
        serializer.save(created_by=user)

    def perform_update(self, serializer):
        user = self.request.user
        if getattr(user, 'role', None) == 'fieldofficer' and not self.request.data.get('farm_owner'):
            raise ValidationError("Field Officer must specify farm_owner.")
        serializer.save()

    @action(detail=False, methods=['get'])
    def geojson(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)


class PlotViewSet(viewsets.ModelViewSet):
    queryset = Plot.objects.all()
    serializer_class = PlotSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrManager]
    filterset_fields = ['gat_number', 'plot_number', 'village', 'taluka', 'state']
    search_fields = ['gat_number', 'plot_number', 'village', 'district']

    def get_serializer_class(self):
        if self.action == 'geojson':
            return PlotGeoSerializer
        return PlotSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if self.request.query_params.get('my_farms') == 'true':
            qs = qs.filter(farms__farm_owner=user)

        if farm_id := self.request.query_params.get('farm'):
            if farm_id.isdigit():
                qs = qs.filter(farms__id=farm_id)

        if self.request.query_params.get('has_boundary') == 'true':
            qs = qs.filter(boundary__isnull=False)

        if getattr(user, 'role', None) == 'fieldofficer':
            qs = qs.filter(farms__created_by=user)

        return qs

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def geojson(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)


class FarmImageViewSet(viewsets.ModelViewSet):
    queryset = FarmImage.objects.all()
    serializer_class = FarmImageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrManager]
    filterset_fields = ['farm']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if farm_id := self.request.query_params.get('farm'):
            if farm_id.isdigit():
                qs = qs.filter(farm_id=farm_id)

        if self.request.query_params.get('my_farms') == 'true':
            qs = qs.filter(farm__farm_owner=user)

        if sd := self.request.query_params.get('start_date'):
            qs = qs.filter(uploaded_at__date__gte=sd)
        if ed := self.request.query_params.get('end_date'):
            qs = qs.filter(uploaded_at__date__lte=ed)

        if getattr(user, 'role', None) == 'fieldofficer':
            qs = qs.filter(farm__created_by=user)

        return qs


class FarmSensorViewSet(viewsets.ModelViewSet):
    queryset = FarmSensor.objects.all()
    serializer_class = FarmSensorSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrManager]
    filterset_fields = ['farm', 'sensor_type', 'status']
    search_fields = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if farm_id := self.request.query_params.get('farm'):
            if farm_id.isdigit():
                qs = qs.filter(farm_id=farm_id)

        if self.request.query_params.get('my_farms') == 'true':
            qs = qs.filter(farm__farm_owner=user)

        if t := self.request.query_params.get('type'):
            qs = qs.filter(sensor_type__name=t)

        if st := self.request.query_params.get('status'):
            qs = qs.filter(status=(st.lower() == 'true'))

        if getattr(user, 'role', None) == 'fieldofficer':
            qs = qs.filter(farm__created_by=user)

        return qs


class FarmIrrigationViewSet(viewsets.ModelViewSet):
    queryset = FarmIrrigation.objects.all()
    serializer_class = FarmIrrigationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrManager]
    filterset_fields = ['farm', 'irrigation_type', 'status']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if farm_id := self.request.query_params.get('farm'):
            if farm_id.isdigit():
                qs = qs.filter(farm_id=farm_id)

        if self.request.query_params.get('my_farms') == 'true':
            qs = qs.filter(farm__farm_owner=user)

        if t := self.request.query_params.get('type'):
            qs = qs.filter(irrigation_type__name=t)

        if st := self.request.query_params.get('status'):
            qs = qs.filter(status=(st.lower() == 'true'))

        if getattr(user, 'role', None) == 'fieldofficer':
            qs = qs.filter(farm__created_by=user)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user)

    def perform_update(self, serializer):
        serializer.save()
