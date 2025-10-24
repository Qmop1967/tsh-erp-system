# Security Features Testing Guide

## Overview
This document provides a comprehensive guide to testing all enhanced security features implemented in the TSH ERP Ecosystem.

## Test Environment
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **Database**: PostgreSQL (erp_db)
- **Date**: October 20, 2025

---

## 1. Password Strength Validation Testing

### Test Cases:

#### Test 1.1: Weak Password Rejection
**Steps:**
1. Navigate to user registration or password change
2. Attempt to set password: `password123`
3. **Expected Result**: Error message "Password must contain at least one special character"

#### Test 1.2: Short Password Rejection
**Steps:**
1. Try password: `Short1!`
2. **Expected Result**: Error message "Password must be at least 12 characters long"

#### Test 1.3: Strong Password Acceptance
**Steps:**
1. Try password: `SecurePass123!@#`
2. **Expected Result**: Password accepted successfully

**API Endpoint**: `POST /api/auth/register` or password change endpoint

---

## 2. Rate Limiting & Account Lockout Testing

### Test Cases:

#### Test 2.1: Failed Login Attempts Tracking
**Steps:**
1. Attempt to login with incorrect password 3 times
2. Check database: `SELECT * FROM login_attempts WHERE email = 'test@example.com' ORDER BY attempted_at DESC LIMIT 5;`
3. **Expected Result**: 3 failed login attempt records created

#### Test 2.2: Account Lockout Trigger
**Steps:**
1. Make 5 failed login attempts with same email
2. Try 6th login attempt
3. **Expected Result**:
   - HTTP 429 Error
   - Message: "Too many failed attempts. Account locked for 15 minutes."
   - Record in `account_lockouts` table

#### Test 2.3: Lockout Expiration
**Steps:**
1. Wait 15 minutes after lockout
2. Attempt login with correct credentials
3. **Expected Result**: Login successful

**API Endpoint**: `POST /api/auth/login`

**Database Check:**
```sql
-- View login attempts
SELECT * FROM login_attempts WHERE email = 'test@example.com' ORDER BY attempted_at DESC LIMIT 10;

-- View lockouts
SELECT * FROM account_lockouts WHERE user_id = 1 ORDER BY locked_at DESC;
```

---

## 3. Multi-Factor Authentication (MFA) Testing

### Test Cases:

#### Test 3.1: MFA Setup Initiation
**Steps:**
1. Login to application
2. Navigate to Security Dashboard: http://localhost:5173/security
3. Click on "Multi-Factor Authentication" card
4. Click "Begin MFA Setup"
5. **Expected Result**: QR code displayed

**API Endpoint**: `POST /api/auth/mfa/setup`

#### Test 3.2: QR Code Scanning
**Steps:**
1. Open Google Authenticator or Authy app
2. Scan the QR code
3. **Expected Result**: Account added to authenticator app showing 6-digit codes

#### Test 3.3: TOTP Verification
**Steps:**
1. Enter 6-digit code from authenticator app
2. Click "Verify & Enable MFA"
3. **Expected Result**:
   - Success message
   - Backup codes displayed
   - Record in `user_mfa` table

**Database Check:**
```sql
-- Verify MFA configuration
SELECT * FROM user_mfa WHERE user_id = 1;
```

#### Test 3.4: Backup Codes Download
**Steps:**
1. Click "Download Codes" button
2. **Expected Result**: Text file downloaded with 10 backup codes

#### Test 3.5: MFA Login Flow
**Steps:**
1. Logout
2. Login with email and password
3. Enter 6-digit code when prompted
4. **Expected Result**: Successfully authenticated

**API Endpoint**: `POST /api/auth/mfa/verify-login`

#### Test 3.6: Backup Code Usage
**Steps:**
1. Logout
2. Login with email and password
3. Use one of the backup codes instead of TOTP
4. **Expected Result**: Login successful, backup code marked as used

---

## 4. Session Management Testing

### Test Cases:

#### Test 4.1: Session Creation
**Steps:**
1. Login from Chrome on Desktop
2. Check database
3. **Expected Result**: New session record created

**Database Check:**
```sql
-- View active sessions
SELECT * FROM user_sessions WHERE user_id = 1 AND terminated_at IS NULL;
```

