"""
Access views
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
import logging

from .models import NFCCard, PINCode, GuestAccess
from .serializers import (
    NFCCardSerializer,
    NFCCardCreateSerializer,
    PINCodeSerializer,
    PINCodeCreateSerializer,
    GuestAccessSerializer,
    GuestAccessCreateSerializer,
)
from apps.devices.models import Device
from apps.devices.permissions import IsDeviceOwnerOrShared

logger = logging.getLogger(__name__)


class NFCCardListCreateView(generics.ListCreateAPIView):
    """
    List and create NFC cards for a device
    """
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwnerOrShared]

    def get_queryset(self):
        device_id = self.kwargs.get('device_id')
        return NFCCard.objects.filter(device_id=device_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NFCCardCreateSerializer
        return NFCCardSerializer

    @extend_schema(
        tags=['Access'],
        responses={200: NFCCardSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = NFCCardSerializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

    @extend_schema(
        tags=['Access'],
        request=NFCCardCreateSerializer,
        responses={201: NFCCardSerializer}
    )
    def post(self, request, *args, **kwargs):
        device_id = self.kwargs.get('device_id')
        device = get_object_or_404(Device, pk=device_id)
        self.check_object_permissions(request, device)
        
        serializer = NFCCardCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        nfc_card = serializer.save(
            device=device,
            created_by=request.user
        )
        
        logger.info(f"NFC card created: {nfc_card.uid} for device {device.device_id}")
        
        return Response({
            'success': True,
            'message': 'NFC card created successfully',
            'data': NFCCardSerializer(nfc_card).data
        }, status=status.HTTP_201_CREATED)


class NFCCardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete NFC card
    """
    queryset = NFCCard.objects.all()
    serializer_class = NFCCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Access'])
    def get(self, request, *args, **kwargs):
        nfc_card = self.get_object()
        return Response({
            'success': True,
            'data': NFCCardSerializer(nfc_card).data
        })

    @extend_schema(tags=['Access'])
    def delete(self, request, *args, **kwargs):
        nfc_card = self.get_object()
        nfc_card.delete()
        
        logger.info(f"NFC card deleted: {nfc_card.uid}")
        
        return Response({
            'success': True,
            'message': 'NFC card deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class PINCodeListCreateView(generics.ListCreateAPIView):
    """
    List and create PIN codes for a device
    """
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwnerOrShared]

    def get_queryset(self):
        device_id = self.kwargs.get('device_id')
        return PINCode.objects.filter(device_id=device_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PINCodeCreateSerializer
        return PINCodeSerializer

    @extend_schema(
        tags=['Access'],
        responses={200: PINCodeSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = PINCodeSerializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

    @extend_schema(
        tags=['Access'],
        request=PINCodeCreateSerializer,
        responses={201: PINCodeSerializer}
    )
    def post(self, request, *args, **kwargs):
        device_id = self.kwargs.get('device_id')
        device = get_object_or_404(Device, pk=device_id)
        self.check_object_permissions(request, device)
        
        serializer = PINCodeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        pin_code_obj = PINCode.objects.create(
            device=device,
            name=serializer.validated_data['name'],
            user=serializer.validated_data.get('user'),
            valid_from=serializer.validated_data.get('valid_from'),
            valid_until=serializer.validated_data.get('valid_until'),
            max_usage=serializer.validated_data.get('max_usage'),
            allowed_days=serializer.validated_data.get('allowed_days', []),
            allowed_hours=serializer.validated_data.get('allowed_hours', {}),
            created_by=request.user
        )
        
        # Set PIN (hashed)
        pin_code_obj.set_pin(serializer.validated_data['pin_code'])
        pin_code_obj.save()
        
        logger.info(f"PIN code created for device {device.device_id}")
        
        return Response({
            'success': True,
            'message': 'PIN code created successfully',
            'data': PINCodeSerializer(pin_code_obj).data
        }, status=status.HTTP_201_CREATED)


class PINCodeDetailView(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete PIN code
    """
    queryset = PINCode.objects.all()
    serializer_class = PINCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Access'])
    def delete(self, request, *args, **kwargs):
        pin_code = self.get_object()
        pin_code.delete()
        
        logger.info(f"PIN code deleted")
        
        return Response({
            'success': True,
            'message': 'PIN code deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class GuestAccessListCreateView(generics.ListCreateAPIView):
    """
    List and create guest access
    """
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwnerOrShared]

    def get_queryset(self):
        device_id = self.kwargs.get('device_id')
        return GuestAccess.objects.filter(device_id=device_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GuestAccessCreateSerializer
        return GuestAccessSerializer

    @extend_schema(
        tags=['Access'],
        responses={200: GuestAccessSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = GuestAccessSerializer(queryset, many=True)
        return Response({
            'success': True,
            'count': queryset.count(),
            'data': serializer.data
        })

    @extend_schema(
        tags=['Access'],
        request=GuestAccessCreateSerializer,
        responses={201: GuestAccessSerializer}
    )
    def post(self, request, *args, **kwargs):
        device_id = self.kwargs.get('device_id')
        device = get_object_or_404(Device, pk=device_id)
        self.check_object_permissions(request, device)
        
        serializer = GuestAccessCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        access_type = data['access_type']
        
        # Create NFC or PIN
        if access_type == 'NFC':
            nfc_card = NFCCard.objects.create(
                device=device,
                uid=data['nfc_uid'],
                name=f"Guest: {data['guest_name']}",
                valid_from=data['valid_from'],
                valid_until=data['valid_until'],
                created_by=request.user
            )
            
            guest_access = GuestAccess.objects.create(
                device=device,
                created_by=request.user,
                guest_name=data['guest_name'],
                guest_email=data.get('guest_email', ''),
                guest_phone=data.get('guest_phone', ''),
                access_type='NFC',
                nfc_card=nfc_card,
                valid_from=data['valid_from'],
                valid_until=data['valid_until']
            )
        else:  # PIN
            pin_code_obj = PINCode.objects.create(
                device=device,
                name=f"Guest: {data['guest_name']}",
                valid_from=data['valid_from'],
                valid_until=data['valid_until'],
                created_by=request.user
            )
            pin_code_obj.set_pin(data['pin_code'])
            pin_code_obj.save()
            
            guest_access = GuestAccess.objects.create(
                device=device,
                created_by=request.user,
                guest_name=data['guest_name'],
                guest_email=data.get('guest_email', ''),
                guest_phone=data.get('guest_phone', ''),
                access_type='PIN',
                pin_code=pin_code_obj,
                valid_from=data['valid_from'],
                valid_until=data['valid_until']
            )
        
        logger.info(f"Guest access created: {data['guest_name']} ({access_type})")
        
        return Response({
            'success': True,
            'message': 'Guest access created successfully',
            'data': GuestAccessSerializer(guest_access).data
        }, status=status.HTTP_201_CREATED)