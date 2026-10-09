# Quick Test Guide - Pickup Booking & EcoPoints

## ✅ Prerequisites
- Backend running: http://127.0.0.1:8000
- Frontend running: http://localhost:3000
- User account created and logged in

## 🚀 Quick Test (5 minutes)

### Test 1: Schedule Pickup from Classification
1. Navigate to http://localhost:3000/scan
2. Enter "iPhone 12" and click "Classify Item"
3. Click "Schedule Pickup" button
4. **Expected**: Navigate to schedule form with pre-filled data
5. Fill in address and date (tomorrow or later)
6. Click "Schedule Pickup"
7. **Expected**: Redirect to pickups page

### Test 2: View and Complete Pickup
1. Navigate to http://localhost:3000/pickups
2. **Expected**: See your scheduled pickup with status "Pending"
3. Note the 6-digit OTP shown
4. Enter the OTP in the "Complete with OTP" field
5. Click "Complete" button
6. **Expected**:
   - Alert: "Pickup completed! You earned 75 EcoPoints."
   - Status changes to "Completed"
   - Green checkmark: "✓ 75 EcoPoints awarded"

### Test 3: Check EcoPoints Balance
1. Navigate to http://localhost:3000/impact
2. **Expected**:
   - EcoPoints Balance card shows: 75
   - Pickups Completed shows: 1
   - Transaction history shows: "Completed pickup: ..." (+75 points)
   - Your Rank shows: #1 (or current rank)

### Test 4: Cancel a Pickup
1. Go back to http://localhost:3000/scan
2. Classify another item
3. Schedule another pickup
4. Go to http://localhost:3000/pickups
5. Click "Cancel Pickup" on the new (pending) pickup
6. Enter reason: "Testing cancellation"
7. **Expected**: Status changes to "Cancelled"

### Test 5: Prevent Duplicate EcoPoints
1. Try to complete an already-completed pickup
2. **Expected**: Error message about pickup already being completed

## 🧪 API Test (Command Line)

```bash
cd /Users/krishankumar/Desktop/ecoloop/backend
source venv/bin/activate
python -c "
import requests
import time
from datetime import datetime, timedelta, timezone

BASE_URL = 'http://127.0.0.1:8000'
email = f'test_{int(time.time())}@example.com'

# 1. Register
reg = requests.post(f'{BASE_URL}/api/auth/register', json={
    'name': 'Test User', 'email': email, 'password': 'test12345'
})
print(f'✓ Register: {reg.status_code}')

# 2. Login
login = requests.post(f'{BASE_URL}/api/auth/login', json={
    'email': email, 'password': 'test12345'
})
token = login.json()['access_token']
print(f'✓ Login: {login.status_code}')

# 3. Create pickup
tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
pickup = requests.post(f'{BASE_URL}/api/pickups',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'item_description': 'iPhone 12',
        'scheduled_at': tomorrow.isoformat(),
        'address': {
            'street': '123 Test St', 'city': 'SF', 'state': 'CA',
            'pincode': '94102', 'lat': 37.7749, 'lng': -122.4194
        }
    }
)
data = pickup.json()
print(f'✓ Create pickup: {pickup.status_code}')
print(f'  OTP: {data[\"otp\"]}')

# 4. Complete pickup
complete = requests.post(f'{BASE_URL}/api/pickups/{data[\"pickup_id\"]}/complete',
    headers={'Authorization': f'Bearer {token}'},
    json={'otp': data['otp']}
)
print(f'✓ Complete: {complete.status_code}')
print(f'  Points: {complete.json()[\"eco_points_awarded\"]}')

# 5. Check balance
balance = requests.get(f'{BASE_URL}/api/ecopoints/balance',
    headers={'Authorization': f'Bearer {token}'}
)
print(f'✓ Balance: {balance.json()[\"balance\"]} points')
print('\\n✅ ALL TESTS PASSED')
"
```

## ✅ Success Criteria

All tests pass if:
- Can schedule pickup from scan results
- Can view pickup in list
- Can complete pickup with OTP
- EcoPoints awarded (75 per pickup)
- Balance shows in impact page
- Transaction history visible
- Can cancel pending pickup
- Cannot get duplicate points
- Authentication required for all endpoints

## 📊 Expected Results

### After First Pickup Completion:
- Pickups: 1 completed
- EcoPoints: 75
- Rank: Varies (depends on other users)
- Transactions: 1 transaction

### After Multiple Pickups:
- Each completed pickup adds 75 points
- Balance increases accordingly
- Transaction history grows
- Rank may improve

## 🐛 Common Issues

### "Not authenticated" error
**Fix**: Make sure you're logged in (check localStorage for token)

### "Pickup date must be in the future"
**Fix**: Select tomorrow or later, not today

### OTP not working
**Fix**:
- Check if OTP expired (30 minutes)
- Create new pickup if expired
- Copy OTP exactly as shown

### Cannot see pickups
**Fix**: Make sure you're logged in with the same account that created them

## 🎯 Performance Benchmarks

Expected response times:
- Create pickup: < 200ms
- Get pickups: < 100ms
- Complete pickup: < 300ms (includes transaction)
- Get balance: < 50ms
- Get transactions: < 100ms

## ✅ Checklist

Manual Testing:
- [ ] Can schedule pickup from scan
- [ ] Pre-fill works correctly
- [ ] Date validation works
- [ ] Address form works
- [ ] Pickup appears in list
- [ ] OTP is visible
- [ ] Can complete with OTP
- [ ] EcoPoints awarded
- [ ] Balance updates
- [ ] Transaction recorded
- [ ] Can cancel pending pickup
- [ ] Cannot cancel completed pickup
- [ ] Impact page shows correct stats
- [ ] Authentication enforced

API Testing:
- [ ] All endpoints return correct status codes
- [ ] Authentication required
- [ ] Validation works
- [ ] Duplicate prevention works
- [ ] No errors in backend logs

## 🎉 Success Message

If all tests pass, you should see:
```
✅ Pickup Booking System: Working
✅ EcoPoints Rewards: Working
✅ Balance Tracking: Working
✅ Transaction History: Working
✅ Duplicate Prevention: Working
✅ Authentication: Working
✅ Frontend UI: Working
```

---

**Quick test completed on**: _____________
**All tests passed**: ☐ Yes ☐ No
**Issues found**: ___________________________
