# SmartLock Backend - Qo'llanma (O'zbek tilida)

Aqlli qulf tizimining backend API'si. Juda oson va sodda.

---

## 🚀 Ishga tushirish

### 1. Serverni ishga tushirish
```bash
./start.sh
```

### 2. Ochish
- **API**: http://localhost:8000/api/
- **Hujjatlar**: http://localhost:8000/api/docs/
- **Admin panel**: http://localhost:8000/admin/

### 3. Kirish ma'lumotlari
```
Email:    admin@smartlock.com
Parol:    admin
```

---

## 📡 API Endpointlar (So'rovlar)

### Foydalanuvchilar (Users)

#### 1. Ro'yxatdan o'tish
```
POST /api/v1/auth/register/
```
**Jo'natish kerak:**
```json
{
  "email": "test@example.com",
  "password": "Parol123!",
  "password_confirm": "Parol123!",
  "first_name": "Ism",
  "last_name": "Familiya",
  "phone": "+998901234567"
}
```

#### 2. Kirish (Login)
```
POST /api/v1/auth/login/
```
**Jo'natish kerak:**
```json
{
  "email": "test@example.com",
  "password": "Parol123!"
}
```

**Javob (Response):**
```json
{
  "success": true,
  "data": {
    "user": {...},
    "tokens": {
      "access": "token_bu_yerda",
      "refresh": "refresh_token_bu_yerda"
    }
  }
}
```

**MUHIM:** `access` tokenni saqlang! Keyingi barcha so'rovlarda kerak bo'ladi.

#### 3. Profilni ko'rish
```
GET /api/v1/auth/profile/
```
**Header qo'shish kerak:**
```
Authorization: Bearer {access_token}
```

#### 4. Profilni yangilash
```
PATCH /api/v1/auth/profile/
```
**Header:**
```
Authorization: Bearer {access_token}
```
**Jo'natish:**
```json
{
  "first_name": "Yangi ism",
  "last_name": "Yangi familiya",
  "phone": "+998901234567"
}
```

#### 5. Parolni o'zgartirish
```
POST /api/v1/auth/change-password/
```
**Header:**
```
Authorization: Bearer {access_token}
```
**Jo'natish:**
```json
{
  "old_password": "Eski_parol",
  "new_password": "Yangi_parol123!",
  "new_password_confirm": "Yangi_parol123!"
}
```

#### 6. Chiqish (Logout)
```
POST /api/v1/auth/logout/
```
**Header:**
```
Authorization: Bearer {access_token}
```
**Jo'natish:**
```json
{
  "refresh": "{refresh_token}"
}
```

---

### Qurilmalar (Devices)

#### 1. Barcha qurilmalarni ko'rish
```
GET /api/v1/devices/
```
**Header:**
```
Authorization: Bearer {access_token}
```

#### 2. Yangi qurilma qo'shish
```
POST /api/v1/devices/
```
**Header:**
```
Authorization: Bearer {access_token}
```
**Jo'natish:**
```json
{
  "device_id": "LOCK-001",
  "name": "Eshik qulfi",
  "device_type": "DOOR_LOCK",
  "location": "Toshkent, Chilonzor",
  "latitude": 41.2995,
  "longitude": 69.2401
}
```

#### 3. Bitta qurilmani ko'rish
```
GET /api/v1/devices/{device_id}/
```
**Header:**
```
Authorization: Bearer {access_token}
```

#### 4. Qurilmani yangilash
```
PATCH /api/v1/devices/{device_id}/
```
**Header:**
```
Authorization: Bearer {access_token}
```
**Jo'natish:**
```json
{
  "name": "Yangi nom",
  "location": "Yangi manzil"
}
```

#### 5. Qurilmani o'chirish
```
DELETE /api/v1/devices/{device_id}/
```
**Header:**
```
Authorization: Bearer {access_token}
```

#### 6. Qulfni ochish
```
POST /api/v1/devices/{device_id}/unlock/
```
**Header:**
```
Authorization: Bearer {access_token}
```
**Jo'natish:**
```json
{
  "duration": 5
}
```
`duration` - necha soniya ochiq turishi (1 dan 30 gacha)

