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

### 4. Get User Profile
**Endpoint:** `GET /auth/profile/`

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "username": "username",
  "email": "user@example.com",
  "phone_number": "1234567890",
  "date_of_birth": "1990-01-01",
  "profile_picture": "url_to_image",
  "bio": "User bio",
  "location": "User location",
  "average_rating": 4.5,
  "member_since": "January 2024",
  "full_name": "First Last",
  "is_trusted": false
}
```

### 5. Update Profile
**Endpoint:** `PATCH /auth/profile/`

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "bio": "Updated bio",
  "location": "Updated location",
  "phone_number": "1234567890",
  "profile_picture": "file"
}
```

**Response (200 OK):**
```json
{
  // Updated profile data
}
```

### 6. Complete Profile
**Endpoint:** `POST /auth/profile/complete/`

**Headers Required:**
```
Authorization: Bearer <access_token>
```

**Request Body (multipart/form-data):**
```
first_name: "First"
last_name: "Last"
phone_number: "1234567890"
date_of_birth: "1990-01-01"
national_id: "1234567890"
national_id_front: [file]
national_id_back: [file]
```

**Response (200 OK):**
```json
{
  // Completed profile data
}
```

### 7. Token Refresh
**Endpoint:** `POST /token/refresh/`

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

### 8. Logout
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
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Missing or invalid authentication
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource not found
- 429 Too Many Requests: Rate limit exceeded

### Error Response Format
```json
{
  "error": "Error message",
  "details": {
    "field_name": ["Error message"]
  }
}
```

## Rate Limiting
- Authentication endpoints: 5 requests per minute
- Other endpoints: 60 requests per minute

## Security Considerations
1. All endpoints except registration and login require authentication
2. Passwords are hashed using Django's secure password hashing
3. JWT tokens expire after 5 minutes (access) and 24 hours (refresh)
4. Email verification is required for account activation
5. Rate limiting is implemented to prevent brute force attacks

## Testing
The API can be tested using the provided Postman collection. See `POSTMAN_COLLECTION.md` for detailed testing instructions.

## Frontend Integration Guide
1. Store tokens securely (e.g., in memory or secure cookies)
2. Implement token refresh logic before access token expiration
3. Handle 401 responses by redirecting to login
4. Use multipart/form-data for file uploads
5. Implement proper error handling and user feedback

## Support
For API support or questions, contact: service.vara2025@gmail.com