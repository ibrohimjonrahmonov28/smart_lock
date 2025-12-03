# Postman API Tests - Users App

Base URL: `http://localhost:8000/api/v1/auth`

---

## 1. User Registration (POST)

**Endpoint:** `POST /api/v1/auth/register/`

**Description:** Create a new user account

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "email": "testuser@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "uuid-here",
      "email": "testuser@example.com",
      "phone": "+1234567890",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "is_active": true,
      "email_verified": false,
      "phone_verified": false,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

**Save from Response:**
- `data.tokens.access` → Save as Postman variable `access_token`
- `data.tokens.refresh` → Save as Postman variable `refresh_token`
- `data.user.id` → Save as `user_id`

---

## 2. User Login (POST)

**Endpoint:** `POST /api/v1/auth/login/`

**Description:** Login with email and password

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "email": "testuser@example.com",
  "password": "SecurePass123!"
}
```

**Alternative - Test with Admin:**
```json
{
  "email": "admin@smartlock.com",
  "password": "admin"
}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "uuid-here",
      "email": "testuser@example.com",
      "phone": "+1234567890",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "is_active": true,
      "email_verified": false,
      "phone_verified": false,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

**Save from Response:**
- `data.tokens.access` → Save as `access_token`
- `data.tokens.refresh` → Save as `refresh_token`

---

## 3. Get User Profile (GET)

**Endpoint:** `GET /api/v1/auth/profile/`

**Description:** Get current user's profile

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "email": "testuser@example.com",
    "phone": "+1234567890",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "is_active": true,
    "email_verified": false,
    "phone_verified": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

---

## 4. Update User Profile (PATCH)

**Endpoint:** `PATCH /api/v1/auth/profile/`

**Description:** Update user profile information

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Body (raw JSON):**
```json
{
  "first_name": "Jonathan",
  "last_name": "Smith",
  "phone": "+9876543210"
}
```

**Partial Update Example (only first name):**
```json
{
  "first_name": "Jonathan"
}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "id": "uuid-here",
    "email": "testuser@example.com",
    "phone": "+9876543210",
    "first_name": "Jonathan",
    "last_name": "Smith",
    "full_name": "Jonathan Smith",
    "is_active": true,
    "email_verified": false,
    "phone_verified": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:45:00Z"
  }
}
```

---

## 5. Change Password (POST)

**Endpoint:** `POST /api/v1/auth/change-password/`

**Description:** Change user password

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Body (raw JSON):**
```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

## 6. Refresh Token (POST)

**Endpoint:** `POST /api/v1/auth/token/refresh/`

**Description:** Get new access token using refresh token

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "refresh": "{{refresh_token}}"
}
```

**Expected Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Save from Response:**
- `access` → Update `access_token`

---

## 7. User Logout (POST)

**Endpoint:** `POST /api/v1/auth/logout/`

**Description:** Logout and blacklist refresh token

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Body (raw JSON):**
```json
{
  "refresh": "{{refresh_token}}"
}
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

## Testing Sequence (Recommended Order)

1. **Register** → Save tokens
2. **Login** → Save new tokens
3. **Get Profile** → Verify user data
4. **Update Profile** → Verify changes
5. **Get Profile Again** → Confirm updates
6. **Change Password** → Update password
7. **Login with New Password** → Verify password changed
8. **Refresh Token** → Test token refresh
9. **Logout** → Blacklist token

---

## Error Scenarios to Test

### 1. Register with Existing Email
```json
{
  "email": "admin@smartlock.com",
  "password": "Test123!",
  "password_confirm": "Test123!",
  "first_name": "Test",
  "last_name": "User"
}
```
**Expected:** 400 Bad Request - Email already exists

### 2. Register with Password Mismatch
```json
{
  "email": "newuser@example.com",
  "password": "Test123!",
  "password_confirm": "Different123!",
  "first_name": "Test",
  "last_name": "User"
}
```
**Expected:** 400 Bad Request - Passwords do not match

### 3. Login with Wrong Password
```json
{
  "email": "testuser@example.com",
  "password": "WrongPassword123!"
}
```
**Expected:** 400 Bad Request - Invalid credentials

### 4. Access Profile Without Token
**Headers:** No Authorization header
**Expected:** 401 Unauthorized

### 5. Change Password with Wrong Old Password
```json
{
  "old_password": "WrongOldPass123!",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}
```
**Expected:** 400 Bad Request - Incorrect old password

---

## Postman Environment Variables Setup

Create environment with these variables:

| Variable Name | Initial Value | Current Value |
|--------------|---------------|---------------|
| base_url | http://localhost:8000/api/v1 | |
| access_token | | (auto-filled after login) |
| refresh_token | | (auto-filled after login) |
| user_id | | (auto-filled after register) |

---

## Quick Copy-Paste for Postman

### Register Request
```
POST http://localhost:8000/api/v1/auth/register/
Content-Type: application/json

{
  "email": "testuser@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

### Login Request
```
POST http://localhost:8000/api/v1/auth/login/
Content-Type: application/json

{
  "email": "testuser@example.com",
  "password": "SecurePass123!"
}
```

### Get Profile Request
```
GET http://localhost:8000/api/v1/auth/profile/
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

## Status Codes Reference

- **200 OK** - Request successful
- **201 Created** - User created successfully
- **400 Bad Request** - Validation error
- **401 Unauthorized** - Missing or invalid token
- **403 Forbidden** - No permission
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

---

## Notes

1. All authenticated requests require `Authorization: Bearer {access_token}` header
2. Tokens expire after configured time (default: 15 minutes for access, 7 days for refresh)
3. Use refresh token to get new access token without logging in again
4. After logout, both tokens are blacklisted and cannot be used
5. Password must contain: uppercase, lowercase, numbers, special characters (min 8 chars)

---

**Ready to Test!** Start with registration, then proceed through the sequence.
