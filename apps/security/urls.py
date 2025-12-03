"""
Security URLs
"""

from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    # Security Events
    path('events/', views.SecurityEventListView.as_view(), name='security-events'),
    
    # Audit Logs (Admin only)
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit-logs'),
    
    # Dashboard
    path('dashboard/', views.SecurityDashboardView.as_view(), name='security-dashboard'),
]