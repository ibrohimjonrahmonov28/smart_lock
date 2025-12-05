"""
Access views
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
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
from apps.core.utils.encryption import verify_pin_code, verify_device_hmac

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

        # YANGI: Generated PIN ni saqlash
        generated_pin = None

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
            # YANGI: PIN ni saqlash (avtomatik yoki manual)
            generated_pin = data['pin_code']

            pin_code_obj = PINCode.objects.create(
                device=device,
                name=f"Guest: {data['guest_name']}",
                valid_from=data['valid_from'],
                valid_until=data['valid_until'],
                created_by=request.user
            )
            pin_code_obj.set_pin(generated_pin)
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

        # YANGI: Response da PIN ni qaytarish (faqat avtomatik yaratilganda)
        response_data = GuestAccessSerializer(guest_access).data

        # Agar PIN avtomatik yaratilgan bo'lsa, response ga qo'shamiz
        if generated_pin and data.get('_pin_auto_generated'):
            response_data['generated_pin'] = generated_pin
            response_data['message'] = f"PIN kod yaratildi: {generated_pin}"

        return Response({
            'success': True,
            'message': 'Guest access created successfully',
            'data': response_data
        }, status=status.HTTP_201_CREATED)


class VerifyPINView(APIView):
    """
    Verify PIN code for device access
    Public endpoint - no authentication required
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Access'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'device_id': {'type': 'string', 'format': 'uuid'},
                    'pin_code': {'type': 'string', 'minLength': 4, 'maxLength': 8},
                    'timestamp': {'type': 'integer', 'description': 'Unix timestamp'},
                    'signature': {'type': 'string', 'description': 'HMAC-SHA256 signature (device_id:timestamp:pin_code)'}
                },
                'required': ['device_id', 'pin_code', 'timestamp', 'signature']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'access_granted': {'type': 'boolean'},
                    'pin_info': {'type': 'object'},
                    'command': {'type': 'string', 'enum': ['UNLOCK', 'DENY']}
                }
            }
        }
    )
    def post(self, request):
        """
        Verify PIN code and check validity

        Security: Requires HMAC signature to prevent WiFi hijacking
        Signature = HMAC-SHA256(device_secret, "device_id:timestamp:pin_code")
        """
        device_id = request.data.get('device_id')
        pin_code = request.data.get('pin_code')
        timestamp = request.data.get('timestamp')
        signature = request.data.get('signature')

        # Validate input
        if not device_id or not pin_code:
            return Response({
                'success': False,
                'message': 'Device ID and PIN code are required',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not timestamp or not signature:
            return Response({
                'success': False,
                'message': 'Timestamp and signature are required for secure communication',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get device
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Device not found',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verify HMAC signature to prevent WiFi hijacking
        if not verify_device_hmac(device_id, timestamp, pin_code, signature, device.device_secret):
            logger.warning(f"Invalid HMAC signature for device {device.device_id}")
            return Response({
                'success': False,
                'message': 'Invalid signature - authentication failed',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check timestamp to prevent replay attacks (within 5 minutes)
        import time
        current_time = int(time.time())
        request_time = int(timestamp)
        time_diff = abs(current_time - request_time)

        if time_diff > 300:  # 5 minutes
            logger.warning(f"Timestamp too old for device {device.device_id}: {time_diff}s")
            return Response({
                'success': False,
                'message': 'Request expired - timestamp too old',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Find all active PIN codes for this device
        active_pins = PINCode.objects.filter(
            device=device,
            is_active=True
        )

        # Check each PIN
        now = timezone.now()
        for pin_obj in active_pins:
            # Verify PIN hash
            if verify_pin_code(pin_code, pin_obj.pin_hash):
                # PIN matches! Now check validity
                is_valid = pin_obj.is_valid

                if is_valid:
                    # Increment usage count
                    pin_obj.increment_usage()

                    # Update device last_unlock
                    device.last_unlock = now
                    device.save(update_fields=['last_unlock'])

                    # Log successful access
                    from apps.devices.models import DeviceLog
                    DeviceLog.objects.create(
                        device=device,
                        user=pin_obj.user,
                        event_type='UNLOCK_PIN',
                        description=f'Unlocked with PIN: {pin_obj.name}',
                        success=True
                    )

                    logger.info(f"PIN verified successfully for device {device.device_id}")

                    return Response({
                        'success': True,
                        'message': 'PIN verified successfully',
                        'access_granted': True,
                        'command': 'UNLOCK',
                        'pin_info': {
                            'name': pin_obj.name,
                            'valid_until': pin_obj.valid_until,
                            'usage_count': pin_obj.usage_count,
                            'max_usage': pin_obj.max_usage
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    # PIN correct but expired/invalid
                    reason = 'expired'
                    if pin_obj.max_usage and pin_obj.usage_count >= pin_obj.max_usage:
                        reason = 'max usage reached'
                    elif now < pin_obj.valid_from:
                        reason = 'not yet valid'
                    elif pin_obj.valid_until and now > pin_obj.valid_until:
                        reason = 'expired'

                    # Log failed attempt
                    from apps.devices.models import DeviceLog
                    DeviceLog.objects.create(
                        device=device,
                        event_type='UNLOCK_PIN',
                        description=f'PIN valid but {reason}: {pin_obj.name}',
                        success=False,
                        error_message=reason
                    )

                    logger.warning(f"PIN correct but invalid for device {device.device_id}: {reason}")

                    return Response({
                        'success': False,
                        'message': f'PIN is {reason}',
                        'access_granted': False,
                        'command': 'DENY'
                    }, status=status.HTTP_403_FORBIDDEN)

        # No matching PIN found
        # Log failed attempt
        from apps.devices.models import DeviceLog
        DeviceLog.objects.create(
            device=device,
            event_type='UNLOCK_PIN',
            description=f'Invalid PIN attempt',
            success=False,
            error_message='Invalid PIN code'
        )

        logger.warning(f"Invalid PIN attempt for device {device.device_id}")

        return Response({
            'success': False,
            'message': 'Invalid PIN code',
            'access_granted': False,
            'command': 'DENY'
        }, status=status.HTTP_401_UNAUTHORIZED)


class VerifyNFCView(APIView):
    """
    Verify NFC card for device access
    Public endpoint - no authentication required
    Used by IoT device when user taps NFC card
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Access'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'device_id': {'type': 'string', 'description': 'Device UUID'},
                    'nfc_uid': {'type': 'string', 'description': 'NFC UID (e.g., 04:A3:2F:B2:1E:8C:90)'},
                    'battery_level': {'type': 'integer', 'description': 'Current battery level (0-100)'},
                    'timestamp': {'type': 'integer', 'description': 'Unix timestamp'},
                    'signature': {'type': 'string', 'description': 'HMAC-SHA256 signature (device_id:timestamp:nfc_uid)'}
                },
                'required': ['device_id', 'nfc_uid', 'timestamp', 'signature']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'access_granted': {'type': 'boolean'},
                    'nfc_info': {'type': 'object'},
                    'command': {'type': 'string', 'enum': ['UNLOCK', 'DENY']}
                }
            }
        }
    )
    def post(self, request):
        """
        Verify NFC card and return unlock command to device

        Security: Requires HMAC signature to prevent WiFi hijacking
        Signature = HMAC-SHA256(device_secret, "device_id:timestamp:nfc_uid")
        """
        device_id = request.data.get('device_id')
        nfc_uid = request.data.get('nfc_uid')
        battery_level = request.data.get('battery_level')
        timestamp = request.data.get('timestamp')
        signature = request.data.get('signature')

        # Validate input
        if not device_id or not nfc_uid:
            return Response({
                'success': False,
                'message': 'Device ID and NFC UID are required',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not timestamp or not signature:
            return Response({
                'success': False,
                'message': 'Timestamp and signature are required for secure communication',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get device
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Device not found',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_404_NOT_FOUND)

        # Verify HMAC signature to prevent WiFi hijacking
        if not verify_device_hmac(device_id, timestamp, nfc_uid, signature, device.device_secret):
            logger.warning(f"Invalid HMAC signature for device {device.device_id}")
            return Response({
                'success': False,
                'message': 'Invalid signature - authentication failed',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check timestamp to prevent replay attacks (within 5 minutes)
        import time
        current_time = int(time.time())
        request_time = int(timestamp)
        time_diff = abs(current_time - request_time)

        if time_diff > 300:  # 5 minutes
            logger.warning(f"Timestamp too old for device {device.device_id}: {time_diff}s")
            return Response({
                'success': False,
                'message': 'Request expired - timestamp too old',
                'access_granted': False,
                'command': 'DENY'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Update device status
        device.is_online = True
        device.last_seen = timezone.now()
        if battery_level is not None:
            device.battery_level = battery_level
        device.save(update_fields=['is_online', 'last_seen', 'battery_level'])

        # Normalize NFC UID (uppercase, remove spaces)
        nfc_uid = nfc_uid.upper().replace(' ', '')

        # Find all active NFC cards for this device
        active_cards = NFCCard.objects.filter(
            device=device,
            is_active=True
        )

        # Check each NFC card
        now = timezone.now()
        for nfc_obj in active_cards:
            # Normalize stored UID
            stored_uid = nfc_obj.uid.upper().replace(' ', '')

            if nfc_uid == stored_uid:
                # NFC matches! Now check validity
                is_valid = nfc_obj.is_valid

                if is_valid:
                    # Increment usage count
                    nfc_obj.increment_usage()

                    # Update device last_unlock
                    device.last_unlock = now
                    device.save(update_fields=['last_unlock'])

                    # Log successful access
                    from apps.devices.models import DeviceLog
                    DeviceLog.objects.create(
                        device=device,
                        user=nfc_obj.user,
                        event_type='UNLOCK_NFC',
                        description=f'Unlocked with NFC card: {nfc_obj.name}',
                        success=True
                    )

                    logger.info(f"NFC verified successfully for device {device.device_id}")

                    return Response({
                        'success': True,
                        'message': 'NFC verified successfully',
                        'access_granted': True,
                        'command': 'UNLOCK',
                        'nfc_info': {
                            'name': nfc_obj.name,
                            'valid_until': nfc_obj.valid_until,
                            'usage_count': nfc_obj.usage_count,
                            'max_usage': nfc_obj.max_usage
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    # NFC correct but expired/invalid
                    reason = 'expired'
                    if nfc_obj.max_usage and nfc_obj.usage_count >= nfc_obj.max_usage:
                        reason = 'max usage reached'
                    elif now < nfc_obj.valid_from:
                        reason = 'not yet valid'
                    elif nfc_obj.valid_until and now > nfc_obj.valid_until:
                        reason = 'expired'

                    # Log failed attempt
                    from apps.devices.models import DeviceLog
                    DeviceLog.objects.create(
                        device=device,
                        event_type='UNLOCK_NFC',
                        description=f'NFC valid but {reason}: {nfc_obj.name}',
                        success=False,
                        error_message=reason
                    )

                    logger.warning(f"NFC correct but invalid for device {device.device_id}: {reason}")

                    return Response({
                        'success': False,
                        'message': f'NFC is {reason}',
                        'access_granted': False,
                        'command': 'DENY'
                    }, status=status.HTTP_403_FORBIDDEN)

        # No matching NFC found
        # Log failed attempt
        from apps.devices.models import DeviceLog
        DeviceLog.objects.create(
            device=device,
            event_type='UNLOCK_NFC',
            description=f'Invalid NFC UID: {nfc_uid}',
            success=False,
            error_message='Invalid NFC UID'
        )

        logger.warning(f"Invalid NFC attempt for device {device.device_id}")

        return Response({
            'success': False,
            'message': 'Invalid NFC card',
            'access_granted': False,
            'command': 'DENY'
        }, status=status.HTTP_401_UNAUTHORIZED)