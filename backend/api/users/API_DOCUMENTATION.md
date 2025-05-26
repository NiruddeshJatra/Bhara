# Vara User Authentication API Documentation

## Overview
This document provides comprehensive documentation for the Vara User Authentication API. The API is built using Django REST Framework and implements JWT-based authentication.

## Base URL
- Development: `http://localhost:8000`
- Production: `[Your Production URL]`

## Authentication
The API uses JWT (JSON Web Token) authentication. Most endpoints require an `Authorization` header with a Bearer token:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### 1. User Registration
**Endpoint:** `POST /auth/signup/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "username": "username",
  "marketing_consent": true
}
```

**Response (201 Created):**
```json
{
  "email": "user@example.com",
  "username": "username",
  "marketing_consent": true
}
```

**Validation Rules:**
- Email must be unique and valid
- Password must be at least 8 characters with uppercase, lowercase, number, and special character
- Username must be unique and contain only letters, numbers, and underscores
- Marketing consent is optional (defaults to false)

### 2. Email Verification
**Endpoint:** `GET /auth/signup/verify/?code=<verification_code>`

**Response (200 OK):**
```json
{
  "message": "Email verified successfully"
}
```

### 3. User Login
**Endpoint:** `POST /auth/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### 4. Password Reset Flow

#### 4.1 Request Password Reset
**Endpoint:** `POST /auth/password/reset/`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset email sent"
}
```

#### 4.2 Verify Password Reset Code
**Endpoint:** `GET /auth/password/reset/verify/?code=<reset_code>`

**Response (200 OK):**
```json
{
  "message": "Password reset code is valid"
}
```

#### 4.3 Reset Password
**Endpoint:** `POST /auth/password/reset/verified/`

**Request Body:**
```json
{
  "code": "<reset_code>",
  "password": "NewSecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successful"
}
```

#### 4.4 Change Password (When Logged In)
**Endpoint:** `POST /auth/password/change/`

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "password": "NewSecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

### 5. Get User Profile
**Endpoint:** `GET /auth/profile/`

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "profile_picture": "http://example.com/media/profile_pictures/user.jpg",
  "bio": "User bio",
  "location": "City, Country",
  "national_id": "1234567890",
  "marketing_consent": true,
  "profile_completed": true
}
```

### 6. Update Profile
**Endpoint:** `PATCH /auth/profile/`

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "bio": "Updated bio",
  "location": "New City, Country"
}
```

**Response (200 OK):**
```json
{
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "bio": "Updated bio",
  "location": "New City, Country"
}
```

### 7. Complete Profile
**Endpoint:** `POST /auth/profile/complete/`

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "national_id": "1234567890",
  "national_id_front": "<file>",
  "national_id_back": "<file>"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile completed successfully"
}
```

### 8. Refresh Token
**Endpoint:** `POST /auth/token/refresh/`

**Request Body:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response (200 OK):**
```json
{
  "access": "<new_access_token>"
}
```

### 9. Logout
**Endpoint:** `POST /auth/logout/`

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

## Error Responses

### Common Error Codes
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded

### Error Response Format
```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

## Rate Limiting
- Authentication endpoints: 5 requests per minute
- Other endpoints: 60 requests per minute

## Security Considerations
1. All passwords are hashed using bcrypt
2. JWT tokens expire after 5 minutes (access) and 24 hours (refresh)
3. Password reset links expire after 24 hours
4. All endpoints use HTTPS in production
5. Rate limiting is enabled to prevent brute force attacks

## Testing
A Postman collection is available for testing the API endpoints. Import the `Vara API.postman_collection.json` file into Postman to get started.

## Frontend Integration Guide
1. Store tokens securely (e.g., in memory or secure HTTP-only cookies)
2. Implement token refresh logic
3. Handle 401 responses by redirecting to login
4. Use proper error handling for all API calls

## Support
For API support, please contact:
- Email: support@vara.com
- Documentation: https://docs.vara.com