#### Test 4.2: Multi-Device Sessions
**Steps:**
1. Login from Chrome (Desktop)
2. Login from Firefox (Desktop)
3. Login from Mobile browser
4. Navigate to: http://localhost:5173/security/sessions
5. **Expected Result**: All 3 sessions visible with device info

**API Endpoint**: `GET /api/auth/sessions`

#### Test 4.3: Session Activity Tracking
**Steps:**
1. Make API request with token
2. Check database
3. **Expected Result**: `last_activity` timestamp updated

#### Test 4.4: Individual Session Termination
**Steps:**
1. In Session Management page, click "Logout" on a non-current session
2. **Expected Result**:
   - Session removed from list
   - Other device logged out
   - Record marked with `terminated_at`

**API Endpoint**: `DELETE /api/auth/sessions/{session_id}`

#### Test 4.5: Terminate All Other Sessions
**Steps:**
1. Have 3+ active sessions
2. Click "Logout All Others" button
3. **Expected Result**:
   - Only current session remains
   - Other devices logged out

**API Endpoint**: `POST /api/auth/sessions/terminate-all?except_current=true`

#### Test 4.6: Concurrent Session Limit
**Steps:**
1. Login from 4 different browsers/devices
2. **Expected Result**: Oldest session automatically terminated (limit is 3)

---

## 5. Token Blacklist & Logout Testing

### Test Cases:

#### Test 5.1: Proper Logout
**Steps:**
1. Login and get access token
2. Click logout
3. Try to use the same token for an API request
4. **Expected Result**: HTTP 401 Error "Token has been revoked"

**API Endpoint**: `POST /api/auth/logout`

**Database Check:**
```sql
-- View blacklisted tokens
SELECT * FROM token_blacklist WHERE user_id = 1 ORDER BY blacklisted_at DESC;
```

#### Test 5.2: Token Blacklist Expiration
**Steps:**
1. Check `expires_at` field in token_blacklist
2. **Expected Result**: Matches token's original expiration time

---

## 6. Password Policy Enforcement Testing

### Test Cases:

#### Test 6.1: Password History Prevention
**Steps:**
1. Change password to "NewPassword123!@#"
2. Try to change password back to "NewPassword123!@#"
3. **Expected Result**: Error "Cannot reuse one of your last 5 passwords"

**Database Check:**
```sql
-- View password history
SELECT * FROM password_history WHERE user_id = 1 ORDER BY created_at DESC LIMIT 5;
```

#### Test 6.2: Password Expiration Warning
**Steps:**
1. Check user whose password is >85 days old
2. Login
3. **Expected Result**: Warning message about upcoming password expiration

---

## 7. Security Event Logging Testing

### Test Cases:

#### Test 7.1: Login Events
**Steps:**
1. Perform successful login
2. Perform failed login
3. Check database
4. **Expected Result**: Both events logged

**Database Check:**
```sql
-- View security events
SELECT * FROM security_events
WHERE event_type IN ('successful_login', 'failed_login')
ORDER BY created_at DESC
LIMIT 10;
```

#### Test 7.2: MFA Events
**Steps:**
1. Enable MFA
2. Disable MFA
3. **Expected Result**: Events logged with severity levels

#### Test 7.3: Session Events
**Steps:**
1. Create session
2. Terminate session
3. **Expected Result**: Both events logged

---

## 8. Audit Log Viewer Testing

### Test Cases:

#### Test 8.1: View All Logs
**Steps:**
1. Login as admin
2. Navigate to: http://localhost:5173/security/audit-log
3. **Expected Result**: All security events displayed with color-coded severity

**API Endpoint**: `GET /api/auth/audit-log`

#### Test 8.2: Filter by Event Type
**Steps:**
1. Select "Failed Login" from Event Type dropdown
2. Click "Apply Filters"
3. **Expected Result**: Only failed login events shown

#### Test 8.3: Filter by Severity
**Steps:**
1. Select "Critical" from Severity dropdown
2. Click "Apply Filters"
3. **Expected Result**: Only critical events shown (account lockouts, suspicious activity)

#### Test 8.4: Date Range Filtering
**Steps:**
1. Set Date From: 2025-10-19
2. Set Date To: 2025-10-20
3. Click "Apply Filters"
4. **Expected Result**: Events within date range displayed

