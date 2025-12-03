# SmartLock Backend API

Production-ready IoT Smart Lock Management System with complete REST API.

---

## 🚀 Quick Start (3 Steps)

### 1. Start Backend
```bash
./start.sh
```

### 2. Access API
- **API**: http://localhost:8000/api/
- **Docs**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/

### 3. Default Login
```
Email:    admin@smartlock.com
Password: admin
```

---

## 📋 What's Included

✅ Complete REST API (80+ endpoints)
✅ JWT Authentication
✅ Device Management (CRUD + Control)
✅ Access Control (PIN, QR codes)
✅ Security Monitoring & Alerts
✅ Background Tasks (Celery)
✅ Interactive API Docs (Swagger)
✅ PostgreSQL + Redis
✅ Docker Deployment

---

## 🛠️ Management Commands

```bash
./start.sh      # Start all services
./stop.sh       # Stop all services
./restart.sh    # Restart services
./logs.sh       # View logs
./logs.sh web   # View web logs
./logs.sh db    # View database logs
```

---

## 🐳 Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| **web** | 8000 | Django API |
| **db** | 5432 | PostgreSQL |
| **redis** | 6379 | Cache |
| **celery** | - | Background tasks |
| **celery-beat** | - | Scheduled tasks |
| **nginx** | 80 | Reverse proxy |

---

## 📡 API Endpoints

### Authentication
```
POST /api/v1/auth/register/      # Register
POST /api/v1/auth/login/         # Login
POST /api/v1/auth/logout/        # Logout
POST /api/v1/auth/token/refresh/ # Refresh token
```

### Devices
```
GET    /api/v1/devices/           # List devices
POST   /api/v1/devices/           # Create device
GET    /api/v1/devices/{id}/      # Get device
PUT    /api/v1/devices/{id}/      # Update device
DELETE /api/v1/devices/{id}/      # Delete device
POST   /api/v1/devices/{id}/lock/   # Lock device
POST   /api/v1/devices/{id}/unlock/ # Unlock device
```

### Access Control
```
GET  /api/v1/access/pins/      # List PIN codes
POST /api/v1/access/pins/      # Create PIN
GET  /api/v1/access/qrcodes/   # List QR codes
POST /api/v1/access/qrcodes/   # Generate QR
GET  /api/v1/access/logs/      # Access logs
```

### Security
```
GET  /api/v1/security/alerts/            # Security alerts
POST /api/v1/security/alerts/{id}/resolve/ # Resolve alert
GET  /api/v1/security/failed-attempts/   # Failed attempts
```

**See full documentation**: [FULLDOCS.md](FULLDOCS.md)

---

## 🔌 Frontend Integration

### JavaScript Example
```javascript
const API_BASE = 'http://localhost:8000/api';

// Login
const response = await fetch(`${API_BASE}/v1/auth/login/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { tokens } = await response.json();

// Make authenticated request
const devices = await fetch(`${API_BASE}/v1/devices/`, {
  headers: { 'Authorization': `Bearer ${tokens.access}` }
});
```

### React/React Native
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

---

## ⚙️ Configuration

Edit `.env` file:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_NAME=smartlock_db
DB_USER=postgres
DB_PASSWORD=your-password

# JWT
ACCESS_TOKEN_LIFETIME_MINUTES=15
REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS (add your frontend URLs)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## 🧪 Testing API

### Using cURL
```bash
# Health check
curl http://localhost:8000/health/

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","password_confirm":"Test123!","first_name":"Test","last_name":"User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

### Using Swagger UI
1. Visit http://localhost:8000/api/docs/
2. Click "Authorize"
3. Login to get token
4. Test all endpoints interactively

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000 | xargs kill -9
```

### Services Not Starting
```bash
docker-compose ps          # Check status
docker-compose logs web    # Check logs
docker-compose restart     # Restart all
```

### Database Issues
```bash
docker-compose restart db
docker-compose exec db psql -U smartlock_user -d smartlock_db
```

### Reset Everything
```bash
./stop.sh
docker-compose down -v
./start.sh
```

---

## 📚 Documentation

- **[FULLDOCS.md](FULLDOCS.md)** - Complete developer documentation
- **API Docs**: http://localhost:8000/api/docs/ (Interactive)

---

## 🔐 Security Features

- JWT authentication with token blacklist
- Rate limiting (60 req/min, 1000 req/day)
- HTTPS support (production)
- CORS configuration
- Security headers (HSTS, CSP)
- Input validation
- SQL injection protection
- XSS protection
- Password hashing (PBKDF2)
- Audit logging

---

## 🚀 Production Deployment

1. Update `.env`:
   ```bash
   DJANGO_ENV=production
   DEBUG=False
   SECRET_KEY=<50+ character random key>
   ALLOWED_HOSTS=yourdomain.com
   ```

2. Set up SSL:
   ```bash
   sudo certbot --nginx -d api.yourdomain.com
   ```

3. Deploy:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. Monitor:
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

---

## 🛠️ Tech Stack

**Backend**: Django 4.2 + DRF 3.15
**Database**: PostgreSQL 16
**Cache**: Redis 7
**Queue**: Celery 5.4
**Server**: Gunicorn + Nginx
**Docs**: drf-spectacular
**Auth**: JWT (Simple JWT)
**Container**: Docker + Docker Compose

---

## 📊 Project Structure

```
smartlock_backend/
├── apps/                 # Django apps
│   ├── users/           # Authentication
│   ├── devices/         # Device management
│   ├── access/          # Access control
│   ├── security/        # Security logs
│   └── core/            # Utilities
├── config/              # Django config
│   ├── settings/        # Settings
│   ├── urls.py         # URL routing
│   └── celery.py       # Celery config
├── docker-compose.yml   # Docker services
├── Dockerfile          # Docker image
├── .env                # Environment vars
├── start.sh            # Start script
├── stop.sh             # Stop script
├── FULLDOCS.md         # Documentation
└── README.md           # This file
```

---

## 📞 Support

**Documentation**: [FULLDOCS.md](FULLDOCS.md)
**API Docs**: http://localhost:8000/api/docs/
**Health Check**: http://localhost:8000/health/

---

## ✅ Success Checklist

- [ ] Docker Desktop installed
- [ ] Backend started with `./start.sh`
- [ ] API accessible at http://localhost:8000/api/
- [ ] Swagger docs at http://localhost:8000/api/docs/
- [ ] Can login and get JWT token
- [ ] Can make authenticated requests

---

**Version**: 1.0.0
**License**: MIT
**Made with ❤️ for SmartLock**
