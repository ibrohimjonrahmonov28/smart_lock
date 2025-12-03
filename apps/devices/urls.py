"""
Device URLs
"""

from django.urls import path
from . import views

app_name = 'devices'

urlpatterns = [
    # Device CRUD
    path('', views.DeviceListCreateView.as_view(), name='device-list-create'),
    path('<uuid:pk>/', views.DeviceDetailView.as_view(), name='device-detail'),
    
    # Device Control
    path('<uuid:pk>/unlock/', views.DeviceUnlockView.as_view(), name='device-unlock'),
    path('<uuid:pk>/lock/', views.DeviceLockView.as_view(), name='device-lock'),
    path('<uuid:pk>/status/', views.DeviceStatusView.as_view(), name='device-status'),
    
    # Device Logs
    path('<uuid:pk>/logs/', views.DeviceLogsView.as_view(), name='device-logs'),
    
    # Device Sharing
    path('<uuid:pk>/sharing/', views.DeviceSharingListView.as_view(), name='device-sharing-list'),
    path('sharing/<uuid:pk>/', views.DeviceSharingDetailView.as_view(), name='device-sharing-detail'),
]