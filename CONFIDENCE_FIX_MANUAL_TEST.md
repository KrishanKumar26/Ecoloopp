# Manual Testing Guide - Confidence NaN Fix

## Quick Test (2 minutes)

### Prerequisites
- Backend running: http://127.0.0.1:8000
- Frontend running: http://localhost:3000
- User account (or create one)

### Test Steps

#### 1. Login
```
URL: http://localhost:3000/login
Email: test@example.com
Password: password123
(or create new account)
```

#### 2. Navigate to Scan Page
```
Click "Scan E-Waste" in navigation
OR
Direct URL: http://localhost:3000/scan
```

#### 3. Test A: Classification Without Image

**Input:**
- Item name: `iPhone 12`
- Image: (leave empty)

**Action:**
- Click "Classify Item"

**Expected Results:**
- ✅ Category: "Mobile Phone"
- ✅ Confidence: "63%" (NOT "NaN%")  ← **THIS IS THE FIX**
- ✅ Progress bar: Green bar at ~63%
- ✅ Estimated Weight: "0.15 kg"
- ✅ Safety tips: 4 bullet points
- ✅ Special care warning: Orange box with battery warning

**Screenshot locations:**
- Confidence percentage
- Progress bar
- Full results display

#### 4. Test B: Classification With Image

**Input:**
- Item name: `Dell Laptop`
- Image: Any JPG/PNG file from your computer

**Action:**
- Click "Choose File"
- Select image
- Verify preview appears
- Click "Classify Item"

**Expected Results:**
- ✅ Image preview shows before submit
- ✅ Classification succeeds (status 200)
- ✅ Category: "Laptop"
- ✅ Confidence: "63%" (valid percentage)
- ✅ Progress bar renders correctly
- ✅ Results display correctly

**Note:**
- Image is uploaded but NOT analyzed
- Classification is based on item name only
- This is honest behavior (baseline keyword classifier)

#### 5. Test C: Various Categories

Try these items and verify confidence shows percentage (not NaN):

| Item Name | Expected Confidence |
|-----------|---------------------|
| `AAA Battery` | ~67% |
| `USB Cable` | ~64% |
| `Computer Mouse` | ~60-70% |
| `iPad Tablet` | ~60-70% |
| `Unknown gadget` | ~30% (low confidence) |

**For each test:**
- ✅ Confidence shows as percentage
- ✅ No "NaN%" anywhere
- ✅ Progress bar renders
- ✅ Can classify another item

#### 6. Test D: Invalid File Upload

**Input:**
- Item name: `Test Phone`
- Image: .txt file or .pdf file

**Action:**
- Try to upload invalid file type

**Expected Results:**
- ✅ Error message: "Please upload a valid image file"
- ✅ Form stays usable
- ✅ Can try again with valid file

#### 7. Test E: Classification History

**Action:**
- Open DevTools → Network tab
- Submit classification
- Look for POST to `/api/classify`

**Expected in Response:**
```json
{
  "confidence": 0.627,  ← Frontend field
  "confidence_score": 0.627,  ← Backend field
  "item_name": "iPhone 12",  ← Frontend field
  "classified_at": "2026-10-08T...",  ← Frontend field
  "special_care_warning": "...",  ← Frontend field
  "image_url": null  ← Frontend field (single value)
}
```

---

## What Fixed the NaN Issue

### Before (Broken)
```
Backend returned:
{
  "confidence_score": 0.627  ← Wrong field name
}

Frontend expected:
result.confidence  ← undefined
result.confidence * 100  ← NaN
Display: "NaN%"
```

### After (Fixed)
```
Backend now returns:
{
  "confidence": 0.627,  ← ✅ Frontend field name
  "confidence_score": 0.627  ← Keep for compatibility
}

Frontend gets:
result.confidence  ← 0.627
result.confidence * 100  ← 62.7
Display: "63%"  ← ✅ FIXED
```

---

## Verification Checklist

After running all tests above, verify:

- [ ] No "NaN%" displayed anywhere
- [ ] Confidence shows as percentage (e.g., "63%")
- [ ] Progress bar renders and fills correctly
- [ ] Multiple classifications work
- [ ] Image upload works (with valid files)
- [ ] Invalid files are rejected
- [ ] Can classify multiple items in sequence
- [ ] "Classify Another Item" resets form
- [ ] "Schedule Pickup" navigates correctly
- [ ] No JavaScript errors in console
- [ ] No TypeScript errors in terminal

---

## Browser DevTools Checks

### 1. Console (F12 → Console)
**Expected:**
- No red errors
- No "NaN" warnings
- Only normal React DevTools messages

### 2. Network (F12 → Network)
**Check POST /api/classify:**
- Status: 200 OK
- Response includes `confidence` field
- Response includes `item_name` field
- Authorization header present

### 3. Application (F12 → Application → Local Storage)
**Verify:**
- `ecoloop_access_token` exists
- Token is valid JWT (3 parts with dots)

---

## Expected vs Actual

| Test Case | Before (Broken) | After (Fixed) |
|-----------|----------------|---------------|
| iPhone 12 confidence | "NaN%" ❌ | "63%" ✅ |
| Progress bar | 0% (broken) ❌ | 63% filled ✅ |
| Laptop confidence | "NaN%" ❌ | "63%" ✅ |
| Battery confidence | "NaN%" ❌ | "67%" ✅ |
| Unknown item | "NaN%" ❌ | "30%" ✅ |
| With image | "NaN%" ❌ | "61%" ✅ |

---

## If You See NaN

If you still see "NaN%" after the fix:

1. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or clear cache manually

2. **Check servers are running:**
   ```bash
   curl http://127.0.0.1:8000/health
   # Should return: {"status":"healthy"}
   ```

3. **Check frontend compiled:**
   ```bash
   cd frontend
   npx tsc --noEmit
   # Should exit with code 0
   ```

4. **Check API response:**
   - Open DevTools → Network
   - Submit classification
   - Check response has "confidence" field (not just "confidence_score")

5. **Check token is valid:**
   - Console: `localStorage.getItem('ecoloop_access_token')`
   - Should return JWT string

---

## Success Criteria

✅ **Fix is successful if:**
1. iPhone 12 shows "63%" (not "NaN%")
2. Progress bar shows green fill at 63%
3. All categories show valid percentages
4. Image upload works without errors
5. No "NaN" anywhere in UI
6. Classification history shows valid confidence
7. No console errors

---

## Quick Verification Command

```javascript
// Run in browser console on /scan page after classification
console.log('Confidence type:', typeof result?.confidence);
console.log('Confidence value:', result?.confidence);
console.log('Is NaN?:', isNaN(result?.confidence));
console.log('Display value:', `${(result?.confidence * 100).toFixed(0)}%`);

// Expected output:
// Confidence type: "number"
// Confidence value: 0.627
// Is NaN?: false
// Display value: "63%"
```

---

## Testing Time Estimate

- **Quick test (items 1-3):** 2 minutes
- **Full test (all items):** 5 minutes
- **With screenshots:** 8 minutes
- **With DevTools inspection:** 10 minutes

---

## Next Steps After Testing

1. ✅ Verify all manual tests pass
2. ✅ Take screenshots of working confidence display
3. ✅ Document any remaining issues (should be none)
4. ✅ Ready for deployment

---

**Test Status:** Ready to execute
**Servers:** Both running (backend 8000, frontend 3000)
**Fix Applied:** Yes
**Expected Outcome:** No NaN%, all confidence values display correctly
