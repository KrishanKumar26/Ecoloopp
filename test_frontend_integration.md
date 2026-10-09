# EcoLoop Frontend Integration Test Guide

## Testing Checklist

### 1. Registration Flow
- [ ] Open http://localhost:3000/register
- [ ] Fill in:
  - Name: Test User
  - Email: frontendtest@example.com
  - Phone: +919999888877 (optional)
  - Password: TestFrontend123
  - Confirm Password: TestFrontend123
- [ ] Click "Create account"
- [ ] Should redirect to home page (/)
- [ ] Should see user name in navigation

### 2. Logout
- [ ] Click on user avatar/name in navigation
- [ ] Click "Sign out"
- [ ] Should redirect to /login
- [ ] Should see "Sign in" and "Get Started" buttons in navigation

### 3. Login Flow
- [ ] Click "Sign in" or go to http://localhost:3000/login
- [ ] Enter:
  - Email: frontendtest@example.com
  - Password: TestFrontend123
- [ ] Click "Sign in"
- [ ] Should redirect to home page (/)
- [ ] Should see user name and EcoPoints in navigation dropdown

### 4. Navigation State
Logged Out:
- [ ] Should see "Sign in" and "Get Started" buttons

Logged In:
- [ ] Should see user avatar with first letter of name
- [ ] Click avatar to see dropdown with:
  - User name
  - Email
  - EcoPoints balance
  - Sign out button

### 5. Error Handling
Registration Errors:
- [ ] Try duplicate email → Should show "Email already registered"
- [ ] Try weak password → Should show password requirements
- [ ] Try mismatched passwords → Should show "Passwords do not match"

Login Errors:
- [ ] Try wrong password → Should show "Invalid email or password"
- [ ] Try non-existent email → Should show "Invalid email or password"
- [ ] Try empty fields → Browser validation should prevent submission

### 6. Loading States
- [ ] Registration button shows spinner while processing
- [ ] Login button shows spinner while processing
- [ ] Navigation shows loading skeleton while checking auth

### 7. Token Persistence
- [ ] Log in
- [ ] Refresh page (F5)
- [ ] Should remain logged in
- [ ] Close browser and reopen → Should still be logged in
- [ ] Log out and refresh → Should stay logged out

### 8. Protected Routes (Future)
Currently all routes are accessible without authentication.
For production, add route protection:
- /scan should require auth
- /pickups should require auth
- /impact should require auth

## Manual Backend Verification

Check that frontend calls reach backend:

```bash
# Watch backend logs
cd ~/Desktop/ecoloop/backend
# Backend terminal shows requests

# Test registration API directly
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test",
    "email": "apitest@example.com",
    "password": "ApiTest123"
  }'

# Test login API directly
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "apitest@example.com",
    "password": "ApiTest123"
  }'
```

## Known Limitations

1. **JWT Storage**: Uses localStorage (see lib/auth.ts for security note)
2. **No Route Protection**: All pages accessible without auth
3. **No Token Refresh**: Tokens expire after 30 minutes, requires re-login
4. **No Remember Me**: Session cleared when browser closes localStorage
5. **No Password Reset**: Not implemented yet
6. **No Email Verification**: Not implemented yet

## Browser Console Checks

Open DevTools Console and check:

```javascript
// Check if token is stored
localStorage.getItem('ecoloop_access_token')

// Check if user is stored
JSON.parse(localStorage.getItem('ecoloop_user'))

// Clear auth (manual logout)
localStorage.removeItem('ecoloop_access_token')
localStorage.removeItem('ecoloop_user')
```

## Success Criteria

✅ User can register a new account
✅ User can log in with correct credentials
✅ User sees their name and EcoPoints in navigation
✅ User can log out
✅ Auth state persists across page refreshes
✅ Error messages are user-friendly
✅ Loading states provide feedback
✅ Token is sent with API requests
