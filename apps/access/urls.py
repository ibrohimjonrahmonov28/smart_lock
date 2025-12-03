"""
Access URLs
"""

from django.urls import path
from . import views

app_name = 'access'

urlpatterns = [
    # NFC Cards
    path('devices/<uuid:device_id>/nfc/', views.NFCCardListCreateView.as_view(), name='nfc-list-create'),
    path('nfc/<uuid:pk>/', views.NFCCardDetailView.as_view(), name='nfc-detail'),
    
    # PIN Codes
    path('devices/<uuid:device_id>/pin/', views.PINCodeListCreateView.as_view(), name='pin-list-create'),
    path('pin/<uuid:pk>/', views.PINCodeDetailView.as_view(), name='pin-detail'),
    
    # Guest Access
    path('devices/<uuid:device_id>/guest/', views.GuestAccessListCreateView.as_view(), name='guest-list-create'),
]