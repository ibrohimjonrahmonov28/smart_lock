# SmartLock API - Intern uchun oddiy qo'llanma

Salom! Bu qo'llanma sizga API'larni Postman orqali test qilishni o'rgatadi.
Siz faqat API'larni test qilasiz, backend kodi bilan ishlamasligingiz kerak.

---

## 📱 Postman nima?

Postman - bu API'larni test qilish uchun dastur. Siz bu yerda serverga so'rov yuborasiz va javobni ko'rasiz.

**Yuklab olish:** https://www.postman.com/downloads/

---

## 🎯 Sizning vazifangiz

Siz faqat **API'larni test qilasiz**:
1. Postman ochib so'rov yuborasiz
2. Javobni tekshirasiz
3. Xatolar bo'lsa - screenshot qilasiz va xabar berasiz

**Esda tuting:** Backend kod bilan ishlamasligingiz kerak. Faqat API test!

---

## 🚀 Boshlash

### 1. Serverni ishga tushirish

Terminal ochib:
```bash
cd /Users/macbookpro/Desktop/smartlock_backend
./start.sh
```

10-15 soniya kutasiz. Server tayyor bo'lganda bu manzillar ochiladi:
- API: http://localhost:8000/api/
- Hujjatlar: http://localhost:8000/api/docs/

### 2. Login qilish

**Admin akkaunt:**
```
Email: admin@smartlock.com
Parol: admin
```

---

## 📋 Test ro'yxati - Users (Foydalanuvchilar)

Quyidagi tartibda test qiling va har birini belgilang ✅

### ✅ Test 1: Register (Ro'yxatdan o'tish)

**1. Postman'ni oching**

**2. Yangi request yarating:**
- Click: "New" → "HTTP Request"
- Method: **POST** (pastga tushadigan menyudan tanlang)
- URL: `http://localhost:8000/api/v1/auth/register/`

**3. Body sozlang:**
- **Body** tab'ga o'ting
- **raw** ni tanlang
- **JSON** ni tanlang (Text o'rniga)

**4. Ushbu kodni kiriting:**
```json
{
  "email": "intern1@example.com",
  "password": "Test12345!",
  "password_confirm": "Test12345!",
  "first_name": "Intern",
  "last_name": "Developer",
  "phone": "+998901234567"
}
```

**5. Send bosing**

**6. Natijani tekshiring:**
- Status: **201 Created** bo'lishi kerak
- Javobda `"success": true` bo'lishi kerak
- `tokens` bo'lishi kerak (access va refresh)

**7. Token'ni saqlang:**
- Javobdan `access` tokenni nusxalang (Ctrl+C)
- Biror joyga yozib qo'ying (keyin kerak bo'ladi)

---

### ✅ Test 2: Login (Kirish)

**1. Yangi request:**
- Method: **POST**
- URL: `http://localhost:8000/api/v1/auth/login/`

**2. Body:**
```json
{
  "email": "admin@smartlock.com",
  "password": "admin"
}
```

**3. Send bosing**

**4. Tekshiring:**
- Status: **200 OK**
- `"success": true`
- `tokens` bo'lishi kerak

**5. Access token'ni nusxalang va saqlang!**

---

### ✅ Test 3: Get Profile (Profilni ko'rish)

**DIQQAT:** Endi har bir requestda token kerak!

**1. Yangi request:**
- Method: **GET**
- URL: `http://localhost:8000/api/v1/auth/profile/`

