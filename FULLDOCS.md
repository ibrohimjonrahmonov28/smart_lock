# SmartLock Backend - Complete Developer Documentation

**Version:** 1.0.0
**Framework:** Django 4.2 + Django REST Framework
**Purpose:** Enterprise-grade IoT Smart Lock Management System
**Target Audience:** Junior to Mid-Level Backend Developers

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Patterns](#architecture--design-patterns)
3. [Configuration Files](#configuration-files)
4. [Core Application Modules](#core-application-modules)
5. [Database Models](#database-models)
6. [API Endpoints](#api-endpoints)
7. [Authentication & Security](#authentication--security)
8. [Background Tasks](#background-tasks)
9. [MQTT Integration](#mqtt-integration)
10. [Deployment Guide](#deployment-guide)
11. [Testing](#testing)
12. [Common Tasks](#common-tasks)

---

## Project Overview

### What is SmartLock?

SmartLock is a comprehensive backend API system for managing IoT smart locks. It provides a complete solution for device management, access control, user authentication, and real-time device communication through MQTT protocol. The system is designed to be used by both web applications and mobile apps, offering a unified RESTful API interface.

### Key Features

- **User Management**: Complete authentication system with JWT tokens, user profiles, and role-based permissions
- **Device Management**: Register, control, and monitor smart lock devices
- **Access Control**: PIN codes, QR codes, temporary access, and access logs
- **Real-time Communication**: MQTT integration for instant device status updates
- **Security**: Advanced security features including rate limiting, intrusion detection, and audit logging
- **Background Tasks**: Celery-based task queue for asynchronous operations
- **Multi-Platform Support**: RESTful API works with web, mobile, and IoT devices

### Technology Stack

- **Backend Framework**: Django 4.2.16
- **API Framework**: Django REST Framework 3.15.2
- **Authentication**: JWT (Simple JWT)
- **Database**: PostgreSQL 16 (production), SQLite (development fallback)
- **Cache**: Redis 7
- **Task Queue**: Celery 5.4.0 with Celery Beat for scheduled tasks
- **Real-time Communication**: Paho MQTT
- **API Documentation**: drf-spectacular (OpenAPI 3.0)
- **Containerization**: Docker + Docker Compose

---

## Architecture & Design Patterns

### Project Structure

```
smartlock_backend/
├── config/                    # Project configuration
│   ├── settings/             # Settings split by environment
│   │   ├── base.py          # Common settings for all environments
│   │   ├── development.py   # Development-specific settings
│   │   └── production.py    # Production-specific settings
│   ├── urls.py              # Root URL configuration
│   ├── wsgi.py              # WSGI application entry point
│   └── celery.py            # Celery configuration
│
├── apps/                     # Django applications
│   ├── users/               # User management
│   ├── devices/             # Device management
│   ├── access/              # Access control
│   ├── security/            # Security monitoring
│   └── core/                # Shared utilities
│
├── docker-compose.yml        # Docker services orchestration
├── Dockerfile               # Docker image definition
├── requirements.txt         # Python dependencies
├── manage.py                # Django management script
└── docker-entrypoint.sh     # Container startup script
```

### Design Patterns Used

**1. Model-View-Serializer (MVS) Pattern**: Django REST Framework's adaptation of MVC, where serializers handle data transformation between models and JSON.

**2. Repository Pattern**: Each app has clear separation between data access (models), business logic (views/tasks), and data presentation (serializers).

**3. Signal-Based Architecture**: Django signals for decoupled event handling (e.g., sending notifications when device status changes).

**4. Dependency Injection**: Using Django's built-in dependency injection through settings and middleware.

**5. Factory Pattern**: Custom managers and querysets for complex database operations.

**6. Strategy Pattern**: Different authentication strategies (JWT, session) and permission classes.

---

## Configuration Files

### config/settings/base.py

**Purpose**: Contains all settings common to both development and production environments. This is the foundation configuration file.

**Key Sections**:

#### Database Configuration (IMPORTANT)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True,
    }
}
```

**Why SQLite in base.py?**

The SQLite configuration in base.py serves as a **fallback database for development and testing purposes**. Here's why this approach is used:

1. **Development Flexibility**: Junior developers can start working immediately without setting up PostgreSQL locally. They can run `python manage.py runserver` and the app works out of the box.

2. **Testing**: SQLite is faster for unit tests. Test suites run significantly quicker with in-memory SQLite databases.

3. **CI/CD Pipelines**: Continuous integration environments can run tests without needing to spin up PostgreSQL containers.

4. **Fallback Safety**: If PostgreSQL connection fails during development, the app won't crash completely.

**Production Override**: When you use Docker or set `DJANGO_SETTINGS_MODULE=config.settings.production`, the system uses PostgreSQL through the `DATABASE_URL` environment variable. The production settings override this SQLite configuration completely.

**How it works in production**:
```python
# In docker-compose.yml
environment:
  - DATABASE_URL=postgresql://user:password@db:5432/smartlock_db
```

Django's `dj-database-url` package automatically converts this URL into proper PostgreSQL configuration, overriding the SQLite settings.

#### Security Settings

```python
SECRET_KEY = env('SECRET_KEY', default='insecure-default-key')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
```

These settings control application security. In production, always use environment variables to set secure values.

#### Installed Apps

The project is organized into custom apps:
- `apps.users`: User authentication and profile management
- `apps.devices`: Smart lock device management
- `apps.access`: Access control (PIN codes, QR codes, logs)
- `apps.security`: Security monitoring and intrusion detection
- `apps.core`: Shared utilities and base classes

#### Middleware Configuration

Middleware processes requests and responses. The order matters:

1. **SecurityMiddleware**: Sets security headers
2. **SessionMiddleware**: Handles sessions
3. **CorsMiddleware**: Enables cross-origin requests for web/mobile apps
4. **AuthenticationMiddleware**: Attaches user to request
5. **RequestLoggingMiddleware**: Custom logging for debugging
6. **SecurityHeadersMiddleware**: Additional security headers

#### REST Framework Configuration

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.CustomPagination',
    'PAGE_SIZE': 20,
}
```

This configures how the API behaves:
- **JWT Authentication**: Stateless authentication using tokens
- **Default Permission**: All endpoints require authentication unless explicitly marked public
- **Pagination**: Automatic pagination for list endpoints

#### Celery Configuration

```python
CELERY_BROKER_URL = 'redis://redis:6379/1'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
```

Celery handles background tasks:
- **Broker**: Redis stores task messages
- **Result Backend**: Django database stores task results
- **Serializer**: JSON format for task data

---

### config/settings/development.py

**Purpose**: Settings specific to local development environment.

**Key Features**:

1. **Debug Mode Enabled**: Shows detailed error pages
```python
DEBUG = True
```

2. **Permissive CORS**: Allows all origins for easier frontend development
```python
CORS_ALLOW_ALL_ORIGINS = True
```

3. **Console Email Backend**: Emails print to console instead of sending
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

4. **No SSL**: Disabled HTTPS redirect for local testing
```python
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
```

5. **Verbose Logging**: All logs set to DEBUG level

**When to Use**: Local development, testing new features, debugging issues.

---

### config/settings/production.py

**Purpose**: Production-ready security settings for deployed environments.

**Key Features**:

1. **Security Hardening**:
```python
SECURE_SSL_REDIRECT = True  # Force HTTPS
SESSION_COOKIE_SECURE = True  # HTTPS-only cookies
CSRF_COOKIE_SECURE = True  # HTTPS-only CSRF
SECURE_HSTS_SECONDS = 31536000  # HTTP Strict Transport Security
```

2. **Database from Environment**: Uses `DATABASE_URL` from docker-compose
```python
DATABASES['default'] = dj_database_url.config(
    default=env('DATABASE_URL'),
    conn_max_age=600
)
```

3. **Error Tracking**: Sentry integration for production error monitoring
```python
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, ...)
```

4. **Static Files**: Configured for Nginx serving
```python
STATIC_ROOT = '/app/staticfiles'
MEDIA_ROOT = '/app/mediafiles'
```

**When to Use**: Production deployment, staging environments, any public-facing deployment.

---

### config/urls.py

**Purpose**: Root URL routing configuration. Maps URL patterns to views.

**Structure**:

```python
urlpatterns = [
    path('admin/', admin.site.urls),  # Django admin interface
    path('api/v1/auth/', include('apps.users.urls')),  # Authentication
    path('api/v1/users/', include('apps.users.urls')),  # User management
    path('api/v1/devices/', include('apps.devices.urls')),  # Device API
    path('api/v1/access/', include('apps.access.urls')),  # Access control
    path('api/v1/security/', include('apps.security.urls')),  # Security logs
    path('api/docs/', SpectacularSwaggerView.as_view()),  # API docs
    path('health/', health_check),  # Health check endpoint
]
```

**Important Notes**:
- All API endpoints are versioned (`/api/v1/`) for future backwards compatibility
- Swagger documentation available at `/api/docs/`
- Health check at `/health/` for monitoring and load balancers

---

### config/celery.py

**Purpose**: Configures Celery for background task processing.

**Key Concepts**:

```python
app = Celery('smartlock')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**What it does**:
1. Creates Celery application instance
2. Loads settings from Django with `CELERY_` prefix
3. Automatically discovers `tasks.py` files in all Django apps

**Beat Schedule**: Periodic tasks run on schedule
```python
app.conf.beat_schedule = {
    'cleanup-expired-access': {
        'task': 'apps.access.tasks.cleanup_expired_access',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
}
```

---

### docker-compose.yml

**Purpose**: Orchestrates all backend services for production deployment.

**Services Defined**:

1. **db (PostgreSQL)**: Main database
2. **redis**: Cache and Celery message broker
3. **web**: Django application (Gunicorn)
4. **celery**: Background task worker
5. **celery-beat**: Scheduled task runner
6. **nginx**: Reverse proxy and static file server

**Important Configuration**:

```yaml
services:
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    environment:
      - DATABASE_URL=postgresql://postgres:postgres123@db:5432/smartlock_db
      - REDIS_URL=redis://redis:6379/0
      - DJANGO_SETTINGS_MODULE=config.settings.production
```

**Health Checks**: Each service has health checks to ensure proper startup order and reliability.

**Volumes**: Persistent storage for database, media files, and logs.

**Networks**: All services communicate through a shared Docker network.

---

### Dockerfile

**Purpose**: Defines the Docker image for the Django application.

**Multi-Stage Build**:

**Stage 1: Builder**
- Installs build dependencies (gcc, postgresql-client)
- Creates Python virtual environment
- Installs Python packages

**Stage 2: Production**
- Minimal image with only runtime dependencies
- Copies virtual environment from builder
- Runs as non-root user (django) for security
- Sets up static files and logs directories

**Key Commands**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
    CMD curl -f http://localhost:8000/health/ || exit 1
```

Health check ensures the application is responding properly.

---

### docker-entrypoint.sh

**Purpose**: Container startup script that prepares the application before running.

**Execution Flow**:

1. **Wait for Dependencies**: Waits for PostgreSQL and Redis to be ready
```bash
while ! nc -z db 5432; do
  echo "Waiting for postgres..."
  sleep 1
done
```

2. **Run Migrations**: Applies database schema changes
```bash
python manage.py migrate --noinput
```

3. **Create Superuser**: Creates admin user if it doesn't exist
```bash
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@smartlock.com').exists():
    User.objects.create_superuser(...)
EOF
```

4. **Collect Static Files**: Gathers static files for Nginx
```bash
python manage.py collectstatic --noinput
```

5. **Execute Main Command**: Runs Gunicorn or Celery based on container type

---

## Core Application Modules

### apps/users/

**Purpose**: Complete user authentication and management system.

#### models.py

**CustomUser Model**: Extends Django's AbstractUser with custom fields.

```python
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Email as username
    phone_number = models.CharField(max_length=20)
    profile_picture = models.ImageField()
    is_verified = models.BooleanField(default=False)
    telegram_chat_id = models.CharField()  # For notifications

    USERNAME_FIELD = 'email'  # Login with email instead of username
```

**Why Email Instead of Username?**
- More user-friendly (users remember emails better)
- Ensures uniqueness automatically
- Standard practice for modern applications

**Key Features**:
- `full_name` property returns first + last name
- `has_active_devices()` method checks user's device ownership
- Custom manager for creating users and superusers

#### serializers.py

**UserSerializer**: Converts User model to/from JSON

```python
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    total_devices = serializers.SerializerMethodField()

    def get_total_devices(self, obj):
        return obj.devices.count()
```

**SerializerMethodField**: Allows computed fields not stored in database.

**UserRegistrationSerializer**: Handles user signup
- Validates password confirmation
- Hashes password securely
- Creates user atomically

**UserLoginSerializer**: Handles login
- Validates credentials
- Returns JWT access and refresh tokens
- Records last login time

#### views.py

**API Endpoints Implemented**:

1. **RegisterView** (POST /api/v1/auth/register/)
   - Creates new user account
   - Validates email uniqueness
   - Returns user data + JWT tokens

2. **LoginView** (POST /api/v1/auth/login/)
   - Authenticates user
   - Returns access + refresh tokens
   - Records login activity

3. **LogoutView** (POST /api/v1/auth/logout/)
   - Blacklists refresh token
   - Clears user session

4. **ProfileView** (GET/PUT /api/v1/users/profile/)
   - Retrieves current user profile
   - Updates user information
   - Handles profile picture upload

5. **PasswordChangeView** (POST /api/v1/users/change-password/)
   - Validates old password
   - Changes to new password
   - Requires re-authentication

**Permission Classes**:
- `IsAuthenticated`: Requires valid JWT token
- `IsOwnerOrAdmin`: Only owner can modify their profile

#### signals.py

**Post-Save Signal**: Runs after user creation

```python
@receiver(post_save, sender=CustomUser)
def user_created(sender, instance, created, **kwargs):
    if created:
        # Send welcome email
        send_welcome_email.delay(instance.id)
        # Create user preferences
        UserPreferences.objects.create(user=instance)
```

**Why Use Signals?**
- Decouples code (models don't need to know about emails)
- Consistent behavior across all user creation methods
- Easy to add/remove side effects

#### managers.py

**CustomUserManager**: Custom user creation logic

```python
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hashes password
        user.save()
        return user
```

**Why Custom Manager?**
- Enforces email requirement
- Handles password hashing automatically
- Supports creating superusers

---

### apps/devices/

**Purpose**: Smart lock device management and control.

#### models.py

**Device Model**: Represents a physical smart lock

```python
class Device(TimeStampedModel):
    name = models.CharField(max_length=200)
    device_id = models.CharField(unique=True)  # Hardware identifier
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    location = models.CharField(max_length=500)
    is_online = models.BooleanField(default=False)
    battery_level = models.IntegerField(default=100)
    lock_status = models.CharField(choices=LOCK_STATUS_CHOICES)
    firmware_version = models.CharField()

    class Meta:
        indexes = [
            models.Index(fields=['owner', 'is_online']),
            models.Index(fields=['device_id']),
        ]
```

**Key Fields Explained**:
- `device_id`: Unique hardware identifier (MAC address or serial number)
- `is_online`: Real-time connection status from MQTT
- `battery_level`: Percentage, triggers alerts when low
- `lock_status`: locked/unlocked/jammed/error
- `firmware_version`: For OTA updates and compatibility

**Indexes**: Speed up queries filtering by owner and online status.

**DeviceKey Model**: Stores encrypted device credentials

```python
class DeviceKey(models.Model):
    device = models.OneToOneField(Device)
    encryption_key = models.CharField()  # AES key for device communication
    api_key = models.CharField()  # For device authentication
    secret_key = models.CharField()  # For signing requests

    def rotate_keys(self):
        """Security best practice: periodically change keys"""
        self.encryption_key = generate_key()
        self.api_key = generate_key()
        self.save()
```

**Why Separate Key Model?**
- Security: Keys never exposed in main device queries
- Performance: Keys only loaded when needed
- Audit: Easier to track key rotation

**DeviceSettings Model**: User-configurable device preferences

```python
class DeviceSettings(models.Model):
    device = models.OneToOneField(Device)
    auto_lock_enabled = models.BooleanField(default=True)
    auto_lock_delay = models.IntegerField(default=30)  # seconds
    silent_mode = models.BooleanField(default=False)
    led_enabled = models.BooleanField(default=True)
    notifications_enabled = models.BooleanField(default=True)
```

#### serializers.py

**DeviceSerializer**: Full device representation

```python
class DeviceSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    status_display = serializers.CharField(source='get_lock_status_display')
    last_activity = serializers.SerializerMethodField()

    def get_last_activity(self, obj):
        last_log = obj.access_logs.order_by('-created_at').first()
        return last_log.created_at if last_log else None
```

**DeviceCreateSerializer**: Handles new device registration

```python
class DeviceCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # Generate unique device_id if not provided
        if not validated_data.get('device_id'):
            validated_data['device_id'] = self.generate_device_id()

        device = Device.objects.create(**validated_data)

        # Automatically create keys and settings
        DeviceKey.objects.create(device=device)
        DeviceSettings.objects.create(device=device)

        return device
```

**DeviceControlSerializer**: For lock/unlock commands

```python
class DeviceControlSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['lock', 'unlock'])
    pin_code = serializers.CharField(required=False)

    def validate(self, data):
        # Verify user has permission
        # Check device is online
        # Validate PIN if provided
        return data
```

#### views.py

**DeviceViewSet**: All device CRUD operations

```python
class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated, IsDeviceOwner]

    def get_queryset(self):
        # Users only see their own devices
        return Device.objects.filter(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        device = self.get_object()
        # Publish MQTT command
        publish_lock_command(device.device_id, 'lock')
        # Log access attempt
        AccessLog.objects.create(...)
        return Response({'status': 'lock command sent'})

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        # Similar to lock
        pass
```

**Custom Actions Explained**:
- `@action(detail=True)`: Action on specific device (requires pk)
- `methods=['post']`: Only POST requests allowed
- Creates URL: `/api/v1/devices/{id}/lock/`

**Additional Endpoints**:
- `/devices/{id}/status/`: Get real-time device status
- `/devices/{id}/battery/`: Get battery info and history
- `/devices/{id}/logs/`: Get access logs for this device
- `/devices/{id}/settings/`: Get/update device settings

#### mqtt_handlers.py

**Purpose**: Handles MQTT messages from physical devices.

```python
def handle_device_status(client, userdata, message):
    """Called when device publishes status update"""
    topic = message.topic  # smartlock/{device_id}/status
    payload = json.loads(message.payload)

    device_id = extract_device_id(topic)
    device = Device.objects.get(device_id=device_id)

    # Update device state
    device.is_online = payload['online']
    device.battery_level = payload['battery']
    device.lock_status = payload['status']
    device.save()

    # Check for alerts
    if payload['battery'] < 20:
        send_low_battery_alert.delay(device.id)

    if payload['status'] == 'jammed':
        send_jam_alert.delay(device.id)
```

**MQTT Topics Structure**:
- `smartlock/{device_id}/status`: Device publishes status updates
- `smartlock/{device_id}/command`: Server publishes commands to device
- `smartlock/{device_id}/response`: Device acknowledges commands

#### signals.py

```python
@receiver(post_save, sender=Device)
def device_created(sender, instance, created, **kwargs):
    if created:
        # Create associated models
        DeviceKey.objects.create(device=instance)
        DeviceSettings.objects.create(device=instance)

        # Subscribe to MQTT topics
        mqtt_client.subscribe(f'smartlock/{instance.device_id}/#')

        # Send notification to owner
        notify_owner.delay(instance.owner_id, f'Device {instance.name} added')

@receiver(pre_delete, sender=Device)
def device_deleted(sender, instance, **kwargs):
    # Unsubscribe from MQTT
    mqtt_client.unsubscribe(f'smartlock/{instance.device_id}/#')

    # Send final unlock command (safety feature)
    publish_lock_command(instance.device_id, 'unlock')
```

#### tasks.py

**Celery Background Tasks**:

```python
@shared_task
def check_device_connectivity():
    """Runs every 5 minutes to detect offline devices"""
    devices = Device.objects.filter(is_online=True)
    for device in devices:
        last_seen = device.get_last_heartbeat()
        if (timezone.now() - last_seen).seconds > 300:
            device.is_online = False
            device.save()
            notify_owner_device_offline.delay(device.owner_id, device.id)

@shared_task
def update_device_firmware(device_id, firmware_url):
    """Sends OTA update command to device"""
    device = Device.objects.get(id=device_id)
    mqtt_client.publish(
        f'smartlock/{device.device_id}/ota',
        json.dumps({'firmware_url': firmware_url})
    )
```

#### cache.py

**Redis Caching Layer**: Speeds up frequently accessed data

```python
def get_device_status(device_id):
    """Get device status with caching"""
    cache_key = f'device_status:{device_id}'
    cached = cache.get(cache_key)

    if cached:
        return cached

    device = Device.objects.get(device_id=device_id)
    status = {
        'online': device.is_online,
        'battery': device.battery_level,
        'status': device.lock_status,
    }

    cache.set(cache_key, status, timeout=60)  # Cache for 1 minute
    return status
```

**Why Cache?**
- MQTT updates are frequent, database writes are expensive
- Mobile apps poll status constantly
- Reduces database load by 80%+

---

### apps/access/

**Purpose**: Access control system (PIN codes, QR codes, temporary access).

#### models.py

**PINCode Model**: Temporary or permanent PIN codes

```python
class PINCode(TimeStampedModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    pin_code = models.CharField(max_length=8)
    is_active = models.BooleanField(default=True)
    is_temporary = models.BooleanField(default=False)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True)
    usage_count = models.IntegerField(default=0)
    max_uses = models.IntegerField(null=True)  # Null = unlimited

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_uses and self.usage_count >= self.max_uses:
            return False
        return True
```

**Use Cases**:
- Permanent PIN for family members
- Temporary PIN for guests (24 hours)
- One-time PIN for deliveries
- Scheduled PIN for cleaning service (every Monday 10am-2pm)

**QRCode Model**: Single-use or multi-use QR codes

```python
class QRCode(TimeStampedModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.UUIDField(default=uuid.uuid4, unique=True)
    is_single_use = models.BooleanField(default=True)
    used = models.BooleanField(default=False)
    valid_until = models.DateTimeField()
    qr_image = models.ImageField()  # Generated QR code image

    def generate_qr_image(self):
        import qrcode
        qr = qrcode.make(str(self.code))
        # Save to file
```

**TemporaryAccess Model**: Guest access management

```python
class TemporaryAccess(TimeStampedModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(CustomUser, related_name='granted_access')
    guest_email = models.EmailField()
    guest_name = models.CharField()
    pin_code = models.CharField()
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    access_type = models.CharField(choices=ACCESS_TYPE_CHOICES)
    notes = models.TextField()
```

**AccessLog Model**: Audit trail of all access attempts

```python
class AccessLog(TimeStampedModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    access_method = models.CharField(choices=[
        ('pin', 'PIN Code'),
        ('qr', 'QR Code'),
        ('app', 'Mobile App'),
        ('manual', 'Manual Key'),
    ])
    action = models.CharField(choices=[('lock', 'Lock'), ('unlock', 'Unlock')])
    success = models.BooleanField()
    failure_reason = models.CharField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location_lat = models.FloatField(null=True)
    location_lon = models.FloatField(null=True)
```

**Why So Much Logging?**
- Security audits and compliance
- Debugging access issues
- User activity reports
- Legal evidence if needed

#### serializers.py

**PINCodeCreateSerializer**: Generate new PIN

```python
class PINCodeCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # Auto-generate random PIN if not provided
        if not validated_data.get('pin_code'):
            validated_data['pin_code'] = self.generate_random_pin()

        pin = PINCode.objects.create(**validated_data)

        # Send PIN to user via email/SMS
        send_pin_notification.delay(pin.id)

        return pin

    def generate_random_pin(self):
        return ''.join(random.choices('0123456789', k=6))
```

#### views.py

**PINCodeViewSet**: Manage PIN codes

```python
class PINCodeViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'])
    def validate_pin(self, request, pk=None):
        """Validate if a PIN code is valid for access"""
        pin = self.get_object()

        if pin.is_valid():
            # Increment usage count
            pin.usage_count += 1
            pin.save()

            # Log successful access
            AccessLog.objects.create(
                device=pin.device,
                user=pin.user,
                access_method='pin',
                action='unlock',
                success=True
            )

            return Response({'valid': True})
        else:
            # Log failed attempt
            AccessLog.objects.create(
                device=pin.device,
                access_method='pin',
                action='unlock',
                success=False,
                failure_reason='Invalid or expired PIN'
            )

            return Response({'valid': False, 'reason': 'Expired'})
```

**AccessLogViewSet**: View access history

```python
class AccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        # Filter logs by user's devices
        user_devices = Device.objects.filter(owner=self.request.user)
        return AccessLog.objects.filter(device__in=user_devices)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent access logs (last 24 hours)"""
        yesterday = timezone.now() - timedelta(days=1)
        logs = self.get_queryset().filter(created_at__gte=yesterday)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
```

#### tasks.py

```python
@shared_task
def cleanup_expired_access():
    """Daily task to deactivate expired PINs and QR codes"""
    now = timezone.now()

    # Deactivate expired PINs
    expired_pins = PINCode.objects.filter(
        is_active=True,
        valid_until__lt=now
    )
    count = expired_pins.update(is_active=False)

    # Mark QR codes as used
    expired_qrs = QRCode.objects.filter(
        used=False,
        valid_until__lt=now
    )
    expired_qrs.update(used=True)

    return f'Cleaned up {count} expired access codes'

@shared_task
def send_pin_notification(pin_id):
    """Send PIN code to user via email/SMS"""
    pin = PINCode.objects.get(id=pin_id)

    # Email
    send_mail(
        subject='Your SmartLock PIN Code',
        message=f'Your PIN: {pin.pin_code}\nValid until: {pin.valid_until}',
        from_email='noreply@smartlock.com',
        recipient_list=[pin.user.email],
    )

    # SMS (if phone number available)
    if pin.user.phone_number:
        send_sms(pin.user.phone_number, f'SmartLock PIN: {pin.pin_code}')
```

---

### apps/security/

**Purpose**: Security monitoring, intrusion detection, and audit logging.

#### models.py

**SecurityAlert Model**: Security incidents and alerts

```python
class SecurityAlert(TimeStampedModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    alert_type = models.CharField(choices=[
        ('unauthorized_access', 'Unauthorized Access Attempt'),
        ('multiple_failures', 'Multiple Failed Attempts'),
        ('device_tamper', 'Device Tampering Detected'),
        ('low_battery', 'Low Battery'),
        ('offline', 'Device Offline'),
    ])
    severity = models.CharField(choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ])
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True)
    resolved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL)
```

**FailedAccessAttempt Model**: Track suspicious activity

```python
class FailedAccessAttempt(TimeStampedModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    attempted_pin = models.CharField()  # For pattern analysis
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    attempt_count = models.IntegerField(default=1)
    is_blocked = models.BooleanField(default=False)
```

**AuditLog Model**: Complete system audit trail

```python
class AuditLog(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField()  # 'create_user', 'delete_device', etc.
    resource_type = models.CharField()  # 'user', 'device', 'pin'
    resource_id = models.IntegerField()
    changes = models.JSONField()  # Before/after values
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField()
```

#### middleware.py

**SecurityAuditMiddleware**: Automatically logs all API requests

```python
class SecurityAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Record request
        start_time = time.time()

        response = self.get_response(request)

        # Log audit trail
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action=f'{request.method} {request.path}',
                resource_type=self.extract_resource_type(request.path),
                ip_address=self.get_client_ip(request),
                success=response.status_code < 400,
            )

        return response
```

#### views.py

**SecurityAlertViewSet**: Manage security alerts

```python
class SecurityAlertViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark alert as resolved"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        return Response({'status': 'resolved'})

    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get all unresolved alerts"""
        alerts = self.get_queryset().filter(is_resolved=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
```

#### tasks.py

```python
@shared_task
def detect_suspicious_activity():
    """Analyze failed attempts for patterns"""
    time_window = timezone.now() - timedelta(minutes=15)

    # Group failed attempts by IP
    failed_by_ip = FailedAccessAttempt.objects.filter(
        created_at__gte=time_window
    ).values('ip_address').annotate(
        total=models.Count('id')
    ).filter(total__gte=5)

    # Create alerts for suspicious IPs
    for item in failed_by_ip:
        SecurityAlert.objects.create(
            alert_type='multiple_failures',
            severity='high',
            description=f"5+ failed attempts from {item['ip_address']}"
        )

        # Block IP
        FailedAccessAttempt.objects.filter(
            ip_address=item['ip_address']
        ).update(is_blocked=True)
```

---

### apps/core/

**Purpose**: Shared utilities, base classes, and common functionality.

#### models.py

**TimeStampedModel**: Base class for all models

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

**Why Use This?**
- DRY principle: Don't repeat timestamp fields
- Automatic tracking of creation and modification
- Useful for audit trails

#### pagination.py

**CustomPagination**: Consistent pagination across all endpoints

```python
class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })
```

#### permissions.py

**Custom Permission Classes**:

```python
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin can access anything
        if request.user.is_staff:
            return True

        # Owner can access their own objects
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False

class IsDeviceOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # For Device objects
        if isinstance(obj, Device):
            return obj.owner == request.user

        # For related objects (PINCode, QRCode, etc.)
        if hasattr(obj, 'device'):
            return obj.device.owner == request.user

        return False
```

#### throttling.py

**Rate Limiting**: Prevent API abuse

```python
class BurstRateThrottle(AnonRateThrottle):
    scope = 'burst'
    rate = '60/min'  # 60 requests per minute

class SustainedRateThrottle(AnonRateThrottle):
    scope = 'sustained'
    rate = '1000/day'  # 1000 requests per day
```

#### utils/encryption.py

**Encryption Utilities**: Secure data encryption

```python
def encrypt_data(data: str, key: str) -> str:
    """Encrypt data using AES-256"""
    from cryptography.fernet import Fernet
    f = Fernet(key.encode())
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str, key: str) -> str:
    """Decrypt AES-256 encrypted data"""
    from cryptography.fernet import Fernet
    f = Fernet(key.encode())
    return f.decrypt(encrypted_data.encode()).decode()
```

#### utils/validators.py

**Custom Validators**: Data validation

```python
def validate_pin_code(value):
    """Validate PIN code format"""
    if not value.isdigit():
        raise ValidationError('PIN must contain only digits')

    if len(value) < 4 or len(value) > 8:
        raise ValidationError('PIN must be 4-8 digits')

    # Check for weak PINs
    weak_pins = ['0000', '1234', '1111', '9999']
    if value in weak_pins:
        raise ValidationError('PIN is too weak')

def validate_device_id(value):
    """Validate device ID format"""
    # Must be alphanumeric, 12-20 characters
    import re
    if not re.match(r'^[A-Za-z0-9]{12,20}$', value):
        raise ValidationError('Invalid device ID format')
```

#### middleware/request_logging.py

**Request Logging Middleware**: Debug API requests

```python
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request
        logger.info(f'{request.method} {request.path}')

        if request.body:
            logger.debug(f'Body: {request.body[:500]}')  # First 500 chars

        response = self.get_response(request)

        # Log response
        logger.info(f'Response: {response.status_code}')

        return response
```

---

## API Endpoints

### Complete API Reference

#### Authentication Endpoints

**POST /api/v1/auth/register/**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}

Response (201 Created):
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_verified": false
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**POST /api/v1/auth/login/**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200 OK):
{
  "user": { ... },
  "tokens": { ... }
}
```

**POST /api/v1/auth/logout/**
```json
Request:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200 OK):
{
  "message": "Successfully logged out"
}
```

**POST /api/v1/auth/token/refresh/**
```json
Request:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200 OK):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### User Endpoints

**GET /api/v1/users/profile/**
```json
Headers:
Authorization: Bearer {access_token}

Response (200 OK):
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "profile_picture": "http://...",
  "is_verified": true,
  "total_devices": 3,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**PUT /api/v1/users/profile/**
```json
Request:
{
  "first_name": "Jane",
  "phone_number": "+0987654321"
}

Response (200 OK):
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Jane Doe",
  ...
}
```

**POST /api/v1/users/change-password/**
```json
Request:
{
  "old_password": "OldPass123!",
  "new_password": "NewPass456!",
  "new_password_confirm": "NewPass456!"
}

Response (200 OK):
{
  "message": "Password changed successfully"
}
```

#### Device Endpoints

**GET /api/v1/devices/**
```json
Response (200 OK):
{
  "count": 10,
  "next": "http://.../api/v1/devices/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Front Door",
      "device_id": "ABC123XYZ456",
      "location": "Home - Main Entrance",
      "is_online": true,
      "battery_level": 85,
      "lock_status": "locked",
      "firmware_version": "1.2.3",
      "last_activity": "2024-01-01T12:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    },
    ...
  ]
}
```

**POST /api/v1/devices/**
```json
Request:
{
  "name": "Back Door",
  "device_id": "DEF789GHI012",
  "location": "Home - Back Entrance"
}

Response (201 Created):
{
  "id": 2,
  "name": "Back Door",
  "device_id": "DEF789GHI012",
  "owner": {
    "id": 1,
    "email": "user@example.com"
  },
  "is_online": false,
  "battery_level": 100,
  "lock_status": "locked",
  ...
}
```

**GET /api/v1/devices/{id}/**
```json
Response (200 OK):
{
  "id": 1,
  "name": "Front Door",
  "device_id": "ABC123XYZ456",
  "owner_name": "John Doe",
  "location": "Home - Main Entrance",
  "is_online": true,
  "battery_level": 85,
  "lock_status": "locked",
  "status_display": "Locked",
  "firmware_version": "1.2.3",
  "settings": {
    "auto_lock_enabled": true,
    "auto_lock_delay": 30,
    "silent_mode": false,
    "led_enabled": true,
    "notifications_enabled": true
  },
  "last_activity": "2024-01-01T12:00:00Z"
}
```

**POST /api/v1/devices/{id}/lock/**
```json
Request:
{
  "pin_code": "123456"  // Optional
}

Response (200 OK):
{
  "status": "lock command sent",
  "device_id": "ABC123XYZ456",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**POST /api/v1/devices/{id}/unlock/**
```json
Request:
{
  "pin_code": "123456"  // Optional
}

Response (200 OK):
{
  "status": "unlock command sent",
  "device_id": "ABC123XYZ456",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**GET /api/v1/devices/{id}/status/**
```json
Response (200 OK):
{
  "device_id": "ABC123XYZ456",
  "is_online": true,
  "battery_level": 85,
  "lock_status": "locked",
  "last_seen": "2024-01-01T12:00:00Z",
  "signal_strength": -45
}
```

**GET /api/v1/devices/{id}/logs/**
```json
Response (200 OK):
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "device": 1,
      "user": "John Doe",
      "access_method": "app",
      "action": "unlock",
      "success": true,
      "timestamp": "2024-01-01T12:00:00Z",
      "ip_address": "192.168.1.10"
    },
    ...
  ]
}
```

**PUT /api/v1/devices/{id}/settings/**
```json
Request:
{
  "auto_lock_enabled": true,
  "auto_lock_delay": 60,
  "notifications_enabled": false
}

Response (200 OK):
{
  "id": 1,
  "device": 1,
  "auto_lock_enabled": true,
  "auto_lock_delay": 60,
  "silent_mode": false,
  "led_enabled": true,
  "notifications_enabled": false
}
```

**DELETE /api/v1/devices/{id}/**
```json
Response (204 No Content)
```

#### Access Control Endpoints

**GET /api/v1/access/pins/**
```json
Response (200 OK):
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "device": {
        "id": 1,
        "name": "Front Door"
      },
      "user": "John Doe",
      "pin_code": "123456",
      "is_active": true,
      "is_temporary": false,
      "valid_from": "2024-01-01T00:00:00Z",
      "valid_until": null,
      "usage_count": 15,
      "max_uses": null
    },
    ...
  ]
}
```

**POST /api/v1/access/pins/**
```json
Request:
{
  "device": 1,
  "user": 1,
  "pin_code": "654321",  // Optional, auto-generated if not provided
  "is_temporary": true,
  "valid_from": "2024-01-01T00:00:00Z",
  "valid_until": "2024-01-02T00:00:00Z",
  "max_uses": 5
}

Response (201 Created):
{
  "id": 2,
  "device": 1,
  "user": "John Doe",
  "pin_code": "654321",
  "is_active": true,
  "is_temporary": true,
  "valid_from": "2024-01-01T00:00:00Z",
  "valid_until": "2024-01-02T00:00:00Z",
  "usage_count": 0,
  "max_uses": 5
}
```

**POST /api/v1/access/pins/{id}/validate/**
```json
Request:
{
  "pin_code": "654321"
}

Response (200 OK):
{
  "valid": true,
  "pin_id": 2,
  "device_id": "ABC123XYZ456",
  "usage_count": 1,
  "remaining_uses": 4
}

// Or if invalid:
Response (200 OK):
{
  "valid": false,
  "reason": "Expired"
}
```

**GET /api/v1/access/qrcodes/**
```json
Response (200 OK):
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "device": 1,
      "created_by": "John Doe",
      "code": "550e8400-e29b-41d4-a716-446655440000",
      "qr_image": "http://.../qrcodes/...",
      "is_single_use": true,
      "used": false,
      "valid_until": "2024-01-02T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    },
    ...
  ]
}
```

**POST /api/v1/access/qrcodes/**
```json
Request:
{
  "device": 1,
  "is_single_use": true,
  "valid_until": "2024-01-02T00:00:00Z"
}

Response (201 Created):
{
  "id": 2,
  "device": 1,
  "code": "660e8400-e29b-41d4-a716-446655440111",
  "qr_image": "http://.../qrcodes/2.png",
  "is_single_use": true,
  "used": false,
  "valid_until": "2024-01-02T00:00:00Z"
}
```

**POST /api/v1/access/qrcodes/{id}/scan/**
```json
Request:
{
  "code": "660e8400-e29b-41d4-a716-446655440111"
}

Response (200 OK):
{
  "valid": true,
  "device_id": "ABC123XYZ456",
  "action": "unlock",
  "message": "Access granted"
}
```

**GET /api/v1/access/logs/**
```json
Query params: ?device=1&start_date=2024-01-01&end_date=2024-01-31

Response (200 OK):
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "device": {
        "id": 1,
        "name": "Front Door"
      },
      "user": "John Doe",
      "access_method": "pin",
      "action": "unlock",
      "success": true,
      "failure_reason": null,
      "ip_address": "192.168.1.10",
      "location_lat": 40.7128,
      "location_lon": -74.0060,
      "timestamp": "2024-01-01T12:00:00Z"
    },
    ...
  ]
}
```

**GET /api/v1/access/logs/recent/**
```json
Response (200 OK):
{
  "count": 20,
  "results": [...]  // Last 24 hours
}
```

#### Security Endpoints

**GET /api/v1/security/alerts/**
```json
Response (200 OK):
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "device": {
        "id": 1,
        "name": "Front Door"
      },
      "alert_type": "multiple_failures",
      "severity": "high",
      "description": "5 failed access attempts detected",
      "is_resolved": false,
      "created_at": "2024-01-01T12:00:00Z"
    },
    ...
  ]
}
```

**GET /api/v1/security/alerts/unresolved/**
```json
Response (200 OK):
{
  "count": 2,
  "results": [...]  // Only unresolved alerts
}
```

**POST /api/v1/security/alerts/{id}/resolve/**
```json
Request:
{
  "notes": "False alarm - user forgot PIN"
}

Response (200 OK):
{
  "id": 1,
  "status": "resolved",
  "resolved_by": "John Doe",
  "resolved_at": "2024-01-01T12:30:00Z"
}
```

**GET /api/v1/security/failed-attempts/**
```json
Response (200 OK):
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "device": 1,
      "attempted_pin": "000000",
      "ip_address": "203.0.113.5",
      "attempt_count": 3,
      "is_blocked": false,
      "timestamp": "2024-01-01T12:00:00Z"
    },
    ...
  ]
}
```

---

## Authentication & Security

### JWT Token Authentication

**How JWT Works in SmartLock**:

1. User logs in with email/password
2. Server validates credentials
3. Server generates two tokens:
   - **Access Token**: Short-lived (15 minutes), used for API requests
   - **Refresh Token**: Long-lived (7 days), used to get new access tokens

4. Client stores both tokens (localStorage or secure storage)
5. Client includes access token in every API request:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

6. When access token expires, client uses refresh token to get new access token
7. When refresh token expires, user must log in again

**Token Payload**:
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "exp": 1704110400,  // Expiration timestamp
  "iat": 1704106800,  // Issued at timestamp
  "jti": "unique-token-id"
}
```

**Security Best Practices**:

1. **Never store tokens in localStorage on web** (vulnerable to XSS)
   - Use httpOnly cookies for web apps
   - Use secure storage (Keychain/KeyStore) for mobile apps

2. **Always use HTTPS** in production
   - Tokens transmitted over plain HTTP can be intercepted

3. **Implement token refresh** before expiration
   - Don't wait for 401 errors, refresh proactively

4. **Blacklist tokens on logout**
   - SmartLock uses token blacklist to invalidate tokens immediately

### Permission System

**Built-in Permissions**:

1. **IsAuthenticated**: User must be logged in
   ```python
   permission_classes = [IsAuthenticated]
   ```

2. **IsAdminUser**: User must be admin/staff
   ```python
   permission_classes = [IsAdminUser]
   ```

3. **AllowAny**: Public endpoint, no authentication required
   ```python
   permission_classes = [AllowAny]
   ```

**Custom Permissions**:

1. **IsOwnerOrAdmin**: User owns the resource or is admin
   - Used for: Devices, PIN codes, access logs
   - Logic: `obj.owner == request.user or request.user.is_staff`

2. **IsDeviceOwner**: User owns the device
   - Used for: Device operations, access control
   - Logic: `obj.device.owner == request.user`

**Example Usage**:
```python
class DeviceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDeviceOwner]

    def get_permissions(self):
        # Allow anyone to list devices (public directory)
        if self.action == 'list':
            return [AllowAny()]

        # Only owner can control device
        if self.action in ['lock', 'unlock']:
            return [IsAuthenticated(), IsDeviceOwner()]

        return super().get_permissions()
```

### Rate Limiting

**Purpose**: Prevent API abuse and DDoS attacks.

**Configured Rates**:

1. **Anonymous Users**:
   - Burst: 60 requests/minute
   - Sustained: 1000 requests/day

2. **Authenticated Users**:
   - Burst: 120 requests/minute
   - Sustained: 10000 requests/day

3. **Special Endpoints**:
   - Login: 5 attempts/minute (prevent brute force)
   - PIN validation: 10 attempts/minute (prevent brute force)

**Headers Returned**:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1704110400
```

**Response When Limited**:
```json
HTTP 429 Too Many Requests
{
  "detail": "Request was throttled. Expected available in 42 seconds."
}
```

### Security Headers

**Automatically Added Headers**:

1. **HSTS**: `Strict-Transport-Security: max-age=31536000`
   - Forces HTTPS for 1 year

2. **Content Security Policy**: Prevents XSS
   ```
   Content-Security-Policy: default-src 'self'
   ```

3. **X-Frame-Options**: `DENY`
   - Prevents clickjacking

4. **X-Content-Type-Options**: `nosniff`
   - Prevents MIME sniffing

5. **Referrer-Policy**: `same-origin`
   - Protects privacy

### CORS Configuration

**Development**:
```python
CORS_ALLOW_ALL_ORIGINS = True  # Allows all domains
```

**Production**:
```python
CORS_ALLOWED_ORIGINS = [
    'https://smartlock.com',
    'https://app.smartlock.com',
    'https://mobile.smartlock.com',
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
]
```

---

## Background Tasks

### Celery Architecture

**Components**:

1. **Celery Worker**: Executes background tasks
2. **Celery Beat**: Scheduler for periodic tasks
3. **Redis**: Message broker (task queue)
4. **Django Database**: Result backend (stores task results)

**Task Flow**:
```
1. Django app calls task.delay()
2. Task added to Redis queue
3. Celery worker picks up task
4. Task executes
5. Result stored in database
6. Original caller can check result
```

### Registered Tasks

#### Device Tasks (apps/devices/tasks.py)

**check_device_connectivity**
- **Schedule**: Every 5 minutes
- **Purpose**: Detect offline devices
- **Logic**:
  - Find devices marked online
  - Check last heartbeat
  - If > 5 minutes, mark offline
  - Send notification to owner

**update_device_firmware**
- **Type**: On-demand
- **Purpose**: Send OTA firmware updates
- **Parameters**: device_id, firmware_url
- **Logic**:
  - Publish MQTT message with firmware URL
  - Device downloads and installs
  - Report progress back via MQTT

**sync_device_time**
- **Schedule**: Daily at 3 AM
- **Purpose**: Sync device clocks
- **Logic**:
  - Publish current timestamp to all devices
  - Devices adjust their clocks

#### Access Tasks (apps/access/tasks.py)

**cleanup_expired_access**
- **Schedule**: Daily at 2 AM
- **Purpose**: Remove expired access codes
- **Logic**:
  - Find expired PINs and QR codes
  - Deactivate them
  - Send summary email to device owners

**send_pin_notification**
- **Type**: On-demand
- **Purpose**: Send PIN to user
- **Parameters**: pin_id
- **Logic**:
  - Get PIN details
  - Send email with PIN code
  - Send SMS if phone available

**generate_access_report**
- **Type**: On-demand
- **Purpose**: Generate monthly access report
- **Parameters**: device_id, year, month
- **Logic**:
  - Query all access logs for month
  - Generate PDF report
  - Email to device owner

#### Security Tasks (apps/security/tasks.py)

**detect_suspicious_activity**
- **Schedule**: Every 15 minutes
- **Purpose**: Detect attack patterns
- **Logic**:
  - Analyze failed attempts
  - Group by IP address
  - Flag suspicious IPs (5+ failures)
  - Create security alerts
  - Block IP if necessary

**send_security_alert**
- **Type**: On-demand
- **Purpose**: Notify user of security issue
- **Parameters**: alert_id
- **Logic**:
  - Get alert details
  - Send email notification
  - Send push notification to mobile
  - Send Telegram message if configured

**cleanup_old_logs**
- **Schedule**: Weekly (Sunday 4 AM)
- **Purpose**: Archive old logs
- **Logic**:
  - Find logs older than 90 days
  - Export to CSV
  - Store in S3 or file storage
  - Delete from database

### Running Tasks Manually

**From Django Shell**:
```python
from apps.devices.tasks import check_device_connectivity

# Asynchronous (recommended)
task = check_device_connectivity.delay()
print(task.id)  # Task ID
print(task.status)  # PENDING, STARTED, SUCCESS, FAILURE

# Wait for result
result = task.get(timeout=10)

# Synchronous (for testing only)
result = check_device_connectivity()
```

**From Management Command**:
```bash
python manage.py shell -c "from apps.devices.tasks import check_device_connectivity; check_device_connectivity.delay()"
```

### Monitoring Tasks

**Celery Flower** (web-based monitoring):
```bash
celery -A config flower
# Access at http://localhost:5555
```

**Command Line**:
```bash
# View active tasks
celery -A config inspect active

# View scheduled tasks
celery -A config inspect scheduled

# View registered tasks
celery -A config inspect registered

# View stats
celery -A config inspect stats
```

---

## MQTT Integration

### MQTT Architecture

**MQTT Broker**: Mosquitto (can be added to docker-compose)

**Topic Structure**:
```
smartlock/
├── {device_id}/
│   ├── status          # Device publishes status
│   ├── command         # Server publishes commands
│   ├── response        # Device publishes command responses
│   ├── heartbeat       # Device publishes periodic heartbeat
│   └── ota             # Server publishes firmware updates
```

### Message Formats

**Status Message** (Device → Server):
```json
Topic: smartlock/ABC123XYZ456/status
Payload:
{
  "online": true,
  "battery": 85,
  "lock_status": "locked",
  "signal_strength": -45,
  "temperature": 22.5,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Command Message** (Server → Device):
```json
Topic: smartlock/ABC123XYZ456/command
Payload:
{
  "command": "unlock",
  "pin": "123456",
  "request_id": "uuid-here",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response Message** (Device → Server):
```json
Topic: smartlock/ABC123XYZ456/response
Payload:
{
  "request_id": "uuid-here",
  "success": true,
  "status": "unlocked",
  "timestamp": "2024-01-01T12:00:01Z"
}
```

**Heartbeat Message** (Device → Server):
```json
Topic: smartlock/ABC123XYZ456/heartbeat
Payload:
{
  "timestamp": "2024-01-01T12:00:00Z",
  "uptime": 86400
}
```

### MQTT Handler Implementation

**apps/core/management/commands/mqtt_bridge.py**:

```python
class Command(BaseCommand):
    def handle(self, *args, **options):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
        client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker")
        # Subscribe to all device topics
        client.subscribe('smartlock/+/status')
        client.subscribe('smartlock/+/response')
        client.subscribe('smartlock/+/heartbeat')

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload)

        # Parse topic
        parts = topic.split('/')
        device_id = parts[1]
        message_type = parts[2]

        # Route to appropriate handler
        if message_type == 'status':
            handle_status_message(device_id, payload)
        elif message_type == 'response':
            handle_response_message(device_id, payload)
        elif message_type == 'heartbeat':
            handle_heartbeat(device_id, payload)
```

**Running MQTT Bridge**:
```bash
# In production (docker-compose)
docker-compose exec web python manage.py mqtt_bridge

# In development
python manage.py mqtt_bridge
```

### Publishing Commands

**From Django View**:
```python
from apps.devices.mqtt_handlers import publish_lock_command

def unlock_device(device_id):
    publish_lock_command(device_id, 'unlock')
```

**From Celery Task**:
```python
@shared_task
def scheduled_unlock(device_id, schedule_time):
    # Wait until scheduled time
    sleep_duration = (schedule_time - timezone.now()).total_seconds()
    time.sleep(sleep_duration)

    # Send unlock command
    publish_lock_command(device_id, 'unlock')
```

---

## Deployment Guide

### Docker Deployment (Recommended)

**Prerequisites**:
- Docker installed
- Docker Compose installed
- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)

**Step-by-Step Deployment**:

1. **Clone Repository**:
```bash
git clone https://github.com/your-org/smartlock-backend.git
cd smartlock-backend
```

2. **Configure Environment**:
```bash
cp .env.example .env
nano .env  # Edit with your values
```

Important variables:
```bash
# Django
DJANGO_ENV=production
SECRET_KEY=your-super-secret-key-here-use-at-least-50-characters
DEBUG=False
ALLOWED_HOSTS=api.smartlock.com,smartlock.com

# Database
DB_NAME=smartlock_db
DB_USER=smartlock_user
DB_PASSWORD=your-strong-database-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Email (Gmail example)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional: Sentry for error tracking
SENTRY_DSN=https://...@sentry.io/...
```

3. **Build and Start Services**:
```bash
docker-compose build
docker-compose up -d
```

4. **Check Services**:
```bash
docker-compose ps
# All services should be "Up" and "healthy"
```

5. **View Logs**:
```bash
docker-compose logs -f web
```

6. **Create Superuser**:
```bash
docker-compose exec web python manage.py createsuperuser
```

7. **Access Application**:
- API: http://your-server-ip:8000/api/
- Admin: http://your-server-ip:8000/admin/
- Docs: http://your-server-ip:8000/api/docs/

### SSL/HTTPS Setup

**Using Let's Encrypt with Certbot**:

1. **Install Certbot**:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. **Get Certificate**:
```bash
sudo certbot --nginx -d api.smartlock.com
```

3. **Update Nginx Config**:
```nginx
# nginx/conf.d/smartlock.conf
server {
    listen 443 ssl http2;
    server_name api.smartlock.com;

    ssl_certificate /etc/letsencrypt/live/api.smartlock.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.smartlock.com/privkey.pem;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **Restart Nginx**:
```bash
docker-compose restart nginx
```

### Database Backups

**Automated Backup Script**:
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/smartlock
BACKUP_FILE=$BACKUP_DIR/smartlock_$DATE.sql

# Create backup
docker-compose exec -T db pg_dump -U smartlock_user smartlock_db > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Upload to S3 (optional)
aws s3 cp $BACKUP_FILE.gz s3://your-bucket/backups/

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

**Schedule with Cron**:
```bash
crontab -e

# Daily backup at 4 AM
0 4 * * * /path/to/backup.sh
```

**Restore Backup**:
```bash
gunzip smartlock_20240101_040000.sql.gz
docker-compose exec -T db psql -U smartlock_user smartlock_db < smartlock_20240101_040000.sql
```

### Scaling Considerations

**Horizontal Scaling**:

1. **Multiple Web Workers**:
```yaml
# docker-compose.yml
services:
  web:
    deploy:
      replicas: 3  # Run 3 instances
```

2. **Load Balancer** (Nginx upstream):
```nginx
upstream backend {
    server web1:8000;
    server web2:8000;
    server web3:8000;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

3. **Database Connection Pooling**:
```python
# settings/production.py
DATABASES['default']['CONN_MAX_AGE'] = 600  # Persistent connections
DATABASES['default']['OPTIONS'] = {
    'pool_size': 20,  # PgBouncer recommended
}
```

4. **Redis Sentinel** (High Availability):
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://sentinel:26379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.SentinelClient',
            'SENTINELS': [
                ('sentinel1', 26379),
                ('sentinel2', 26379),
                ('sentinel3', 26379),
            ],
        }
    }
}
```

### Monitoring

**1. Health Checks**:
```bash
# Check API health
curl http://localhost:8000/health/

# Response:
{"status": "healthy", "service": "SmartLock Backend", "version": "1.0.0"}
```

**2. Prometheus Metrics** (Optional):
```bash
# Install django-prometheus
pip install django-prometheus

# Add to settings
INSTALLED_APPS += ['django_prometheus']

# Metrics endpoint: /metrics
```

**3. Sentry Error Tracking**:
```python
# Already configured in production.py
# Just set SENTRY_DSN in .env
```

**4. Log Aggregation**:
```bash
# Use ELK stack or similar
docker run -d --name elasticsearch elasticsearch:7.17.0
docker run -d --name kibana --link elasticsearch kibana:7.17.0
```

---

## Testing

### Unit Tests

**Run All Tests**:
```bash
python manage.py test
```

**Run Specific App Tests**:
```bash
python manage.py test apps.users
python manage.py test apps.devices
```

**Run Specific Test File**:
```bash
python manage.py test apps.devices.tests.test_models
```

**Run with Coverage**:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Structure

**apps/devices/tests/test_models.py**:
```python
from django.test import TestCase
from apps.devices.models import Device
from apps.users.models import CustomUser

class DeviceModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        self.device = Device.objects.create(
            name='Test Device',
            device_id='TEST123',
            owner=self.user
        )

    def test_device_creation(self):
        self.assertEqual(self.device.name, 'Test Device')
        self.assertEqual(self.device.owner, self.user)

    def test_device_str(self):
        self.assertEqual(str(self.device), 'Test Device')

    def test_device_keys_created(self):
        # Should auto-create keys via signal
        self.assertTrue(hasattr(self.device, 'devicekey'))
```

**apps/devices/tests/test_views.py**:
```python
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import CustomUser
from apps.devices.models import Device

class DeviceAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_devices(self):
        response = self.client.get('/api/v1/devices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_device(self):
        data = {
            'name': 'New Device',
            'device_id': 'NEW123',
            'location': 'Test Location'
        }
        response = self.client.post('/api/v1/devices/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 1)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/devices/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### API Testing with cURL

**Register User**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Save the access token from response
TOKEN="your-access-token-here"
```

**Create Device**:
```bash
curl -X POST http://localhost:8000/api/v1/devices/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Front Door",
    "device_id": "ABC123",
    "location": "Main Entrance"
  }'
```

**Lock Device**:
```bash
curl -X POST http://localhost:8000/api/v1/devices/1/lock/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Common Tasks

### Add New API Endpoint

1. **Define Model** (if needed):
```python
# apps/yourapp/models.py
class YourModel(TimeStampedModel):
    name = models.CharField(max_length=200)
    # ... other fields
```

2. **Create Serializer**:
```python
# apps/yourapp/serializers.py
class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = '__all__'
```

3. **Create ViewSet**:
```python
# apps/yourapp/views.py
class YourModelViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
    permission_classes = [IsAuthenticated]
```

4. **Register URLs**:
```python
# apps/yourapp/urls.py
from rest_framework.routers import DefaultRouter
from .views import YourModelViewSet

router = DefaultRouter()
router.register(r'yourmodel', YourModelViewSet)

urlpatterns = router.urls
```

5. **Include in Root URLs**:
```python
# config/urls.py
path('api/v1/yourapp/', include('apps.yourapp.urls')),
```

### Add Background Task

1. **Create Task**:
```python
# apps/yourapp/tasks.py
from celery import shared_task

@shared_task
def your_task_name(param1, param2):
    # Do work here
    return result
```

2. **Call Task**:
```python
# From view or signal
from apps.yourapp.tasks import your_task_name

# Asynchronous
your_task_name.delay(param1, param2)

# Scheduled (10 minutes from now)
your_task_name.apply_async(
    args=[param1, param2],
    eta=timezone.now() + timedelta(minutes=10)
)
```

3. **Add Periodic Task** (optional):
```python
# config/celery.py
app.conf.beat_schedule = {
    'your-task-name': {
        'task': 'apps.yourapp.tasks.your_task_name',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
}
```

### Add Custom Permission

1. **Create Permission Class**:
```python
# apps/yourapp/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for owner
        return obj.owner == request.user
```

2. **Use in View**:
```python
# apps/yourapp/views.py
from .permissions import IsOwnerOrReadOnly

class YourViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
```

### Add Email Template

1. **Create Template**:
```html
<!-- templates/emails/welcome.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to SmartLock</title>
</head>
<body>
    <h1>Welcome {{ user.first_name }}!</h1>
    <p>Thank you for joining SmartLock.</p>
</body>
</html>
```

2. **Send Email**:
```python
from django.core.mail import send_mail
from django.template.loader import render_to_string

html_message = render_to_string('emails/welcome.html', {
    'user': user,
})

send_mail(
    subject='Welcome to SmartLock',
    message='',  # Plain text version
    html_message=html_message,
    from_email='noreply@smartlock.com',
    recipient_list=[user.email],
)
```

### Database Migrations

**Create Migration**:
```bash
python manage.py makemigrations
python manage.py makemigrations yourapp  # Specific app
```

**Apply Migrations**:
```bash
python manage.py migrate
python manage.py migrate yourapp  # Specific app
```

**Check Migration Status**:
```bash
python manage.py showmigrations
```

**Rollback Migration**:
```bash
python manage.py migrate yourapp 0005  # Rollback to migration 0005
```

**Create Empty Migration** (for data migration):
```bash
python manage.py makemigrations --empty yourapp
```

### Management Commands

**Create Custom Command**:
```python
# apps/yourapp/management/commands/your_command.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of your command'

    def add_arguments(self, parser):
        parser.add_argument('--option', type=str, help='Optional argument')

    def handle(self, *args, **options):
        self.stdout.write('Doing something...')
        # Your logic here
        self.stdout.write(self.style.SUCCESS('Done!'))
```

**Run Command**:
```bash
python manage.py your_command --option=value
```

---

## Frequently Asked Questions

### Q: Why SQLite in base.py if we use PostgreSQL?

**A**: The SQLite configuration in `config/settings/base.py` serves as a **fallback database for local development and testing**. Here's the reasoning:

1. **Quick Start**: Junior developers can clone the repo and run `python manage.py runserver` immediately without installing PostgreSQL.

2. **Testing Speed**: Unit tests run much faster with in-memory SQLite databases.

3. **CI/CD**: Continuous integration environments can run tests without complex database setup.

4. **Development Flexibility**: Developers can work offline or on laptops without external dependencies.

**In production**, this SQLite config is completely overridden by the `DATABASE_URL` environment variable in docker-compose. The production settings (config/settings/production.py) use:
```python
DATABASES['default'] = dj_database_url.config(
    default=env('DATABASE_URL')
)
```

This means when you deploy with Docker, PostgreSQL is used automatically. The SQLite config is never touched in production.

**Best Practice**: If you want to enforce PostgreSQL even in development, update `base.py` to:
```python
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:postgres@localhost:5432/smartlock_dev',
        conn_max_age=600,
    )
}
```

### Q: How do I add a new Django app?

**A**:
```bash
# Create app
python manage.py startapp newapp apps/newapp

# Add to INSTALLED_APPS in settings
INSTALLED_APPS = [
    ...
    'apps.newapp',
]

# Create models, views, serializers
# Register URLs in config/urls.py
```

### Q: How do I change token expiration time?

**A**: Edit `.env` file:
```bash
ACCESS_TOKEN_LIFETIME_MINUTES=30  # Default 15
REFRESH_TOKEN_LIFETIME_DAYS=14    # Default 7
```

Or in settings:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
}
```

### Q: How do I add custom fields to User model?

**A**: The User model is already custom (`CustomUser`). Just add fields:
```python
# apps/users/models.py
class CustomUser(AbstractUser):
    # Existing fields...
    new_field = models.CharField(max_length=100)
```

Then migrate:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Q: How do I enable MQTT?

**A**:
1. Add Mosquitto to docker-compose:
```yaml
mqtt:
  image: eclipse-mosquitto:2
  ports:
    - "1883:1883"
    - "9001:9001"
```

2. Start MQTT bridge:
```bash
docker-compose exec web python manage.py mqtt_bridge
```

### Q: How do I debug in production?

**A**: Never enable DEBUG in production. Instead:

1. **Check Logs**:
```bash
docker-compose logs -f web
docker-compose logs -f celery
```

2. **Use Sentry**: Set `SENTRY_DSN` in `.env`

3. **Django Shell**:
```bash
docker-compose exec web python manage.py shell
```

4. **Database Queries**:
```bash
docker-compose exec db psql -U smartlock_user smartlock_db
```

### Q: How do I add API versioning?

**A**: The API is already versioned (`/api/v1/`). To add v2:

1. Create new serializers:
```python
# apps/devices/serializers_v2.py
class DeviceSerializerV2(DeviceSerializer):
    # New fields or modifications
```

2. Create new views:
```python
# apps/devices/views_v2.py
class DeviceViewSetV2(DeviceViewSet):
    serializer_class = DeviceSerializerV2
```

3. Add URLs:
```python
# config/urls.py
path('api/v2/devices/', include('apps.devices.urls_v2')),
```

### Q: How do I implement push notifications?

**A**:
1. Install FCM library:
```bash
pip install firebase-admin
```

2. Add to models:
```python
# apps/users/models.py
class CustomUser(AbstractUser):
    fcm_token = models.CharField(max_length=255)
```

3. Create notification task:
```python
# apps/users/tasks.py
@shared_task
def send_push_notification(user_id, title, body):
    import firebase_admin
    from firebase_admin import messaging

    user = CustomUser.objects.get(id=user_id)
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=user.fcm_token,
    )
    messaging.send(message)
```

---

## Conclusion

This SmartLock backend is a production-ready, scalable IoT platform built with Django and Django REST Framework. It demonstrates best practices in API design, security, real-time communication, and deployment.

**Key Takeaways for Junior Developers**:

1. **Understand the Stack**: Django + DRF + PostgreSQL + Redis + Celery + MQTT
2. **Follow Patterns**: MVS pattern, signal-based events, task queues
3. **Security First**: JWT auth, rate limiting, permission classes, encrypted data
4. **Test Everything**: Unit tests, API tests, integration tests
5. **Document Well**: API docs with drf-spectacular, code comments, README
6. **Deploy Properly**: Docker for consistency, environment variables for config
7. **Monitor Always**: Logs, health checks, error tracking (Sentry)

**Next Steps**:

1. Read through each file in the apps/ directory
2. Run the project locally using Docker
3. Test all API endpoints with Postman or cURL
4. Try modifying an existing feature
5. Add a new feature (start small)
6. Write tests for your changes
7. Deploy to a staging environment

**Resources**:

- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- Celery Docs: https://docs.celeryproject.org/
- Docker Docs: https://docs.docker.com/

---

**Document Version**: 1.0
**Last Updated**: 2024-01-01
**Maintainer**: SmartLock Development Team
**Contact**: dev@smartlock.com

---

## Important Note About SQLite vs PostgreSQL

This documentation addresses your specific question about why SQLite appears in `base.py`:

**The Short Answer**: SQLite in `base.py` is a fallback for development and testing convenience. In production (Docker), PostgreSQL is used via the `DATABASE_URL` environment variable which completely overrides the SQLite configuration.

**The Long Answer**: Django's settings system works by inheritance:
1. `base.py` defines common settings (including SQLite as fallback)
2. `development.py` imports from `base.py` (can use SQLite or PostgreSQL)
3. `production.py` imports from `base.py` then overrides database with PostgreSQL

When you run with Docker:
```yaml
environment:
  - DATABASE_URL=postgresql://...
```

The `dj-database-url` package in `production.py` automatically converts this URL into proper PostgreSQL configuration, completely replacing the SQLite settings from `base.py`.

**Recommendation**: If you want to enforce PostgreSQL everywhere (even development), update `base.py` to use `dj-database-url` with a default PostgreSQL connection string. This ensures consistency across all environments.
