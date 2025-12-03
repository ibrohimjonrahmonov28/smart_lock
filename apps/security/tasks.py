"""
Security Celery tasks
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_daily_report():
    """
    Generate daily security report (Periodic task)
    """
    from .models import SecurityEvent
    
    try:
        yesterday = timezone.now() - timedelta(days=1)
        
        # Count events by severity
        critical_count = SecurityEvent.objects.filter(
            severity='CRITICAL',
            created_at__gte=yesterday
        ).count()
        
        high_count = SecurityEvent.objects.filter(
            severity='HIGH',
            created_at__gte=yesterday
        ).count()
        
        medium_count = SecurityEvent.objects.filter(
            severity='MEDIUM',
            created_at__gte=yesterday
        ).count()
        
        # Log summary
        logger.info(
            f"Daily Security Report: "
            f"Critical: {critical_count}, "
            f"High: {high_count}, "
            f"Medium: {medium_count}"
        )
        
        # TODO: Send email report to admins
        
        return {
            'success': True,
            'critical': critical_count,
            'high': high_count,
            'medium': medium_count,
        }
        
    except Exception as e:
        logger.error(f"Error generating daily report: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_logs():
    """
    Cleanup old logs (90 days retention)
    """
    from .models import SecurityEvent, AuditLog
    
    try:
        retention_days = 90
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        # Delete old security events
        deleted_events = SecurityEvent.objects.filter(
            created_at__lt=cutoff_date,
            resolved=True
        ).delete()
        
        logger.info(f"Cleaned up {deleted_events[0]} old security events")
        
        # Note: AuditLog is kept forever (compliance)
        
        return {
            'success': True,
            'deleted_events': deleted_events[0],
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up logs: {str(e)}")
        return {'success': False, 'error': str(e)}