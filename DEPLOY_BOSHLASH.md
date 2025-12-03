# 🚀 Deploy - Qisqacha boshlash

Bu fayl sizga 15 daqiqada CI/CD sozlashni o'rgatadi.

---

## ⚡ Tez boshlash (3 qadam)

### 1️⃣ GitHub'ga push qiling

```bash
cd /Users/macbookpro/Desktop/smartlock_backend

# GitHub repository yarating: https://github.com/new
# Keyin:

git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/smartlock_backend.git
git push -u origin main
```

### 2️⃣ GitHub Secrets qo'shing

GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret | Qiymat | Misol |
|--------|--------|-------|
| `SERVER_HOST` | Server IP | `123.45.67.89` |
| `SERVER_USERNAME` | SSH user | `ubuntu` |
| `SSH_PRIVATE_KEY` | Private SSH key | `cat ~/.ssh/id_rsa` |
| `SERVER_PORT` | SSH port | `22` |

### 3️⃣ Server'ni tayyorla

```bash
# Server'ga kiring
ssh ubuntu@YOUR-SERVER-IP

# Loyihani clone qiling
cd ~
git clone https://github.com/YOUR-USERNAME/smartlock_backend.git
cd smartlock_backend

# .env yarating
cp .env .env.production
nano .env.production
# To'ldiring: SECRET_KEY, ALLOWED_HOSTS, DB_PASSWORD

# Ishga tushiring
./start.sh
```

---

## ✅ Test qiling

```bash
# Local'da o'zgarish qiling
echo "# Test" >> README.md

# Push qiling
git add .
git commit -m "Test CI/CD"
git push origin main

# GitHub'da kuzating
# https://github.com/YOUR-USERNAME/smartlock_backend/actions
```

---

## 📚 To'liq qo'llanma

Batafsil ma'lumot uchun: [CI_CD_SETUP_UZ.md](CI_CD_SETUP_UZ.md)

---

## 🆘 Yordam kerakmi?

1. GitHub Actions log'larini o'qing
2. [CI_CD_SETUP_UZ.md](CI_CD_SETUP_UZ.md) - Xatolarni hal qilish bo'limiga o'ting
3. Server loglarini tekshiring: `./logs.sh`

**Omad! 🎉**
