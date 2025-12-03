# SmartLock Backend - To'liq Texnik Qo'llanma

Bu qo'llanmada backend kodining qanday ishlashi, arxitekturasi va keyinchalik qanday davom ettirish tushuntirilgan.

---

## 📚 Mundarija

1. [Loyiha tuzilishi](#loyiha-tuzilishi)
2. [Backend arxitektura](#backend-arxitektura)
3. [Kod qanday ishlaydi](#kod-qanday-ishlaydi)
4. [Ma'lumotlar bazasi](#malumotlar-bazasi)
5. [API qanday yasalgan](#api-qanday-yasalgan)
6. [Yangi funksiya qo'shish](#yangi-funksiya-qoshish)
7. [Xatolarni topish va tuzatish](#xatolarni-topish-va-tuzatish)

---

## 📁 Loyiha tuzilishi

```
smartlock_backend/
├── apps/                         # Asosiy ilovalar
│   ├── users/                   # Foydalanuvchilar (User)
│   │   ├── models.py            # Database modellari (User)
│   │   ├── views.py             # API endpointlar (Login, Register)
│   │   ├── serializers.py       # JSON konvertatsiya
│   │   ├── urls.py              # URL yo'llari
│   │   ├── admin.py             # Admin panel
│   │   ├── apps.py              # App config
│   │   ├── signals.py           # Signal handlerlar
│   │   ├── migrations/          # Database o'zgarishlari
│   │   └── tests/               # Testlar
│   │
│   ├── devices/                 # Qurilmalar (Device)
│   │   ├── models.py            # Device, DeviceLog, DeviceSharing
│   │   ├── views.py             # CRUD, Lock/Unlock API
│   │   ├── serializers.py       # JSON serializer
│   │   ├── urls.py              # URL routing
│   │   ├── tasks.py             # Celery background tasks
│   │   ├── mqtt_handlers.py     # MQTT aloqa
│   │   ├── permissions.py       # Ruxsatlar (IsDeviceOwner)
│   │   ├── admin.py             # Admin panel
│   │   ├── signals.py           # Signal handlerlar
│   │   ├── migrations/          # Migratsiyalar
│   │   └── tests/               # Testlar
│   │
│   ├── access/                  # Kirish nazorati (PIN, QR)
│   │   ├── models.py            # PINCode, QRCode, AccessLog
│   │   ├── views.py             # PIN yaratish/tekshirish
│   │   ├── serializers.py       # JSON serializer
│   │   ├── urls.py              # URL routing
│   │   ├── tasks.py             # Background tasks
│   │   ├── admin.py             # Admin panel
│   │   ├── signals.py           # Signal handlerlar
│   │   ├── management/          # Custom commands
│   │   ├── migrations/          # Migratsiyalar
│   │   └── tests/               # Testlar
│   │
│   ├── security/                # Xavfsizlik
│   │   ├── models.py            # SecurityAlert, FailedAttempt
│   │   ├── views.py             # Alert API
│   │   ├── serializers.py       # JSON serializer
│   │   ├── urls.py              # URL routing
│   │   ├── tasks.py             # Monitoring tasks
│   │   ├── admin.py             # Admin panel
│   │   ├── signals.py           # Signal handlerlar
│   │   ├── migrations/          # Migratsiyalar
│   │   └── tests/               # Testlar
│   │
│   └── core/                    # Umumiy utillar
│       ├── models.py            # Abstract modellar (UUIDModel, TimeStampedModel)
│       ├── permissions.py       # Custom permissions
│       ├── pagination.py        # Pagination klasslar
│       ├── exceptions.py        # Custom exceptionlar
│       ├── throttling.py        # Rate limiting
│       ├── middleware/          # Middleware
│       │   ├── request_logging.py  # Request loglar
│       │   └── security.py      # Security headers
│       ├── utils/               # Utility funksiyalar
│       │   ├── encryption.py    # Shifrlash
│       │   └── validators.py    # Validatorlar
│       ├── management/          # Management commands
│       │   └── commands/
│       │       ├── mqtt_bridge.py   # MQTT bridge
│       │       └── wait_for_db.py   # Database kutish
│       └── tests/               # Testlar
│
├── config/                      # Sozlamalar
│   ├── settings/                # Settings paketlari
│   │   ├── __init__.py         # Settings loader
│   │   ├── base.py             # Asosiy sozlamalar
│   │   ├── development.py      # Development sozlamalar
│   │   └── production.py       # Production sozlamalar
│   ├── urls.py                 # Asosiy URL routing
│   ├── celery.py               # Celery config
│   ├── wsgi.py                 # WSGI config
│   └── asgi.py                 # ASGI config
│
├── staticfiles/                 # Yig'ilgan static fayllar (collectstatic)
├── mediafiles/                  # User yuklamalari (rasm, fayl)
├── logs/                        # Log fayllar
│
├── docker-compose.yml           # Docker xizmatlari
├── Dockerfile                   # Docker image
├── docker-entrypoint.sh         # Container boshlash skripti
├── requirements.txt             # Python paketlar
├── .env                        # Environment variables (SECRET!)
├── .dockerignore               # Docker ignore
├── .gitignore                  # Git ignore
├── manage.py                   # Django boshqaruv
│
├── start.sh                    # Serverni ishga tushirish
├── stop.sh                     # Serverni to'xtatish
├── restart.sh                  # Qayta ishga tushirish
├── logs.sh                     # Loglarni ko'rish
│
├── README.md                   # Asosiy qo'llanma
├── FULLDOCS.md                 # To'liq hujjat (ingliz)
├── DOKUMENTATSIYA_UZ.md        # O'zbek qo'llanma
├── TEXNIK_QOLLANMA_UZ.md       # Texnik qo'llanma (siz o'qiyapsiz)
├── INTERN_QOLLANMA.md          # Intern uchun oddiy qo'llanma
├── POSTMAN_TESTS_USERS.md      # Postman testlar
└── CREDENTIALS.md              # Login ma'lumotlari

```

### Har bir fayl nima uchun kerak:

- **models.py** - Ma'lumotlar bazasi jadvallari (User, Device, Log)
- **views.py** - API endpointlar (GET, POST, PATCH, DELETE)
- **serializers.py** - Python obyektlarni JSON'ga aylantirish
- **urls.py** - API yo'llarini belgilash
- **tasks.py** - Background ishlar (Celery)
- **permissions.py** - Kim nimaga ruxsat borligini tekshirish

---

## 🏗️ Backend arxitektura

### 1. Request qanday ishlaydi

```
Client (Postman/App)
    ↓
    | HTTP Request (POST /api/v1/auth/login/)
    ↓
Nginx (80 port)
    ↓
Gunicorn (Django server)
    ↓
Django Middleware
    ↓
URL Routing (urls.py)
    ↓
View (views.py)
    ↓
Serializer (ma'lumotni tekshirish)
    ↓
Database (PostgreSQL)
    ↓
Serializer (JSON'ga aylantirish)
    ↓
View (javob qaytarish)
    ↓
Client (Response)
```

### 2. Arxitektura komponentlari

```
┌─────────────────────────────────────────┐
│         Frontend (Mobile/Web)            │
└──────────────┬──────────────────────────┘
               │ REST API (JSON)
               ↓
┌──────────────────────────────────────────┐
│          Nginx (Reverse Proxy)           │
└──────────────┬───────────────────────────┘
               ↓
┌──────────────────────────────────────────┐
│    Django REST Framework (Backend)       │
│  ┌────────────────────────────────────┐  │
│  │ Authentication (JWT)                │  │
│  │ Authorization (Permissions)         │  │
│  │ Business Logic (Views)              │  │
│  │ Data Validation (Serializers)       │  │
│  └────────────────────────────────────┘  │
└──────┬───────────────────┬───────────────┘
       │                   │
       ↓                   ↓
┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis     │
│  (Database)  │    │   (Cache)    │
└──────────────┘    └──────────────┘
       ↓
┌──────────────────────────┐
│   Celery (Background)    │
│  - Device commands       │
│  - Notifications         │
│  - Periodic tasks        │
└──────────────────────────┘
```

---

## 💻 Kod qanday ishlaydi

### Misol 1: Login API

**Fayl:** `apps/users/views.py`

```python
class UserLoginView(APIView):
    """
    User login endpoint
    Foydalanuvchi kirish API'si
    """
    permission_classes = [permissions.AllowAny]  # Hammaga ochiq
    serializer_class = UserLoginSerializer

    def post(self, request):
        # 1. Ma'lumotni tekshirish
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Foydalanuvchini olish
        user = serializer.validated_data['user']

        # 3. IP manzilni saqlash
        user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save()

        # 4. JWT token yaratish
        refresh = RefreshToken.for_user(user)

        # 5. Javob qaytarish
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        }, status=status.HTTP_200_OK)
```

**Qadamma-qadam tushuntirish:**

1. **Line 1-3:** API class yaratish
2. **Line 4:** Ruxsatlar - hamma kirishi mumkin
3. **Line 7:** POST metod - ma'lumot qabul qilish
4. **Line 9-10:** Serializer bilan tekshirish (email/parol to'g'rimi?)
5. **Line 13:** Foydalanuvchini olish
6. **Line 16-17:** IP manzilni saqlash (xavfsizlik uchun)
7. **Line 20:** JWT token yaratish
8. **Line 23-33:** JSON javob qaytarish

---

### Misol 2: Serializer (Ma'lumotni tekshirish)

**Fayl:** `apps/users/serializers.py`

```python
class UserLoginSerializer(serializers.Serializer):
    """
    Ma'lumotlarni tekshirish uchun serializer
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """
        Email va parolni tekshirish
        """
        email = attrs.get('email')
        password = attrs.get('password')

        # Database'dan foydalanuvchini qidirish
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError('Invalid email or password')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')

        attrs['user'] = user
        return attrs
```

**Bu kod nima qiladi:**

1. **Line 5:** Email formatini tekshiradi (`test@example.com` bo'lishi kerak)
2. **Line 6:** Parol bormi tekshiradi, lekin javobda ko'rsatmaydi (`write_only`)
3. **Line 8:** `validate()` - asosiy tekshirish metodi
4. **Line 16:** Database'dan foydalanuvchini topish
5. **Line 18-19:** Agar topilmasa - xato
6. **Line 21-22:** Agar o'chirilgan bo'lsa - xato
7. **Line 24:** User obyektini qaytarish

---

### Misol 3: Model (Database jadvali)

**Fayl:** `apps/users/models.py`

```python
class User(AbstractBaseUser, PermissionsMixin, UUIDModel, TimeStampedModel):
    """
    Custom User model
    Foydalanuvchi modeli
    """
    # Maydonlar (fields)
    email = models.EmailField(unique=True)  # Unikal email
    phone = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    # Statuslar
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Tasdiqlanish
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    # Xavfsizlik
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    # Django kerakli
    USERNAME_FIELD = 'email'  # Email bilan login
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """To'liq ism qaytarish"""
        return f"{self.first_name} {self.last_name}"
```

**Tushuntirish:**

- **Line 7:** Email - unikal bo'lishi kerak (2 ta bir xil email bo'lmaydi)
- **Line 13-15:** Statuslar - faol/xodim/admin
- **Line 18-19:** Tasdiqlash - email/telefon tasdiqlangan
- **Line 22:** Oxirgi kirish IP manzili
- **Line 25:** Email bilan kirish (username o'rniga)
- **Line 28-29:** String representation (print qilganda)
- **Line 31-33:** Property - computed field (saqlanmaydi, faqat hisoblanadi)

**Database'da qanday ko'rinadi:**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    password VARCHAR(255),
    is_active BOOLEAN,
    email_verified BOOLEAN,
    last_login_ip INET,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 🗄️ Ma'lumotlar bazasi

### Database tuzilishi

```
users (foydalanuvchilar)
├── id (UUID)
├── email (unique)
├── password (hashed)
├── first_name
├── last_name
├── phone
├── is_active
└── created_at

devices (qurilmalar)
├── id (UUID)
├── device_id (unique)
├── name
├── owner_id (→ users.id)
├── status (ACTIVE/INACTIVE)
├── is_locked (true/false)
├── battery_level (0-100)
└── created_at

device_logs (tarix)
├── id (UUID)
├── device_id (→ devices.id)
├── user_id (→ users.id)
├── event_type (UNLOCK/LOCK/...)
├── success (true/false)
├── ip_address
└── created_at

pin_codes (PIN kodlar)
├── id (UUID)
├── device_id (→ devices.id)
├── code (hashed)
├── is_active
├── expires_at
└── created_at
```

### Relation (Bog'lanishlar)

```
User ─┬─── Device (1 user → ko'p device)
      │
      └─── DeviceLog (1 user → ko'p log)

Device ─┬─── DeviceLog (1 device → ko'p log)
        │
        ├─── PINCode (1 device → ko'p PIN)
        │
        └─── QRCode (1 device → ko'p QR)
```

### Migration (Database o'zgarishi)

Yangi maydon qo'shish:

```bash
# 1. Model o'zgartiring (models.py)
class Device(models.Model):
    # Yangi maydon qo'shing
    firmware_version = models.CharField(max_length=20, default='1.0.0')

# 2. Migration yaratish
docker-compose exec web python manage.py makemigrations

# 3. Database'ga qo'llash
docker-compose exec web python manage.py migrate
```

---

## 🔌 API qanday yasalgan

### REST API tamoyillari

```
Resource (Resurs):    /api/v1/devices/
Action (Harakat):     GET, POST, PATCH, DELETE

GET    /devices/          → Hammasini olish (List)
POST   /devices/          → Yangi yaratish (Create)
GET    /devices/{id}/     → Bittasini olish (Retrieve)
PATCH  /devices/{id}/     → Yangilash (Update)
DELETE /devices/{id}/     → O'chirish (Delete)

POST   /devices/{id}/unlock/  → Custom action
```

### URL Routing

**Fayl:** `apps/devices/urls.py`

```python
urlpatterns = [
    # CRUD
    path('', views.DeviceListCreateView.as_view()),
    path('<uuid:pk>/', views.DeviceDetailView.as_view()),

    # Actions
    path('<uuid:pk>/unlock/', views.DeviceUnlockView.as_view()),
    path('<uuid:pk>/lock/', views.DeviceLockView.as_view()),
    path('<uuid:pk>/logs/', views.DeviceLogsView.as_view()),
]
```

**Asosiy URL:** `config/urls.py`

```python
urlpatterns = [
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/devices/', include('apps.devices.urls')),
    path('api/v1/access/', include('apps.access.urls')),
    path('api/v1/security/', include('apps.security.urls')),
]
```

### Authentication (Token)

**JWT Token qanday ishlaydi:**

```python
# 1. Login - Token olish
POST /auth/login/
{
  "email": "user@example.com",
  "password": "pass"
}

Response:
{
  "tokens": {
    "access": "eyJhbGc...",    # 15 daqiqa
    "refresh": "eyJhbGc..."    # 7 kun
  }
}

# 2. API'ga so'rov - Token bilan
GET /devices/
Header: Authorization: Bearer eyJhbGc...

# 3. Token eskirdi - Yangilash
POST /auth/token/refresh/
{
  "refresh": "eyJhbGc..."
}

Response:
{
  "access": "yangi_token..."
}
```

### Permission (Ruxsat) tizimi

**Fayl:** `apps/devices/permissions.py`

```python
class IsDeviceOwner(permissions.BasePermission):
    """
    Faqat device egasi ruxsat bor
    """
    def has_object_permission(self, request, view, obj):
        # obj.owner == request.user ?
        return obj.owner == request.user


class CanUnlockDevice(permissions.BasePermission):
    """
    Faqat owner yoki shared user unlock qilishi mumkin
    """
    def has_object_permission(self, request, view, obj):
        # Owner?
        if obj.owner == request.user:
            return True

        # Shared user?
        shared = DeviceSharing.objects.filter(
            device=obj,
            shared_with=request.user,
            can_unlock=True,
            is_active=True
        ).exists()

        return shared
```

**View'da ishlatish:**

```python
class DeviceUnlockView(APIView):
    permission_classes = [IsAuthenticated, CanUnlockDevice]

    def post(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        # Ruxsat tekshiriladi avtomatik
        self.check_object_permissions(request, device)

        # Unlock logic...
```

---

## ➕ Yangi funksiya qo'shish

### Misol: Device'ga "Reboot" funksiyasi qo'shish

#### 1. Yangi endpoint yaratish

**Fayl:** `apps/devices/views.py`

```python
class DeviceRebootView(APIView):
    """
    Qurilmani qayta ishga tushirish
    """
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwner]

    @extend_schema(
        tags=['Devices'],
        responses={200: OpenApiResponse(description='Reboot command sent')}
    )
    def post(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        self.check_object_permissions(request, device)

        # Device online tekshirish
        if not device.is_online:
            return Response({
                'success': False,
                'message': 'Device is offline'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Background task yuborish
        send_reboot_command.delay(
            device_id=str(device.id),
            user_id=str(request.user.id)
        )

        # Log yozish
        DeviceLog.objects.create(
            device=device,
            user=request.user,
            event_type='REBOOT',
            description='Device reboot initiated',
            ip_address=request.META.get('REMOTE_ADDR'),
            success=True
        )

        logger.info(f"Reboot command sent: {device.device_id}")

        return Response({
            'success': True,
            'message': 'Reboot command sent successfully'
        }, status=status.HTTP_200_OK)
```

#### 2. URL qo'shish

**Fayl:** `apps/devices/urls.py`

```python
urlpatterns = [
    # ... boshqa URL'lar
    path('<uuid:pk>/reboot/', views.DeviceRebootView.as_view(), name='device-reboot'),
]
```

#### 3. Celery task yaratish

**Fayl:** `apps/devices/tasks.py`

```python
@shared_task(bind=True, max_retries=3)
def send_reboot_command(self, device_id, user_id):
    """
    MQTT orqali reboot command yuborish
    """
    try:
        device = Device.objects.get(id=device_id)

        # MQTT topic
        topic = f"smartlock/{device.device_id}/commands"

        # Payload
        payload = {
            'command': 'REBOOT',
            'timestamp': timezone.now().isoformat(),
            'user_id': user_id
        }

        # MQTT publish
        mqtt_client.publish(topic, json.dumps(payload))

        logger.info(f"Reboot command sent to device: {device.device_id}")
        return {'success': True}

    except Device.DoesNotExist:
        logger.error(f"Device not found: {device_id}")
        return {'success': False, 'error': 'Device not found'}

    except Exception as e:
        logger.error(f"Reboot command failed: {str(e)}")
        # Retry
        raise self.retry(exc=e, countdown=60)
```

#### 4. Test qilish

```bash
# Postman'da test
POST http://localhost:8000/api/v1/devices/{device_id}/reboot/
Header: Authorization: Bearer {token}

# Kutilgan javob:
{
  "success": true,
  "message": "Reboot command sent successfully"
}
```

#### 5. Model'ga yangi event qo'shish

**Fayl:** `apps/devices/models.py`

```python
class DeviceLog(models.Model):
    EVENT_TYPE_CHOICES = [
        ('UNLOCK', 'Unlock'),
        ('LOCK', 'Lock'),
        ('REBOOT', 'Reboot'),  # ← Yangi event
        # ... boshqalar
    ]
```

#### 6. Migration

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

## 🐛 Xatolarni topish va tuzatish

### 1. Debug qilish

**Loglarni ko'rish:**

```bash
# Barcha loglar
./logs.sh

# Faqat web
./logs.sh web

# Faqat celery
docker-compose logs celery

# Real-time logs
docker-compose logs -f web
```

**Python debugger:**

```python
# views.py ichida
def post(self, request):
    import pdb; pdb.set_trace()  # ← Debug point

    # Kod davom etadi...
```

### 2. Database'ni tekshirish

```bash
# PostgreSQL'ga kirish
docker-compose exec db psql -U postgres -d smartlock_db

# Jadvallarni ko'rish
\dt

# Ma'lumotlarni ko'rish
SELECT * FROM users LIMIT 5;
SELECT * FROM devices WHERE owner_id = 'user_uuid';

# Statistika
SELECT COUNT(*) FROM device_logs;
SELECT event_type, COUNT(*) FROM device_logs GROUP BY event_type;
```

### 3. Tez-tez uchraydigan xatolar

#### Xato: "UNIQUE constraint failed"

**Sabab:** Database'da takroriy qiymat

**Tuzatish:**
```python
# Avval tekshiring
if Device.objects.filter(device_id=device_id).exists():
    return Response({'error': 'Device already exists'}, status=400)

# Keyin yarating
device = Device.objects.create(...)
```

#### Xato: "RelatedObjectDoesNotExist"

**Sabab:** Foreign key yo'q

**Tuzatish:**
```python
# To'g'ri usul
device = get_object_or_404(Device, pk=device_id)

# Yoki
try:
    device = Device.objects.get(pk=device_id)
except Device.DoesNotExist:
    return Response({'error': 'Device not found'}, status=404)
```

#### Xato: "ValidationError"

**Sabab:** Ma'lumot formati noto'g'ri

**Tuzatish:**
```python
serializer = DeviceSerializer(data=request.data)
if not serializer.is_valid():
    # Xatolarni ko'rish
    print(serializer.errors)
    return Response(serializer.errors, status=400)
```

### 4. Performance (Tezlik) muammolari

**Muammo:** So'rov sekin ishlaydi

**Tuzatish:**

```python
# Yomon - N+1 query
devices = Device.objects.all()
for device in devices:
    print(device.owner.email)  # Har safar query

# Yaxshi - select_related
devices = Device.objects.select_related('owner').all()
for device in devices:
    print(device.owner.email)  # Faqat 1 ta query

# Yaxshi - prefetch_related (many-to-many)
devices = Device.objects.prefetch_related('logs').all()
```

**Index qo'shish:**

```python
class Device(models.Model):
    device_id = models.CharField(max_length=50, unique=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['-created_at']),
        ]
```

---

## 🚀 Production'ga chiqarish

### 1. Environment sozlash

```bash
# .env faylni yangilang
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=50_ta_tasodifiy_belgi_bering
ALLOWED_HOSTS=api.yourdomain.com

# Database
DB_PASSWORD=kuchli_parol_bering

# Redis
REDIS_PASSWORD=redis_paroli
```

### 2. SSL sertifikat

```bash
sudo certbot --nginx -d api.yourdomain.com
```

### 3. Docker rebuild

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 4. Monitoring

```bash
# Healthcheck
curl https://api.yourdomain.com/health/

# Logs monitoring
docker-compose logs -f --tail=100

# Resource usage
docker stats
```

---

## 📚 Qo'shimcha o'rganish

### Django
- Official docs: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/

### PostgreSQL
- PostgreSQL tutorial: https://www.postgresqltutorial.com/

### Celery
- Celery docs: https://docs.celeryproject.org/

### Docker
- Docker docs: https://docs.docker.com/

---

## ✅ Keyingi qadamlar

1. ✅ API'larni Postman'da test qiling
2. ✅ Kod tuzilishini o'rganing
3. ✅ Kichik o'zgarish qiling va test qiling
4. ✅ Yangi endpoint yarating
5. ✅ Database migration qiling
6. ✅ Celery task yozing

---

**Omad! Backend development qiziqarli! 💻🚀**