#### Test 8.5: Search Functionality
**Steps:**
1. Enter user email in search box
2. Click "Apply Filters"
3. **Expected Result**: Only events for that user shown

#### Test 8.6: Export to CSV
**Steps:**
1. Click "Export CSV" button
2. **Expected Result**: CSV file downloaded with all audit log data

---

## 9. Security Dashboard Testing

### Test Cases:

#### Test 9.1: Security Score Calculation
**Steps:**
1. Navigate to: http://localhost:5173/security
2. Check security score
3. **Expected Result**:
   - Base score: 50
   - +30 if MFA enabled
   - +10 if ≤2 active sessions
   - +10 if 0 failed login attempts
   - Total: 0-100

#### Test 9.2: MFA Status Card
**Steps:**
1. View dashboard
2. **Expected Result**:
   - Green checkmark if MFA enabled
   - Yellow warning if not enabled

#### Test 9.3: Active Sessions Card
**Steps:**
1. View dashboard
2. Click on Active Sessions card
3. **Expected Result**: Redirects to Session Management page

#### Test 9.4: Security Recommendations
**Steps:**
1. Disable MFA
2. View dashboard
3. **Expected Result**: Yellow recommendation box suggesting MFA enablement

---

## 10. Permission & Access Control Testing

### Test Cases:

#### Test 10.1: Audit Log Access Control
**Steps:**
1. Login as regular user (not admin)
2. Try to access: http://localhost:5173/security/audit-log
3. **Expected Result**: HTTP 403 Error "Insufficient permissions"

#### Test 10.2: Admin Access
**Steps:**
1. Login as admin/owner
2. Access audit log
3. **Expected Result**: Full access granted

---

## Database Verification Queries

### Check All Security Tables
```sql
-- 1. Login Attempts
SELECT COUNT(*) as total_attempts,
       SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
       SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed
FROM login_attempts;

-- 2. Account Lockouts
SELECT COUNT(*) as total_lockouts,
       COUNT(CASE WHEN unlocked_at IS NULL THEN 1 END) as currently_locked
FROM account_lockouts;

-- 3. MFA Configuration
SELECT COUNT(*) as users_with_mfa_enabled,
       COUNT(CASE WHEN verified_at IS NOT NULL THEN 1 END) as verified_users
FROM user_mfa;

-- 4. Active Sessions
SELECT COUNT(*) as total_sessions,
       COUNT(CASE WHEN terminated_at IS NULL THEN 1 END) as active_sessions
FROM user_sessions;

-- 5. Token Blacklist
SELECT COUNT(*) as blacklisted_tokens,
       COUNT(CASE WHEN expires_at > NOW() THEN 1 END) as still_valid_blacklisted
FROM token_blacklist;

-- 6. Security Events by Type
SELECT event_type, severity, COUNT(*) as count
FROM security_events
GROUP BY event_type, severity
ORDER BY count DESC;

-- 7. Password History
SELECT u.email, COUNT(ph.id) as password_changes
FROM users u
LEFT JOIN password_history ph ON u.id = ph.user_id
GROUP BY u.id, u.email;
```

---

## API Endpoints Summary

### Authentication
- `POST /api/auth/login` - Enhanced login with rate limiting
- `POST /api/auth/logout` - Proper logout with token blacklist
- `POST /api/auth/register` - Registration with password validation

### MFA
- `POST /api/auth/mfa/setup` - Initiate MFA setup
- `POST /api/auth/mfa/verify-setup` - Verify and enable MFA
- `POST /api/auth/mfa/verify-login` - MFA code verification during login
- `POST /api/auth/mfa/disable` - Disable MFA
- `GET /api/auth/mfa/backup-codes` - Get new backup codes

### Sessions
- `GET /api/auth/sessions` - List all active sessions
- `DELETE /api/auth/sessions/{id}` - Terminate specific session
- `POST /api/auth/sessions/terminate-all` - Terminate all sessions

### Audit
- `GET /api/auth/audit-log` - Get security audit logs (admin only)

---

## Performance Testing

### Load Testing Recommendations
```bash
# Test rate limiting with multiple concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}' &
done
wait
```

---

## Security Best Practices Verification

