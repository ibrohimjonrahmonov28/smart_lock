"""
Device views
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
import logging

from .models import Device, DeviceLog, DeviceSharing
from .serializers import (
    DeviceSerializer,
    DeviceCreateSerializer,
    DeviceUpdateSerializer,
    DeviceUnlockSerializer,
    DeviceLogSerializer,
    DeviceSharingSerializer,
    DeviceSharingCreateSerializer,
)
from .permissions import IsDeviceOwner, IsDeviceOwnerOrShared, CanUnlockDevice
from .tasks import send_unlock_command, send_lock_command, log_device_event
from apps.core.throttling import UnlockRateThrottle

logger = logging.getLogger(__name__)


class DeviceListCreateView(generics.ListCreateAPIView):
    """
    List all devices and create new device
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return devices owned by user and devices shared with user
        """
        user = self.request.user
        owned = Device.objects.filter(owner=user)
        shared = Device.objects.filter(
            shared_with__shared_with=user,
            shared_with__is_active=True
        )
        return (owned | shared).distinct()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeviceCreateSerializer
        return DeviceSerializer

    @extend_schema(
        tags=['Devices'],
        responses={200: DeviceSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = DeviceSerializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

    @extend_schema(
        tags=['Devices'],
        request=DeviceCreateSerializer,
        responses={
            201: DeviceSerializer,
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = DeviceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device = serializer.save(owner=request.user)
        
        logger.info(f"New device created: {device.device_id} by {request.user.email}")
        
        return Response({
            'success': True,
            'message': 'Device created successfully',
            'data': DeviceSerializer(device).data
        }, status=status.HTTP_201_CREATED)


class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a device
    """
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwnerOrShared]
    
    def get_queryset(self):
        return Device.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DeviceUpdateSerializer
        return DeviceSerializer

    @extend_schema(
        tags=['Devices'],
        responses={200: DeviceSerializer}
    )
    def get(self, request, *args, **kwargs):
        device = self.get_object()
        return Response({
            'success': True,
            'data': DeviceSerializer(device).data
        })

    @extend_schema(
        tags=['Devices'],
        request=DeviceUpdateSerializer,
        responses={200: DeviceSerializer}
    )
    def patch(self, request, *args, **kwargs):
        device = self.get_object()
        serializer = DeviceUpdateSerializer(device, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        logger.info(f"Device updated: {device.device_id}")
        
        return Response({
            'success': True,
            'message': 'Device updated successfully',
            'data': DeviceSerializer(device).data
        })

    @extend_schema(
        tags=['Devices'],
        responses={204: OpenApiResponse(description='Device deleted')}
    )
    def delete(self, request, *args, **kwargs):
        device = self.get_object()
        
        # Only owner can delete
        if device.owner != request.user:
            return Response({
                'success': False,
                'message': 'Only owner can delete device'
            }, status=status.HTTP_403_FORBIDDEN)
        
        device_id = device.device_id
        device.delete()
        
        logger.warning(f"Device deleted: {device_id} by {request.user.email}")
        
        return Response({
            'success': True,
            'message': 'Device deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class DeviceUnlockView(APIView):
    """
    Unlock device remotely
    """
    permission_classes = [permissions.IsAuthenticated, CanUnlockDevice]
    throttle_classes = [UnlockRateThrottle]

    @extend_schema(
        tags=['Devices'],
        request=DeviceUnlockSerializer,
        responses={
            200: OpenApiResponse(description='Unlock command sent'),
            400: OpenApiResponse(description='Device offline or error'),
        }
    )
    def post(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        self.check_object_permissions(request, device)
        
        serializer = DeviceUnlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        duration = serializer.validated_data.get('duration', 5)
        
        # Check if device is online
        if not device.is_online:
            return Response({
                'success': False,
                'message': 'Device is offline'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send unlock command via MQTT (async)
        send_unlock_command.delay(
            device_id=str(device.id),
            user_id=str(request.user.id),
            duration=duration,
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        logger.info(f"Unlock command sent: {device.device_id} by {request.user.email}")
        
        return Response({
            'success': True,
            'message': 'Unlock command sent successfully',
            'data': {
                'device_id': device.device_id,
                'duration': duration,
            }
        }, status=status.HTTP_200_OK)


class DeviceLockView(APIView):
    """
    Lock device remotely
    """
    permission_classes = [permissions.IsAuthenticated, CanUnlockDevice]
    throttle_classes = [UnlockRateThrottle]

    @extend_schema(
        tags=['Devices'],
        responses={200: OpenApiResponse(description='Lock command sent')}
    )
    def post(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        self.check_object_permissions(request, device)
        
        if not device.is_online:
            return Response({
                'success': False,
                'message': 'Device is offline'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send lock command via MQTT (async)
        send_lock_command.delay(
            device_id=str(device.id),
            user_id=str(request.user.id),
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        
        logger.info(f"Lock command sent: {device.device_id} by {request.user.email}")
        
        return Response({
            'success': True,
            'message': 'Lock command sent successfully'
        }, status=status.HTTP_200_OK)


class DeviceStatusView(APIView):
    """
    Get device current status
    """
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwnerOrShared]

    @extend_schema(
        tags=['Devices'],
        responses={200: DeviceSerializer}
    )
    def get(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        self.check_object_permissions(request, device)
        
        return Response({
            'success': True,
            'data': {
                'device_id': device.device_id,
                'name': device.name,
                'is_locked': device.is_locked,
                'is_online': device.is_online,
                'battery_level': device.battery_level,
                'is_battery_low': device.is_battery_low,
                'last_seen': device.last_seen,
                'last_unlock': device.last_unlock,
            }
        })


class DeviceLogsView(generics.ListAPIView):
    """
    Get device activity logs
    """
    serializer_class = DeviceLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwnerOrShared]

    def get_queryset(self):
        device_id = self.kwargs.get('pk')
        return DeviceLog.objects.filter(device_id=device_id)

    @extend_schema(
        tags=['Devices'],
        responses={200: DeviceLogSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })


class DeviceSharingListView(generics.ListCreateAPIView):
    """
    List device sharings and create new sharing
    """
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwner]

    def get_queryset(self):
        device_id = self.kwargs.get('pk')
        return DeviceSharing.objects.filter(device_id=device_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeviceSharingCreateSerializer
        return DeviceSharingSerializer

    @extend_schema(
        tags=['Devices'],
        responses={200: DeviceSharingSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = DeviceSharingSerializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

    @extend_schema(
        tags=['Devices'],
        request=DeviceSharingCreateSerializer,
        responses={201: DeviceSharingSerializer}
    )
    def post(self, request, *args, **kwargs):
        device_id = self.kwargs.get('pk')
        device = get_object_or_404(Device, pk=device_id)
        
        # Check ownership
        if device.owner != request.user:
            return Response({
                'success': False,
                'message': 'Only owner can share device'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = DeviceSharingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        shared_with = User.objects.get(email=serializer.validated_data['email'])
        
        # Check if already shared
        if DeviceSharing.objects.filter(device=device, shared_with=shared_with).exists():
            return Response({
                'success': False,
                'message': 'Device already shared with this user'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sharing = DeviceSharing.objects.create(
            device=device,
            shared_with=shared_with,
            shared_by=request.user,
            role=serializer.validated_data['role'],
            expires_at=serializer.validated_data.get('expires_at'),
        )
        
        logger.info(f"Device shared: {device.device_id} with {shared_with.email}")
        
        return Response({
            'success': True,
            'message': 'Device shared successfully',
            'data': DeviceSharingSerializer(sharing).data
        }, status=status.HTTP_201_CREATED)


class DeviceSharingDetailView(generics.DestroyAPIView):
    """
    Remove device sharing
    """
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwner]
    queryset = DeviceSharing.objects.all()

    @extend_schema(
        tags=['Devices'],
        responses={204: OpenApiResponse(description='Sharing removed')}
    )
    def delete(self, request, *args, **kwargs):
        sharing = self.get_object()
        
        # Check if user is owner
        if sharing.device.owner != request.user:
            return Response({
                'success': False,
                'message': 'Only owner can remove sharing'
            }, status=status.HTTP_403_FORBIDDEN)
        
        sharing.delete()
        
        logger.info(f"Device sharing removed: {sharing.device.device_id}")
        
        return Response({
            'success': True,
            'message': 'Sharing removed successfully'
        }, status=status.HTTP_204_NO_CONTENT)