#### 7. Qulfni yopish
```
POST /api/v1/devices/{device_id}/lock/
```
**Header:**
```
Authorization: Bearer {access_token}
```

#### 8. Qurilma holati
```
GET /api/v1/devices/{device_id}/status/
```
**Header:**
```
Authorization: Bearer {access_token}
```

#### 9. Tarix (Loglar)
```
GET /api/v1/devices/{device_id}/logs/
```
**Header:**
```
Authorization: Bearer {access_token}
```

**Javob misoli:**
```json
{
  "success": true,
  "data": [
    {
      "id": "...",
      "user": {
        "email": "user@example.com",
        "first_name": "Ism",
        "last_name": "Familiya"
      },
      "event_type": "UNLOCK_APP",
      "description": "Mobil ilova orqali ochildi",
      "created_at": "2024-01-15 10:30:00",
      "success": true
    }
  ]
}
```

---

## 📱 Postman'da qanday test qilish

### 1-qadam: Register (Ro'yxatdan o'tish)
1. Postman oching
2. Yangi request yarating
3. **POST** ni tanlang
4. URL: `http://localhost:8000/api/v1/auth/register/`
5. **Body** → **raw** → **JSON** tanlang
6. JSON kodini yozing va **Send** bosing

### 2-qadam: Login qilish
1. **POST** `http://localhost:8000/api/v1/auth/login/`
2. Body'ga email va parol yozing
3. **Send** bosing
4. Javobdan **access** tokenni nusxalang (copy qiling)