### Checklist
- [ ] SECRET_KEY is loaded from environment variable (not hardcoded)
- [ ] Passwords are hashed with bcrypt
- [ ] JWT tokens expire after 30 minutes
- [ ] Failed login attempts are tracked
- [ ] Accounts lock after 5 failed attempts
- [ ] MFA uses industry-standard TOTP (compatible with Google Authenticator)
- [ ] Sessions track device and IP information
- [ ] Tokens are properly blacklisted on logout
- [ ] Password history prevents reuse of last 5 passwords
- [ ] All security events are logged with timestamps
- [ ] Audit logs are only accessible to admins
- [ ] CORS is configured (currently open for dev, should restrict in production)

---

## Frontend UI Testing

### Security Dashboard
- [ ] Security score displays correctly
- [ ] Cards are clickable and navigate properly
- [ ] Recommendations show based on user's security posture
- [ ] Real-time data loading works

### MFA Setup
- [ ] Step-by-step wizard flows properly
- [ ] QR code displays correctly
- [ ] Manual secret key option works
- [ ] 6-digit code validation works
- [ ] Backup codes display and download properly

### Session Management
- [ ] All sessions load and display
- [ ] Current session is highlighted in green
- [ ] Device icons match device types
- [ ] Time ago displays correctly
- [ ] Session termination works
- [ ] Terminate all others works

### Audit Log Viewer
- [ ] Logs display with proper formatting
- [ ] Severity colors are correct (red=critical, yellow=warning, blue=info)
- [ ] Filters work independently and together
- [ ] Search functionality works
- [ ] CSV export works
- [ ] Summary stats are accurate

---

## Known Limitations & Future Enhancements

### Current Limitations
1. Geolocation is not tracked (only IP address)
2. Device fingerprinting is basic (user-agent only)
3. No SMS or email 2FA options (TOTP only)
4. Password expiration warnings are passive (no forced change)

### Recommended Enhancements
1. Add IP geolocation lookup for session tracking
2. Implement WebAuthn/FIDO2 for hardware key support
3. Add suspicious login detection (unusual IP, device, time)
4. Implement security notifications via email/SMS
5. Add session timeout with inactivity detection
6. Implement CAPTCHA after failed login attempts

---

## Testing Completion Checklist

### Backend Testing
- [ ] All 11 security tables exist in database
- [ ] All API endpoints return correct responses
- [ ] Rate limiting works correctly
- [ ] Account lockout functions properly
- [ ] MFA setup and verification work
- [ ] Session management works
- [ ] Token blacklist prevents token reuse
- [ ] Security events are logged

### Frontend Testing
- [ ] All 4 security pages load without errors
- [ ] Routes are configured correctly
- [ ] UI components render properly
- [ ] API calls work from frontend
- [ ] Error handling works
- [ ] Loading states display correctly

### Integration Testing
- [ ] Login flow works end-to-end
- [ ] MFA flow works end-to-end
- [ ] Session management works across devices
- [ ] Logout properly invalidates tokens
- [ ] Audit log shows all activities

---

## Test Results Summary

**Date**: October 20, 2025
**Tester**: Claude Code
**Status**: Ready for Testing

### Components Implemented
1. ✅ Database Models (11 tables)
2. ✅ Security Services (7 service classes)
3. ✅ Enhanced Auth Router (600+ lines)
4. ✅ Frontend UI Components (4 pages)
5. ✅ API Integration
6. ✅ Routing Configuration

### Environment
- Backend: Running on http://localhost:8000
- Frontend: Running on http://localhost:5173
- Database: PostgreSQL with all migrations applied

### Next Steps
1. Follow test cases above sequentially
2. Document any issues found
3. Verify all database tables populate correctly
4. Test cross-browser compatibility
5. Test mobile responsiveness
6. Perform security penetration testing

---

## Support & Documentation

For implementation details, see:
- `/docs/SECURITY_UPGRADE_COMPLETE.md` - Feature overview
- `/docs/SECURITY_IMPLEMENTATION_GUIDE.md` - Integration guide
- `/app/services/enhanced_auth_security.py` - Service implementations
- `/app/routers/auth_enhanced.py` - API endpoints

---

**Document Version**: 1.0
**Last Updated**: October 20, 2025
