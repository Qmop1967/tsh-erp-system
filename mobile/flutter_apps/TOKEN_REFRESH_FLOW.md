# Token Refresh Flow Documentation

**Automatic Token Refresh for TSH ERP Mobile Apps**

---

## Overview

The TSH ERP mobile apps now implement an automatic token refresh mechanism to keep users logged in for up to 30 days without requiring re-authentication. This improves user experience while maintaining security.

---

## Architecture

### Token Types

1. **Access Token**
   - Duration: 30 minutes
   - Purpose: Used for authenticating API requests
   - Security: Short-lived to minimize security risk if compromised
   - Storage: Secure storage (flutter_secure_storage)

2. **Refresh Token**
   - Duration: 30 days
   - Purpose: Used to obtain new access tokens
   - Security: Long-lived but only used for token refresh endpoint
   - Storage: Secure storage (flutter_secure_storage)

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Login Flow                              │
└─────────────────────────────────────────────────────────────────┘

1. User enters credentials
   ↓
2. App sends POST /api/auth/login/mobile
   {
     "email": "user@example.com",
     "password": "password123"
   }
   ↓
3. Backend validates credentials
   ↓
4. Backend generates tokens:
   - Access Token (30 min expiry)
   - Refresh Token (30 day expiry)
   ↓
5. Backend responds:
   {
     "access_token": "eyJ...",
     "refresh_token": "eyJ...",
     "token_type": "bearer",
     "user": {...}
   }
   ↓
6. App saves both tokens to secure storage
   ↓
7. User is logged in!

┌─────────────────────────────────────────────────────────────────┐
│                  Automatic Token Refresh                         │
└─────────────────────────────────────────────────────────────────┘

1. App makes API request with access token
   GET /api/accounting/currencies
   Authorization: Bearer eyJ... (access token)
   ↓
2. Backend checks token validity
   ↓
   ┌─── Token Valid? ────┐
   │                     │
  Yes                   No (401 Unauthorized)
   │                     │
   ↓                     ↓
Return data         Interceptor catches 401
   │                     │
   │                     ↓
   │              3. App automatically calls:
   │                 POST /api/auth/refresh
   │                 {
   │                   "refresh_token": "eyJ..."
   │                 }
   │                     │
   │                     ↓
   │              4. Backend validates refresh token
   │                     │
   │                     ↓
   │              5. Backend generates NEW access token
   │                     │
   │                     ↓
   │              6. Backend responds:
   │                 {
   │                   "access_token": "eyJ... (NEW)",
   │                   "token_type": "bearer"
   │                 }
   │                     │
   │                     ↓
   │              7. App saves new access token
   │                     │
   │                     ↓
   │              8. App RETRIES original request
   │                 GET /api/accounting/currencies
   │                 Authorization: Bearer eyJ... (NEW token)
   │                     │
   └─────────────────────┴─ Success! User never notices.
```

---

## Backend Implementation

### 1. Token Creation (`auth_service.py`)

```python
# Access token - 30 minutes
@staticmethod
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Refresh token - 30 days
@staticmethod
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=30))
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Token verification with type check
@staticmethod
def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        t_type: str = payload.get("type")

        if email is None or t_type != token_type:
            return None

        return {"email": email, "type": t_type}
    except JWTError:
        return None
```

**Location**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/app/services/auth_service.py`

### 2. Mobile Login Endpoint (`auth.py`)

```python
@router.post("/login/mobile", response_model=LoginResponse)
async def mobile_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Create both tokens
    access_token = AuthService.create_access_token(
        data={"sub": user.email, "platform": "mobile"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = AuthService.create_refresh_token(
        data={"sub": user.email, "platform": "mobile"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={...}
    )
```