### 3-qadam: Tokenli so'rov yuborish
1. Yangi request yarating
2. **Headers** bo'limiga o'ting
3. Key: `Authorization`
4. Value: `Bearer {access_token}` (tokenni qo'ying)
5. **Send** bosing

---

## 🔑 Muhim tushunchalar

### Token nima?
Token - bu sizning ruxsatnomangiz. Kirganingizdan keyin olasiz va har bir so'rovda jo'natasiz.

**2 xil token bor:**
- **access token** - 15 daqiqa ishlaydi, har bir so'rovda kerak
- **refresh token** - 7 kun ishlaydi, yangi access token olish uchun

### Header nima?
Header - bu qo'shimcha ma'lumot. Tokenni shu yerda jo'natasiz.

**Misol:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### HTTP metodlari

| Metod | Vazifasi | Misol |
|-------|----------|-------|
| **GET** | Ma'lumot olish | Barcha qurilmalarni ko'rish |
| **POST** | Yangi yaratish | Yangi qurilma qo'shish |
| **PATCH** | O'zgartirish | Profilni yangilash |
| **PUT** | To'liq o'zgartirish | Barcha ma'lumotni yangilash |
| **DELETE** | O'chirish | Qurilmani o'chirish |

### Status kodlar

| Kod | Ma'nosi | Qachon |
|-----|---------|--------|
| **200** | OK | Hammasi yaxshi |
| **201** | Created | Yangi narsa yaratildi |
| **400** | Bad Request | Xato ma'lumot jo'natdingiz |
| **401** | Unauthorized | Token yo'q yoki noto'g'ri |
| **403** | Forbidden | Ruxsat yo'q |
| **404** | Not Found | Topilmadi |
| **500** | Server Error | Server xatosi |

---

## 🛠️ Boshqaruv buyruqlari

### Serverni boshqarish
```bash
./start.sh      # Ishga tushirish
./stop.sh       # To'xtatish
./restart.sh    # Qayta ishga tushirish
./logs.sh       # Loglarni ko'rish
./logs.sh web   # Faqat web loglar
```

### Docker buyruqlari
```bash
docker-compose ps              # Holatni ko'rish
docker-compose logs web        # Web loglarni ko'rish
docker-compose restart web     # Web'ni qayta ishga tushirish
```

### Ma'lumotlar bazasini tozalash
```bash
docker-compose down -v         # Hamma narsani o'chirish
./start.sh                     # Qaytadan ishga tushirish
```

---

## 📝 Amaliy misollar

### Misol 1: Yangi foydalanuvchi yaratish

**1. Register:**
```bash
POST http://localhost:8000/api/v1/auth/register/

{
  "email": "aziz@example.com",
  "password": "Aziz12345!",
  "password_confirm": "Aziz12345!",
  "first_name": "Aziz",
  "last_name": "Ahmadov",
  "phone": "+998901234567"
}
```

**2. Login:**
```bash
POST http://localhost:8000/api/v1/auth/login/

{
  "email": "aziz@example.com",
  "password": "Aziz12345!"
}
```

**3. Tokenni saqlang:**
```
access_token = "eyJhbGc..."
```

### Misol 2: Qurilma qo'shish va boshqarish

**1. Qurilma qo'shish:**
```bash
POST http://localhost:8000/api/v1/devices/
Header: Authorization: Bearer {token}

{
  "device_id": "LOCK-001",
  "name": "Ofis eshigi",
  "device_type": "DOOR_LOCK",
  "location": "Toshkent, Amir Temur ko'chasi"
}
```

**2. Qulfni ochish:**
```bash
POST http://localhost:8000/api/v1/devices/{device_id}/unlock/
Header: Authorization: Bearer {token}

{
  "duration": 10
}
```

**3. Tarixni ko'rish:**
```bash
GET http://localhost:8000/api/v1/devices/{device_id}/logs/
Header: Authorization: Bearer {token}
```

---

## ❓ Tez-tez beriladigan savollar

### 1. Token nima uchun ishlamayapti?
**Javob:** Token 15 daqiqadan keyin eskiradi. Yangi token oling (login qiling).

### 2. "401 Unauthorized" xatosi
**Javob:**
- Tokenni to'g'ri qo'ydingizmi? `Bearer` so'zini yozmadingizmi?
- Token eskirgan bo'lishi mumkin, qayta login qiling

### 3. "400 Bad Request" xatosi
**Javob:**
- JSON formatini tekshiring
- Majburiy maydonlarni to'ldirdingizmi?
- Email formati to'g'rimi?

### 4. Parol qanday bo'lishi kerak?
**Javob:**
- Kamida 8 ta belgi
- Katta harf bo'lishi kerak (A-Z)
- Kichik harf bo'lishi kerak (a-z)
- Raqam bo'lishi kerak (0-9)
- Maxsus belgi bo'lishi kerak (!@#$%^&*)

**To'g'ri:** `Parol123!`, `MyPass456#`, `Secure789$`
**Noto'g'ri:** `parol`, `12345678`, `password`

### 5. Serverni qanday to'xtataman?
```bash
./stop.sh
```

### 6. Ma'lumotlar bazasini qanday tozalayman?
```bash
docker-compose down -v
./start.sh
```

---

## 🎯 Test uchun ketma-ketlik

Ushbu tartibda test qiling:

1. ✅ **Register** - Yangi foydalanuvchi yaratish
2. ✅ **Login** - Tizimga kirish, token olish
3. ✅ **Get Profile** - Profilni ko'rish
4. ✅ **Update Profile** - Profilni o'zgartirish
5. ✅ **Create Device** - Qurilma qo'shish
6. ✅ **List Devices** - Barcha qurilmalarni ko'rish
7. ✅ **Unlock Device** - Qulfni ochish
8. ✅ **Lock Device** - Qulfni yopish
9. ✅ **Device Logs** - Tarixni ko'rish
10. ✅ **Change Password** - Parolni o'zgartirish
11. ✅ **Logout** - Chiqish

---

## 📞 Yordam

- **API hujjatlar:** http://localhost:8000/api/docs/
- **Admin panel:** http://localhost:8000/admin/
- **Postman testlar:** `POSTMAN_TESTS_USERS.md` faylini oching

---

## 💡 Maslahatlar

1. **Har doim tokenni tekshiring** - Eskirgan bo'lishi mumkin
2. **JSON formatini tekshiring** - Vergul va qavs xatolarini ko'ring
3. **Status kodlarni o'rganing** - 200 = yaxshi, 400 = xato, 401 = token xato
4. **Loglarni ko'ring** - `./logs.sh web` buyrug'i bilan
5. **Postman Collection yarating** - Barcha so'rovlarni bir joyda saqlang

---

**Omad tilaymiz! Savollar bo'lsa telegram yoki email orqali yozing.**

**Yaratilgan:** 2024
**Versiya:** 1.0.0