**2. Token qo'shish (MUHIM!):**
- **Headers** tab'ga o'ting
- Key: `Authorization`
- Value: `Bearer ` (so'ngiga bitta bo'sh joy qoldiring va tokenni qo'ying)
- Masalan: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**3. Send bosing**

**4. Tekshiring:**
- Status: **200 OK**
- Sizning ma'lumotlaringiz ko'rinishi kerak

---

### ✅ Test 4: Update Profile (Profilni yangilash)

**1. Yangi request:**
- Method: **PATCH**
- URL: `http://localhost:8000/api/v1/auth/profile/`

**2. Headers:**
```
Authorization: Bearer {sizning_tokeningiz}
```

**3. Body:**
```json
{
  "first_name": "Yangi Ism",
  "last_name": "Yangi Familiya"
}
```

**4. Send → Tekshiring:**
- Status: **200 OK**
- Yangi ma'lumotlar ko'rinishi kerak

---

### ✅ Test 5: Change Password (Parolni o'zgartirish)

**1. Request:**
- Method: **POST**
- URL: `http://localhost:8000/api/v1/auth/change-password/`

**2. Headers:**
```
Authorization: Bearer {token}
```

**3. Body:**
```json
{
  "old_password": "admin",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}
```

**4. Send → Tekshiring:**
- Status: **200 OK**
- `"message": "Password changed successfully"`

**DIQQAT:** Parolni o'zgartirsangiz, qayta login qiling!

---

### ✅ Test 6: Refresh Token (Tokenni yangilash)

**1. Request:**
- Method: **POST**
- URL: `http://localhost:8000/api/v1/auth/token/refresh/`

**2. Body:**
```json
{
  "refresh": "{refresh_token}"
}
```

**3. Send → Tekshiring:**
- Status: **200 OK**
- Yangi `access` token olasiz

---

### ✅ Test 7: Logout (Chiqish)

**1. Request:**
- Method: **POST**
- URL: `http://localhost:8000/api/v1/auth/logout/`

**2. Headers:**
```
Authorization: Bearer {token}
```

**3. Body:**
```json
{
  "refresh": "{refresh_token}"
}
```

**4. Send → Tekshiring:**
- Status: **200 OK**
- `"message": "Logout successful"`

---

## 📝 Natijalarni qayd qilish

Har bir test uchun:

### To'g'ri natija:
✅ Status kod to'g'ri (200, 201)
✅ `"success": true`
✅ Kutilgan ma'lumotlar bor

Screenshot oling va "Test X - To'g'ri" deb yozing.

### Xato bo'lsa:
❌ Status kod xato (400, 401, 500)
❌ `"success": false` yoki xato xabari

Screenshot oling va quyidagilarni yozing:
1. Test raqami
2. Status kod
3. Xato xabari (error message)
4. Siz nima qildingiz

---

## 🔴 Tez-tez uchraydigan xatolar

### Xato 1: "401 Unauthorized"
**Sabab:** Token noto'g'ri yoki yo'q

**Hal qilish:**
1. Token'ni tekshiring
2. `Bearer ` so'zini yozib, bo'sh joy qoldirgansizmi?
3. Token eskirgan bo'lishi mumkin - qayta login qiling

### Xato 2: "400 Bad Request"
**Sabab:** Ma'lumot noto'g'ri

**Hal qilish:**
1. JSON formatini tekshiring (vergullar, qavs)
2. Email formatini tekshiring
3. Parol talablariga javob beradimi? (8+ ta belgi, katta-kichik harf, raqam, maxsus belgi)

### Xato 3: "404 Not Found"
**Sabab:** URL noto'g'ri

**Hal qilish:**
1. URL'ni qaytadan tekshiring
2. Oxirida `/` bormi?
3. `localhost:8000` ishlaydimi?

### Xato 4: "Connection refused"
**Sabab:** Server ishlamayapti

**Hal qilish:**
```bash
./start.sh
```
va 15 soniya kuting.

---

## 📊 Test natijalarini yuboring

Barcha testlarni yakunlab:

**Excel yoki Google Sheets yarating:**

| # | Test nomi | Status | Natija | Screenshot | Izoh |
|---|-----------|--------|--------|------------|------|
| 1 | Register | ✅ | 201 Created | ✅ | To'g'ri ishladi |
| 2 | Login | ✅ | 200 OK | ✅ | Token olindi |
| 3 | Get Profile | ✅ | 200 OK | ✅ | Ma'lumot ko'rsatildi |
| ... | ... | ... | ... | ... | ... |

---

## 💡 Postman maslahatlar

### 1. Environment yarating
- Postman'da: Environments → Add
- Nom: `SmartLock Dev`
- Variables:
  - `base_url` = `http://localhost:8000/api/v1`
  - `access_token` = `(login'dan keyin to'ldiring)`

Keyin URL: `{{base_url}}/auth/login/`

### 2. Collection yarating
- Barcha requestlarni bitta Collection'ga qo'ying
- Nom: `SmartLock Tests`
- Har bir requestni nomlab saqlang

### 3. Tests tab'dan foydalaning
Lekin bu keyin, hozircha oddiy test kifoya.

---

## 🎓 Status kodlar jadvali

| Kod | Nomi | Ma'nosi | Qachon |
|-----|------|---------|--------|
| 200 | OK | To'g'ri | GET, PATCH muvaffaqiyatli |
| 201 | Created | Yaratildi | POST muvaffaqiyatli (yangi narsa) |
| 204 | No Content | Kontent yo'q | DELETE muvaffaqiyatli |
| 400 | Bad Request | Xato so'rov | Ma'lumot noto'g'ri |
| 401 | Unauthorized | Ruxsat yo'q | Token yo'q/xato |
| 403 | Forbidden | Man etilgan | Huquq yetarli emas |
| 404 | Not Found | Topilmadi | URL xato |
| 500 | Server Error | Server xatosi | Backend muammo |

---

## ✅ Yakuniy checklist

Test boshlanishidan oldin:
- [ ] Postman o'rnatilganmi?
- [ ] Server ishlaydimi? (localhost:8000)
- [ ] Admin login ma'lumotlari bormi?
- [ ] Excel/Google Sheets tayyormi?
- [ ] Screenshot olish bilasizmi?

Test jarayonida:
- [ ] Har bir requestni ketma-ket test qilasiz
- [ ] Token'ni saqlaydiz
- [ ] Natijalarni yozib borasiz
- [ ] Screenshot olasiz
- [ ] Xatolarni batafsil yozasiz

Test tugagach:
- [ ] Barcha 7 ta test bajarildi
- [ ] Excel to'ldirildi
- [ ] Screenshotlar yig'ildi
- [ ] Xabar berdingiz

---

## 📞 Yordam kerakmi?

Agar tushunmagan bo'lsangiz:
1. Telegram/Email orqali so'rang
2. Qaysi test tushunarsiz bo'lsa - raqamini ayting
3. Screenshot yuboring

**MUHIM:** Backend kodga tegmang! Faqat Postman'da test qiling.

---

**Omad! Testni boshlang! 🚀**
