# Vara API Postman Collection Guide

## Setup Instructions

1. **Import the Collection**
   - Open Postman
   - Click "Import" button
   - Select the `Vara API.postman_collection.json` file

2. **Environment Setup**
   - Create a new environment named "Vara Local"
   - Add the following variables:
     - `base_url`: `http://localhost:8000`
     - `access_token`: (leave empty, will be set automatically)
     - `refresh_token`: (leave empty, will be set automatically)

## Collection Structure

### 1. Authentication
#### Signup
- **Method**: POST
- **URL**: `{{base_url}}/auth/signup/`
- **Body**:
```json
{
  "email": "test@example.com",
  "password": "SecurePassword123!",
  "username": "testuser",
  "marketing_consent": true
}
```
- **Tests**:
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});
```

#### Verify Email
- **Method**: GET
- **URL**: `{{base_url}}/auth/signup/verify/?code={{verification_code}}`
- **Note**: Check console output for verification code

#### Login
- **Method**: POST
- **URL**: `{{base_url}}/auth/login/`
- **Body**:
```json
{
  "email": "test@example.com",
  "password": "SecurePassword123!"
}
```
- **Tests**:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has tokens", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access');
    pm.expect(jsonData).to.have.property('refresh');
    
    // Save tokens to environment
    pm.environment.set("access_token", jsonData.access);
    pm.environment.set("refresh_token", jsonData.refresh);
});
```

### 2. Profile Management
#### Get Profile
- **Method**: GET
- **URL**: `{{base_url}}/auth/profile/`
- **Headers**: 
  - `Authorization`: `Bearer {{access_token}}`
- **Tests**:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has user data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('email');
    pm.expect(jsonData).to.have.property('username');
});
```

#### Update Profile
- **Method**: PATCH
- **URL**: `{{base_url}}/auth/profile/`
- **Headers**: 
  - `Authorization`: `Bearer {{access_token}}`
- **Body**:
```json
{
  "bio": "This is my test bio",
  "location": "Test Location"
}
```
- **Tests**:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
```

#### Complete Profile
- **Method**: POST
- **URL**: `{{base_url}}/auth/profile/complete/`
- **Headers**: 
  - `Authorization`: `Bearer {{access_token}}`
- **Body** (form-data):
  - `first_name`: "Test"
  - `last_name`: "User"
  - `phone_number`: "1234567890"
  - `date_of_birth`: "1990-01-01"
  - `national_id`: "1234567890"
  - `national_id_front`: [file]
  - `national_id_back`: [file]
- **Tests**:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
```

### 3. Token Management
#### Refresh Token
- **Method**: POST
- **URL**: `{{base_url}}/token/refresh/`
- **Body**:
```json
{
  "refresh": "{{refresh_token}}"
}
```
- **Tests**:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("New access token received", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access');
    pm.environment.set("access_token", jsonData.access);
});
```

#### Logout
- **Method**: POST
- **URL**: `{{base_url}}/auth/logout/`
- **Headers**: 
  - `Authorization`: `Bearer {{access_token}}`
- **Body**:
```json
{
  "refresh": "{{refresh_token}}"
}
```
- **Tests**:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
```

## Testing Workflow

1. **Initial Setup**
   - Run the Signup request
   - Check console for verification code
   - Run Verify Email request with the code
   - Run Login request to get tokens

2. **Profile Management**
   - Get Profile to verify authentication
   - Update Profile with new information
   - Complete Profile with required documents

3. **Token Management**
   - Test token refresh before access token expires
   - Test logout functionality

## Common Issues and Solutions

1. **401 Unauthorized**
   - Check if access token is valid
   - Try refreshing the token
   - Re-login if refresh token is expired

2. **400 Bad Request**
   - Verify request body format
   - Check required fields
   - Validate input data format

3. **File Upload Issues**
   - Ensure correct content-type header
   - Check file size limits
   - Verify file format is supported

## Best Practices

1. **Token Management**
   - Store tokens securely
   - Implement automatic token refresh
   - Clear tokens on logout

2. **Error Handling**
   - Check response status codes
   - Parse error messages
   - Implement retry logic for failed requests

3. **Testing**
   - Test all endpoints in sequence
   - Verify response formats
   - Check error scenarios

## Frontend Integration Tips

1. **Authentication Flow**
   - Implement proper token storage
   - Handle token refresh automatically
   - Manage session state

2. **File Uploads**
   - Use FormData for multipart requests
   - Show upload progress
   - Handle upload errors

3. **Error Handling**
   - Display user-friendly error messages
   - Implement retry mechanisms
   - Handle network issues

## Support
For issues with the Postman collection or testing, contact: service.vara2025@gmail.com