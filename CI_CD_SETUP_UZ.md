# GitHub CI/CD - Avtomatik Deploy qo'llanma

Bu qo'llanma orqali siz local PC'da kod yozib GitHub'ga push qilganingizda avtomatik ravishda server'da deploy bo'ladi.

---

## 🎯 Bu nima beradi?

✅ Local'da kod yozdingiz → Git push qildingiz → Server avtomatik yangilanadi
✅ Qo'lda server'ga kirib deploy qilish kerak emas
✅ Xatolar bo'lsa GitHub'da ko'rasiz
✅ Deploy tarixi saqlanadi

---

## 📋 Boshlashdan oldin kerakli narsalar

1. ✅ GitHub akkaunt
2. ✅ Google VM yoki boshqa server (Ubuntu)
3. ✅ Server'da Docker o'rnatilgan
4. ✅ Server'da SSH access

---

## 🔧 1-qadam: Server'ni tayyorlash

### Server'ga kirish:
```bash
ssh username@your-server-ip
```

### Docker o'rnatish (agar yo'q bo'lsa):
```bash
# Docker o'rnatish
sudo apt update
sudo apt install docker.io docker-compose -y

# Docker'ni ishga tushirish
sudo systemctl start docker
sudo systemctl enable docker

# User'ni Docker group'ga qo'shish
sudo usermod -aG docker $USER

# Logout va qayta login qiling
exit
ssh username@your-server-ip
```

### Loyihani server'ga joylashtirish:
```bash
# Home papkaga o'tish
cd ~

# GitHub'dan clone qilish
git clone https://github.com/your-username/smartlock_backend.git
cd smartlock_backend

# .env faylni yaratish
nano .env
```

**.env faylni to'ldiring (Production uchun):**
```bash
# Django
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=50_TA_TASODIFIY_BELGI_YOZING_BU_YERGA
ALLOWED_HOSTS=your-domain.com,your-server-ip

# Database
DB_NAME=smartlock_db
DB_USER=postgres
DB_PASSWORD=KUCHLI_PAROL_YOZING
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT
ACCESS_TOKEN_LIFETIME_MINUTES=15
REFRESH_TOKEN_LIFETIME_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=https://your-app.com
```

### Docker'da ishga tushirish:
```bash
chmod +x start.sh stop.sh restart.sh logs.sh
./start.sh
```

---

## 🔑 2-qadam: SSH Key yaratish

Server'da SSH key yaratamiz va GitHub'ga qo'shamiz.

### Local PC'da SSH key yaratish:
```bash
# SSH key yaratish
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Key'ni ko'rish
cat ~/.ssh/id_rsa
```

**MUHIM:** Bu private key'ni copy qiling! Keyinroq GitHub Secrets'ga qo'yasiz.

### Public key'ni server'ga qo'shish:
```bash
# Public key'ni ko'rish
cat ~/.ssh/id_rsa.pub

# Server'ga kirish
ssh username@your-server-ip

# Authorized keys'ga qo'shish
nano ~/.ssh/authorized_keys
# Public key'ni bu yerga paste qiling
```

---

## 🐙 3-qadam: GitHub Repository sozlash

### 3.1 Repository yaratish

1. GitHub'ga kiring: https://github.com
2. Yangi repository yarating: **smartlock_backend**
3. Public yoki Private tanlang

### 3.2 Local kodingizni GitHub'ga push qilish

```bash
# Local PC'da loyiha papkasiga o'ting
cd /Users/macbookpro/Desktop/smartlock_backend

# Git init (agar qilmagan bo'lsangiz)
git init

# .gitignore tekshirish
cat .gitignore

# Hamma narsani qo'shish
git add .

# Commit qilish
git commit -m "Initial commit - SmartLock Backend"

# Remote qo'shish
git remote add origin https://github.com/your-username/smartlock_backend.git

# Push qilish
git branch -M main
git push -u origin main
```

---

## 🔐 4-qadam: GitHub Secrets sozlash

GitHub'da repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Qo'shiladigan secretlar:

| Secret nomi | Qiymati | Qayerdan olish |
|-------------|---------|----------------|
| `SERVER_HOST` | `your-server-ip` yoki `your-domain.com` | Server IP manzili |
| `SERVER_USERNAME` | `ubuntu` yoki `root` | SSH username |
| `SSH_PRIVATE_KEY` | Private SSH key | `cat ~/.ssh/id_rsa` |
| `SERVER_PORT` | `22` | SSH port (odatda 22) |

### Qanday qo'shish:

1. **SERVER_HOST:**
   - Name: `SERVER_HOST`
   - Value: `123.45.67.89` (server IP)

2. **SERVER_USERNAME:**
   - Name: `SERVER_USERNAME`
   - Value: `ubuntu` (yoki sizning username)

3. **SSH_PRIVATE_KEY:**
   - Name: `SSH_PRIVATE_KEY`
   - Value: Private key'ning to'liq mazmuni
   ```
   -----BEGIN RSA PRIVATE KEY-----
   ... butun key ...
   -----END RSA PRIVATE KEY-----
   ```

4. **SERVER_PORT:**
   - Name: `SERVER_PORT`
   - Value: `22`

---

## ✅ 5-qadam: Test qilish

### Birinchi deploy:

```bash
# Local PC'da
cd /Users/macbookpro/Desktop/smartlock_backend

# Biror o'zgarish qiling (masalan, README'ni o'zgartiring)
echo "# Test" >> README.md

# Commit va push
git add .
git commit -m "Test: CI/CD setup"
git push origin main
```

### GitHub'da kuzatish:

