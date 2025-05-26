# Frontend Integration Guide

## Overview
This guide provides detailed instructions for integrating the Vara User Authentication API with your frontend application. The API uses JWT (JSON Web Token) authentication and follows RESTful principles.

## Prerequisites
- Frontend framework (React, Vue, Angular, etc.)
- HTTP client (Axios, Fetch, etc.)
- State management solution (Redux, Vuex, etc.)

## Authentication Flow

### 1. User Registration
```javascript
// Example using Axios
const registerUser = async (userData) => {
  try {
    const response = await axios.post('http://localhost:8000/auth/signup/', {
      email: userData.email,
      password: userData.password,
      username: userData.username,
      marketing_consent: userData.marketing_consent
    });
    
    // Handle successful registration
    return response.data;
  } catch (error) {
    // Handle registration errors
    throw error.response.data;
  }
};
```

### 2. Email Verification
```javascript
const verifyEmail = async (code) => {
  try {
    const response = await axios.get(`http://localhost:8000/auth/signup/verify/?code=${code}`);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};
```

### 3. User Login
```javascript
const login = async (credentials) => {
  try {
    const response = await axios.post('http://localhost:8000/auth/login/', {
      email: credentials.email,
      password: credentials.password
    });
    
    // Store tokens securely
    const { access, refresh } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};
```

## Token Management

### 1. Axios Interceptor Setup
```javascript
// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't tried to refresh token yet
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('http://localhost:8000/token/refresh/', {
          refresh: refreshToken
        });
        
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Handle refresh token failure (e.g., logout user)
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

## Profile Management

### 1. Get User Profile
```javascript
const getProfile = async () => {
  try {
    const response = await api.get('/auth/profile/');
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};
```

### 2. Update Profile
```javascript
const updateProfile = async (profileData) => {
  try {
    const response = await api.patch('/auth/profile/', profileData);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};
```

### 3. Complete Profile
```javascript
const completeProfile = async (profileData) => {
  try {
    // Create FormData for file uploads
    const formData = new FormData();
    Object.keys(profileData).forEach(key => {
      formData.append(key, profileData[key]);
    });
    
    const response = await api.post('/auth/profile/complete/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};
```

## Error Handling

### 1. Global Error Handler
```javascript
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        // Handle validation errors
        return {
          type: 'VALIDATION_ERROR',
          message: 'Please check your input',
          details: data
        };
      
      case 401:
        // Handle authentication errors
        return {
          type: 'AUTH_ERROR',
          message: 'Please login to continue'
        };
      
      case 403:
        // Handle permission errors
        return {
          type: 'PERMISSION_ERROR',
          message: 'You don\'t have permission to perform this action'
        };
      
      case 404:
        // Handle not found errors
        return {
          type: 'NOT_FOUND',
          message: 'The requested resource was not found'
        };
      
      default:
        // Handle other errors
        return {
          type: 'SERVER_ERROR',
          message: 'An unexpected error occurred'
        };
    }
  }
  
  // Handle network errors
  return {
    type: 'NETWORK_ERROR',
    message: 'Please check your internet connection'
  };
};
```

### 2. Form Validation
```javascript
const validateSignupForm = (data) => {
  const errors = {};
  
  // Email validation
  if (!data.email) {
    errors.email = 'Email is required';
  } else if (!/\S+@\S+\.\S+/.test(data.email)) {
    errors.email = 'Email is invalid';
  }
  
  // Password validation
  if (!data.password) {
    errors.password = 'Password is required';
  } else if (data.password.length < 8) {
    errors.password = 'Password must be at least 8 characters';
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/.test(data.password)) {
    errors.password = 'Password must contain uppercase, lowercase, number and special character';
  }
  
  // Username validation
  if (!data.username) {
    errors.username = 'Username is required';
  } else if (!/^[a-zA-Z0-9_]+$/.test(data.username)) {
    errors.username = 'Username can only contain letters, numbers, and underscores';
  }
  
  return errors;
};
```

## State Management

### 1. Redux Example
```javascript
// authSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { login, register, logout } from '../api/auth';

export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await login(credentials);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    token: null,
    loading: false,
    error: null
  },
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.token = action.payload.access;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});
```

## Security Best Practices

1. **Token Storage**
   - Store tokens in memory when possible
   - Use secure, HTTP-only cookies for refresh tokens
   - Implement token rotation
   - Clear tokens on logout

2. **Request Security**
   - Use HTTPS for all API calls
   - Implement CSRF protection
   - Sanitize user inputs
   - Validate responses

3. **Error Handling**
   - Don't expose sensitive information in errors
   - Implement proper logging
   - Handle network errors gracefully
   - Provide user-friendly error messages

## Performance Optimization

1. **Caching**
   - Cache user profile data
   - Implement request debouncing
   - Use local storage for non-sensitive data

2. **Request Optimization**
   - Batch related requests
   - Implement request cancellation
   - Use optimistic updates

## Testing

1. **Unit Tests**
```javascript
// auth.test.js
import { login, register } from '../api/auth';

describe('Auth API', () => {
  test('login success', async () => {
    const credentials = {
      email: 'test@example.com',
      password: 'SecurePassword123!'
    };
    
    const response = await login(credentials);
    expect(response.data).toHaveProperty('access');
    expect(response.data).toHaveProperty('refresh');
  });
  
  test('login failure', async () => {
    const credentials = {
      email: 'test@example.com',
      password: 'wrongpassword'
    };
    
    await expect(login(credentials)).rejects.toThrow();
  });
});
```

2. **Integration Tests**
```javascript
// auth.integration.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginForm } from '../components/LoginForm';

describe('Login Form', () => {
  test('submits form with valid data', async () => {
    render(<LoginForm />);
    
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'SecurePassword123!' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    expect(await screen.findByText(/welcome/i)).toBeInTheDocument();
  });
});
```

## Support
For integration support or questions, contact: service.vara2025@gmail.com 