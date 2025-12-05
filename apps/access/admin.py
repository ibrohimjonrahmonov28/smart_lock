"""
Access admin
"""

from django.contrib import admin
from django import forms
from django.contrib import messages
from .models import NFCCard, PINCode, GuestAccess


@admin.register(NFCCard)
class NFCCardAdmin(admin.ModelAdmin):
    """
    NFC Card admin
    """
    list_display = [
        'name',
        'uid',
        'device',
        'user',
        'is_active',
        'is_valid',
        'usage_count',
        'created_at',
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'uid', 'device__name', 'user__email']
    readonly_fields = ['id', 'usage_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Card Info', {
            'fields': ('uid', 'name', 'device', 'user')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Usage', {
            'fields': ('usage_count', 'max_usage')
        }),
        ('Restrictions', {
            'fields': ('allowed_days', 'allowed_hours')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


class PINCodeAdminForm(forms.ModelForm):
    """
    Custom form for PIN Code with auto-generation
    """
    pin_code_input = forms.CharField(
        max_length=8,
        required=False,
        help_text='Enter PIN (4-8 digits) or leave empty to auto-generate',
        widget=forms.TextInput(attrs={
            'placeholder': 'Leave empty for auto-generate'
        })
    )

    class Meta:
        model = PINCode
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make pin_hash not required in form
        if 'pin_hash' in self.fields:
            self.fields['pin_hash'].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Get PIN from input field
        pin_code = self.cleaned_data.get('pin_code_input')

        # If no PIN provided, auto-generate
        if not pin_code:
            from .utils import generate_random_pin
            pin_code = generate_random_pin(6)
            # Store for display message
            self._generated_pin = pin_code

        # Set PIN (will be hashed)
        instance.set_pin(pin_code)

        if commit:
            instance.save()

        return instance


@admin.register(PINCode)
class PINCodeAdmin(admin.ModelAdmin):
    """
    PIN Code admin with auto-generation support
    """
    form = PINCodeAdminForm

    list_display = [
        'name',
        'device',
        'user',
        'is_active',
        'is_valid',
        'usage_count',
        'created_at',
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'device__name', 'user__email']
    readonly_fields = ['id', 'pin_hash', 'usage_count', 'created_at', 'updated_at']

    fieldsets = (
        ('PIN Info', {
            'fields': ('name', 'device', 'user', 'pin_code_input')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Usage', {
            'fields': ('usage_count', 'max_usage')
        }),
        ('Restrictions', {
            'fields': ('allowed_days', 'allowed_hours')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
        ('Technical (Read-only)', {
            'fields': ('id', 'pin_hash'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        # Set created_by if new object
        if not change:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)

        # Show generated PIN if auto-generated
        if hasattr(form, '_generated_pin'):
            pin = form._generated_pin
            messages.success(
                request,
                f'✅ PIN KOD YARATILDI: {pin} | Bu PIN ni mehmonlarga ayting!'
            )
            messages.warning(
                request,
                f'⚠️ DIQQAT: PIN "{pin}" faqat hozir ko\'rsatiladi. Screenshot qiling!'
            )


class GuestAccessAdminForm(forms.ModelForm):
    """
    Custom form for Guest Access with auto PIN generation
    """
    auto_generate_pin = forms.BooleanField(
        required=False,
        initial=True,
        help_text='Automatically generate PIN for guest (PIN access only)'
    )

    manual_pin = forms.CharField(
        max_length=8,
        required=False,
        help_text='Or enter PIN manually (4-8 digits)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Optional: Enter manual PIN'
        })
    )

    class Meta:
        model = GuestAccess
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        access_type = cleaned_data.get('access_type')
        nfc_card = cleaned_data.get('nfc_card')
        pin_code = cleaned_data.get('pin_code')

        # Validate based on access type
        if access_type == 'NFC' and not nfc_card:
            raise forms.ValidationError('NFC card is required for NFC access')

        if access_type == 'PIN' and not pin_code:
            # Will be created automatically in save()
            pass

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Store generated PIN for later display
        generated_pin = None

        # Auto-create PIN if needed
        if instance.access_type == 'PIN' and not instance.pin_code:
            # Get or generate PIN
            manual_pin = self.cleaned_data.get('manual_pin')
            auto_generate = self.cleaned_data.get('auto_generate_pin', True)

            if manual_pin:
                pin_value = manual_pin
            elif auto_generate:
                from .utils import generate_random_pin
                pin_value = generate_random_pin(6)
                generated_pin = pin_value
            else:
                raise forms.ValidationError('PIN is required or enable auto-generation')

            # Save instance first to ensure created_by is set
            if commit:
                instance.save()

            # Now create PIN Code object with proper created_by
            pin_code_obj = PINCode.objects.create(
                device=instance.device,
                name=f"Guest: {instance.guest_name}",
                valid_from=instance.valid_from,
                valid_until=instance.valid_until,
                created_by=instance.created_by
            )
            pin_code_obj.set_pin(pin_value)
            pin_code_obj.save()

            # Update instance with pin_code
            instance.pin_code = pin_code_obj
            if commit:
                instance.save()

            # Store for display
            if generated_pin:
                self._generated_pin = generated_pin
        elif commit:
            instance.save()

        return instance


@admin.register(GuestAccess)
class GuestAccessAdmin(admin.ModelAdmin):
    """
    Guest Access admin with auto PIN generation
    """
    form = GuestAccessAdminForm

    list_display = [
        'guest_name',
        'device',
        'access_type',
        'is_active',
        'valid_from',
        'valid_until',
        'created_at',
    ]
    list_filter = ['access_type', 'is_active', 'created_at']
    search_fields = ['guest_name', 'guest_email', 'device__name']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Guest Info', {
            'fields': ('guest_name', 'guest_email', 'guest_phone')
        }),
        ('Access Type', {
            'fields': ('device', 'access_type')
        }),
        ('NFC Access (if NFC selected)', {
            'fields': ('nfc_card',),
            'classes': ('collapse',)
        }),
        ('PIN Access (if PIN selected)', {
            'fields': ('pin_code', 'auto_generate_pin', 'manual_pin'),
            'description': 'Leave PIN code empty and enable auto-generation, or enter manual PIN'
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Set created_by if new object
        if not change:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)

        # Show generated PIN if auto-generated
        if hasattr(form, '_generated_pin'):
            pin = form._generated_pin
            messages.success(
                request,
                f'✅ MEHMON QO\'SHILDI! PIN KOD: {pin} | Mehmonlarga ayting: "{pin}" | Screenshot qiling!'
            )
            messages.warning(
                request,
                f'⚠️ MUHIM: PIN "{pin}" faqat hozir ko\'rsatiladi. Keyinchalik ko\'ra olmaysiz!'
            )