**Location**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/app/routers/auth.py:176-224`

### 3. Refresh Token Endpoint (`auth.py`)

```python
@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    # Verify refresh token
    token_data = AuthService.verify_token(refresh_data.refresh_token, token_type="refresh")
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Get user
    user = db.query(User).filter(User.email == token_data["email"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Create new access token
    access_token = AuthService.create_access_token(
        data={"sub": user.email, "platform": "mobile"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer"
    )
```

**Location**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/app/routers/auth.py:274-312`

---

## Flutter Implementation

### 1. API Service with Auto-Refresh (`api_service.dart`)

```dart
class ApiService {
  static const String _tokenKey = 'auth_token';
  static const String _refreshTokenKey = 'refresh_token';

  late final Dio _dio;
  late final FlutterSecureStorage _storage;

  // Setup interceptor for automatic token refresh
  void _setupInterceptors() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Add access token to every request
        final token = await getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        // Catch 401 Unauthorized errors
        if (error.response?.statusCode == 401) {
          // Try to refresh token
          final refreshed = await _refreshToken();
          if (refreshed) {
            // Retry the original request with new token
            final opts = error.requestOptions;
            final token = await getToken();
            if (token != null) {
              opts.headers['Authorization'] = 'Bearer $token';
            }
            try {
              final response = await _dio.fetch(opts);
              return handler.resolve(response);
            } catch (e) {
              return handler.next(error);
            }
          } else {
            // Refresh failed - logout user
            await clearTokens();
            throw AuthException('Session expired. Please login again.');
          }
        }
        handler.next(error);
      },
    ));
  }

  // Automatic token refresh
  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await getRefreshToken();
      if (refreshToken == null) return false;

      // Use separate Dio instance to avoid interceptor loop
      final dio = Dio(BaseOptions(
        baseUrl: _baseUrl,
        headers: {'Content-Type': 'application/json'},
      ));

      final response = await dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        // Update access token (keep refresh token)
        await _storage.write(key: _tokenKey, value: data['access_token']);
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  // Token management
  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  Future<String?> getRefreshToken() async {
    return await _storage.read(key: _refreshTokenKey);
  }

  Future<void> saveTokens(String accessToken, String? refreshToken) async {
    await _storage.write(key: _tokenKey, value: accessToken);
    if (refreshToken != null) {
      await _storage.write(key: _refreshTokenKey, value: refreshToken);
    }
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }
}
```

**Location**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/shared/tsh_core_package/lib/src/services/api_service.dart`

### 2. Auth Service Login (`auth_service.dart`)

```dart
Future<ApiResponse<User>> login(String email, String password) async {
  try {
    // Call mobile login endpoint
    final response = await _apiService.post(
      '/auth/login/mobile',
      data: {
        'email': email,
        'password': password,
      },
    );

    if (response.success && response.data != null) {
      final data = response.data;

      // Save both tokens to secure storage
      await _apiService.saveTokens(
        data['access_token'],
        data['refresh_token'], // 30 days expiration
      );

      // Parse user data and update state
      final userData = data['user'];
      _currentUser = User(...);

      await _storageService.saveData(_userKey, _currentUser!.toJson());
      _userController.add(_currentUser);

      return ApiResponse.success(
        data: _currentUser,
        message: 'Login successful',
      );
    } else {
      return ApiResponse.error(error: response.error ?? 'Login failed');
    }
  } catch (e) {
    return ApiResponse.error(error: e.toString());
  }
}
```

**Location**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/mobile/flutter_apps/shared/tsh_core_package/lib/src/services/auth_service.dart:75-143`

---

## Security Considerations

### 1. Token Storage

- **Secure Storage**: Both tokens are stored using `flutter_secure_storage`
- **Encrypted**: Tokens are encrypted at rest
- **iOS**: Uses Keychain
- **Android**: Uses KeyStore

### 2. Token Types

- **Type Field**: Each JWT contains a `type` field (`"access"` or `"refresh"`)
- **Verification**: Backend verifies token type matches expected use
- **Prevention**: Prevents using refresh token as access token and vice versa

### 3. Token Expiration

- **Short Access Token**: 30 minutes reduces window for misuse
- **Long Refresh Token**: 30 days for convenience
- **Automatic Refresh**: Happens transparently without user intervention

### 4. Error Handling

- **401 Unauthorized**: Triggers automatic refresh
- **Refresh Fails**: User is logged out and redirected to login
- **Invalid Tokens**: Cleared from storage immediately

---

## User Experience

### What Users Experience

1. **Initial Login**: User logs in once with email/password
2. **First 30 Minutes**: Access token is valid, all requests succeed
3. **After 30 Minutes**: Access token expires
   - App automatically refreshes token
   - User continues working without interruption
4. **Up to 30 Days**: Refresh token keeps getting new access tokens
5. **After 30 Days**: Refresh token expires, user must log in again

### Transparent Operation

- Users never see "Session Expired" messages (except after 30 days)
- No interruptions during work
- Seamless experience across all 11 apps

---

## Configuration

### Backend Environment Variables

```bash
# .env file
ACCESS_TOKEN_EXPIRE_MINUTES=30      # 30 minutes for access tokens
REFRESH_TOKEN_EXPIRE_DAYS=30        # 30 days for refresh tokens
SECRET_KEY=your-secret-key-here     # JWT signing key
ALGORITHM=HS256                     # JWT algorithm
```

**Location**: `/Users/khaleelal-mulla/TSH_ERP_Ecosystem/.env`

### Flutter Configuration

All apps use the shared `tsh_core_package` which automatically handles token refresh. No per-app configuration needed.

---

## Testing

### Manual Testing

1. **Login Test**:
   ```bash
   curl -X POST http://192.168.68.51:8000/api/auth/login/mobile \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@tsh.com", "password": "admin123"}'
   ```

   Expected response:
   ```json
   {
     "access_token": "eyJ...",
     "refresh_token": "eyJ...",
     "token_type": "bearer",
     "user": {...}
   }
   ```

2. **Refresh Token Test**:
   ```bash
   curl -X POST http://192.168.68.51:8000/api/auth/refresh \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "eyJ..."}'
   ```

   Expected response:
   ```json
   {
     "access_token": "eyJ... (new token)",
     "token_type": "bearer"
   }
   ```

3. **API Request with Token**:
   ```bash
   curl -X GET http://192.168.68.51:8000/api/accounting/currencies \
     -H "Authorization: Bearer eyJ..."
   ```

### App Testing Checklist

- [ ] User can login successfully
- [ ] Access token is saved to secure storage
- [ ] Refresh token is saved to secure storage
- [ ] API requests work with valid access token
- [ ] After 30 minutes, automatic refresh happens
- [ ] User is not interrupted during automatic refresh
- [ ] After 30 days, user is logged out
- [ ] Invalid tokens are cleared properly
- [ ] Network errors are handled gracefully

---

## Migration Notes

### For Existing Apps

All 11 Flutter apps now use the updated `tsh_core_package` which includes:

1. ✅ Automatic token refresh in `api_service.dart`
2. ✅ Updated login to save refresh tokens in `auth_service.dart`
3. ✅ Proper token storage and retrieval
4. ✅ Error handling and logout on refresh failure

### No Changes Required

Since all apps use the shared package, no per-app changes are needed. Simply:

1. Update dependencies: `flutter pub get`
2. Rebuild app: `flutter run`
3. Test login and API calls

---

## Troubleshooting

### Issue: User keeps getting logged out

**Possible Causes**:
- Refresh token expired (after 30 days)
- Backend SECRET_KEY changed
- Tokens cleared from storage

**Solution**: User needs to login again

### Issue: "Invalid refresh token" error

**Possible Causes**:
- Refresh token malformed
- Backend SECRET_KEY mismatch
- Token type mismatch

**Solution**: Clear tokens and login again

### Issue: 401 errors not being caught

**Check**:
1. Interceptor is properly set up in `_setupInterceptors()`
2. Error handler catches `statusCode == 401`
3. `_refreshToken()` is being called

---

## Benefits

### For Users

- Stay logged in for 30 days
- No daily login prompts
- Seamless work experience
- No interruptions

### For Business

- Better user adoption
- Reduced support requests
- Professional app experience
- Industry-standard security

### For Developers

- Centralized implementation (shared package)
- Automatic handling (no manual refresh calls)
- Proper error handling
- Easy to maintain

---

## Related Files

### Backend

- `/app/services/auth_service.py` - Token creation and verification
- `/app/routers/auth.py` - Login and refresh endpoints
- `/app/schemas/auth.py` - Request/response schemas

### Flutter

- `/mobile/flutter_apps/shared/tsh_core_package/lib/src/services/api_service.dart` - Auto-refresh logic
- `/mobile/flutter_apps/shared/tsh_core_package/lib/src/services/auth_service.dart` - Login with token save

---

## Future Enhancements

### Planned Features

1. **Refresh Token Rotation**: Issue new refresh token on each refresh
2. **Device Tracking**: Track which devices have active tokens
3. **Token Revocation**: Allow admin to revoke specific tokens
4. **Biometric Auth**: Add fingerprint/face unlock after initial login
5. **Session Management**: View and manage active sessions

---

**Last Updated**: 2025-01-24

**Status**: ✅ Fully Implemented and Ready for Production

**Applies To**: All 11 TSH ERP Mobile Apps
