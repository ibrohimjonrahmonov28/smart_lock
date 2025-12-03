"""
Security views
"""

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import SecurityEvent, AuditLog
from .serializers import SecurityEventSerializer, AuditLogSerializer


class SecurityEventListView(generics.ListAPIView):
    """
    List security events
    """
    serializer_class = SecurityEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SecurityEvent.objects.all()
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by event_type
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by date range
        days = self.request.query_params.get('days', 7)
        try:
            days = int(days)
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=start_date)
        except ValueError:
            pass
        
        return queryset

    @extend_schema(tags=['Security'])
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


class AuditLogListView(generics.ListAPIView):
    """
    List audit logs (Admin only)
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return AuditLog.objects.all()[:1000]  # Limit to last 1000

    @extend_schema(tags=['Security'])
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


class SecurityDashboardView(APIView):
    """
    Security dashboard statistics
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(tags=['Security'])
    def get(self, request):
        # Last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        
        # Critical events
        critical_events = SecurityEvent.objects.filter(
            severity='CRITICAL',
            created_at__gte=week_ago
        ).count()
        
        # High severity events
        high_events = SecurityEvent.objects.filter(
            severity='HIGH',
            created_at__gte=week_ago
        ).count()
        
        # Failed login attempts
        failed_logins = SecurityEvent.objects.filter(
            event_type='LOGIN_FAILED',
            created_at__gte=week_ago
        ).count()
        
        # Tamper attempts
        tamper_attempts = SecurityEvent.objects.filter(
            event_type='TAMPER_DETECTED',
            created_at__gte=week_ago
        ).count()
        
        # Events by type
        events_by_type = SecurityEvent.objects.filter(
            created_at__gte=week_ago
        ).values('event_type').annotate(count=Count('id'))
        
        return Response({
            'success': True,
            'data': {
                'summary': {
                    'critical_events': critical_events,
                    'high_events': high_events,
                    'failed_logins': failed_logins,
                    'tamper_attempts': tamper_attempts,
                },
                'events_by_type': list(events_by_type)
            }
        })