1. GitHub repository'ga o'ting
2. **Actions** tab'ga o'ting
3. "Deploy to Production" workflow'ni ko'ring
4. Yashil galochka ✅ - Success
5. Qizil X ❌ - Error (loglarni o'qing)

---

## 🔄 Qanday ishlaydi?

```
┌─────────────────────────────────────────────────────┐
│  1. Siz local'da kod yozasiz                       │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  2. Git commit va push qilasiz                     │
│     git add .                                       │
│     git commit -m "Yangi feature"                   │
│     git push origin main                            │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  3. GitHub Actions ishga tushadi                   │
│     (.github/workflows/deploy.yml)                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  4. Server'ga SSH orqali ulanadi                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  5. Yangi kodni git pull qiladi                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  6. Docker container'larni rebuild qiladi          │
│     docker-compose down                             │
│     docker-compose build                            │
│     docker-compose up -d                            │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  7. Migration va collectstatic ishlatadi           │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  8. ✅ Deploy tugadi! Server yangilandi!          │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Kundalik ishlatish

### Har kuni ishlaganingizda:

```bash
# 1. Kod yozasiz (VS Code'da)

# 2. Testni local'da qilasiz
./start.sh
# API test qilish: http://localhost:8000/api/

# 3. Git'ga commit qilasiz
git add .
git commit -m "Fix: Bug in login API"
git push origin main

# 4. GitHub Actions'da kuzatasiz
# https://github.com/your-username/smartlock_backend/actions

# 5. Server'da yangilangan kodingizni ko'rasiz
# https://api.yourdomain.com/health/
```

---

## 🐛 Xatolarni hal qilish

### Xato 1: "Permission denied (publickey)"

**Sabab:** SSH key noto'g'ri

**Hal qilish:**
1. Private key'ni to'g'ri copy qilganingizni tekshiring
2. GitHub Secrets'da `SSH_PRIVATE_KEY` to'g'ri bo'lishi kerak
3. Butun key boshidan oxirigacha copy qiling:
   ```
   -----BEGIN RSA PRIVATE KEY-----
   ...
   -----END RSA PRIVATE KEY-----
   ```

### Xato 2: "Could not resolve hostname"

**Sabab:** Server IP noto'g'ri

**Hal qilish:**
1. `SERVER_HOST` secret'ni tekshiring
2. Server IP to'g'rimi?
3. Ping qilib ko'ring: `ping your-server-ip`

### Xato 3: "git pull failed"

**Sabab:** Server'da git repository yo'q yoki noto'g'ri

**Hal qilish:**
```bash
# Server'ga kirish
ssh username@your-server-ip

# Papka bormi tekshirish
cd ~/smartlock_backend
git status

# Agar yo'q bo'lsa, qayta clone qiling
cd ~
rm -rf smartlock_backend
git clone https://github.com/your-username/smartlock_backend.git
```

### Xato 4: Docker container ishlamayapti

**Sabab:** Docker xatosi yoki .env yo'q

**Hal qilish:**
```bash
# Server'da loglarni ko'ring
cd ~/smartlock_backend
docker-compose logs

# Container'larni qayta ishga tushiring
docker-compose down
docker-compose up -d

# .env faylni tekshiring
cat .env
```

---

## 🎨 Workflow'ni sozlash

### Faqat ma'lum branchlar uchun:

`.github/workflows/deploy.yml` faylida:

```yaml
on:
  push:
    branches:
      - main        # Faqat main
      - production  # Yoki production branch
```

### Pull request uchun ham:

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

### Faqat ma'lum fayllar o'zgarganda:

```yaml
on:
  push:
    branches: [main]
    paths:
      - 'apps/**'
      - 'config/**'
      - 'requirements.txt'
      - 'docker-compose.yml'
```

---

## 📊 Deploy tarixini ko'rish

1. GitHub repository → **Actions**
2. Barcha deploy'larni ko'rasiz
3. Har birini bosib detalni ko'rasiz
4. Loglarni o'qiysiz

---

## 🔒 Xavfsizlik

### MUHIM:

1. ❌ `.env` faylini GitHub'ga push qilmang!
2. ❌ Private key'ni GitHub'ga commit qilmang!
3. ✅ Faqat GitHub Secrets'da saqlang
4. ✅ `.gitignore` faylda `.env` borligini tekshiring

### .gitignore tekshirish:

```bash
cat .gitignore
```

Quyidagilar bo'lishi kerak:
```
.env
.env.*
*.pem
*.key
id_rsa*
```

---

## 🚀 Qo'shimcha CI/CD features

### Avtomatik test qo'shish:

`.github/workflows/deploy.yml` ga qo'shing:

```yaml
- name: Run Tests
  run: |
    docker-compose exec -T web python manage.py test
```

### Slack/Telegram notification:

Deploy tugaganda xabar yuborish uchun:

```yaml
- name: Send Telegram notification
  if: success()
  run: |
    curl -X POST \
      https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage \
      -d chat_id=${{ secrets.TELEGRAM_CHAT_ID }} \
      -d text="✅ Deploy successful!"
```

---

## ✅ Checklist

Deploy qilishdan oldin:

- [ ] Server tayyormi?
- [ ] Docker o'rnatilganmi?
- [ ] SSH key yaratilganmi?
- [ ] GitHub repository yaratilganmi?
- [ ] GitHub Secrets to'ldirilganmi?
- [ ] `.github/workflows/deploy.yml` fayli bormi?
- [ ] `.gitignore` to'g'rimi?
- [ ] `.env` fayli server'da bormi?

---

## 📞 Yordam

Agar muammo bo'lsa:

1. GitHub Actions log'larini o'qing
2. Server loglarini tekshiring: `./logs.sh`
3. Docker statusini ko'ring: `docker-compose ps`

---

**Tayyor! Endi har safar kod push qilsangiz avtomatik deploy bo'ladi! 🎉**

**Omad tilaymiz! 🚀**
