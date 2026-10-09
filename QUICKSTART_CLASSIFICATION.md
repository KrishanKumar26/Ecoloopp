# Quick Start: Test E-Waste Classification Frontend

## 🚀 Ready to Test!

Both servers are running and the classification frontend is complete. Follow this guide to test the new feature.

## ✅ Pre-flight Check

```bash
# Backend status
curl http://127.0.0.1:8000/health
# Should return: {"status":"healthy"}

# Frontend status
curl http://localhost:3000 -s -o /dev/null -w "%{http_code}"
# Should return: 200
```

## 🎯 Testing Steps (5 minutes)

### Step 1: Login (1 min)
1. Open browser: **http://localhost:3000/login**
2. Use existing account or register new one:
   - Email: `test@example.com`
   - Password: `password123`
3. Click "Sign In"
4. ✅ Should see home page with your name in navigation

### Step 2: Navigate to Scan Page (30 sec)
1. Click "Scan E-Waste" in navigation menu
2. Or go directly to: **http://localhost:3000/scan**
3. ✅ Should see:
   - Yellow warning banner: "Baseline Classifier"
   - Form with item name input
   - Image upload button
   - "Classify Item" button

### Step 3: Test Basic Classification (1 min)
1. Enter item name: `iPhone 12`
2. Click "Classify Item"
3. ✅ Wait ~1 second, should see:
   - Green checkmark ✓
   - "Classification Complete"
   - Category: "Smartphone"
   - Confidence: ~85% (with green progress bar)
   - Estimated Weight: ~0.17 kg
   - Safety tips (3-4 bullet points)
   - Orange warning box about battery
   - Two buttons: "Schedule Pickup" and "Classify Another Item"

### Step 4: Test with Image Upload (1 min)
1. Click "Classify Another Item"
2. Enter item name: `Dell Laptop`
3. Click "Choose File"
4. Select any image from your computer (JPG/PNG)
5. ✅ Should see:
   - Image preview below the file picker
   - File name displayed
6. Click "Classify Item"
7. ✅ Should see classification results (category: "Laptop")

### Step 5: Test File Validation (30 sec)
1. Click "Classify Another Item"
2. Enter item name: `Monitor`
3. Try uploading a non-image file (e.g., .txt, .pdf)
4. ✅ Should see red error: "Please upload a valid image file (JPG, JPEG, PNG, or WEBP)"
5. Form should remain usable

### Step 6: Test Different Categories (1 min)
Try these item names and verify categories:

| Item Name | Expected Category | Expected Confidence |
|-----------|------------------|---------------------|
| `Samsung TV` | Television | ~90% |
| `HP Printer` | Printer | ~88% |
| `AAA Battery` | Battery | ~95% |
| `Computer Mouse` | Peripherals | ~75% |
| `Old Fridge` | Large Appliance | ~85% |

### Step 7: Test Schedule Pickup Navigation (30 sec)
1. After any classification completes
2. Click "Schedule Pickup" button
3. ✅ Should navigate to `/pickups` page
4. ✅ URL should contain: `?classification_id=<some-uuid>`

## 🎨 Visual Verification

### Form Layout
- [ ] Yellow warning banner at top
- [ ] Item name input with placeholder text
- [ ] "Choose File" button (gray background)
- [ ] File name appears when selected
- [ ] Image preview centered and properly sized
- [ ] Green "Classify Item" button (full width)
- [ ] Gray "Reset" button (appears when data entered)

### Loading State
- [ ] Spinner animation visible
- [ ] Button text changes to "Classifying..."
- [ ] Button disabled (grayed out)

### Results Display
- [ ] Green checkmark icon in circle
- [ ] "Classification Complete" heading
- [ ] All sections properly separated
- [ ] Progress bar for confidence is green
- [ ] Safety tips have green bullet points
- [ ] Orange warning box (if hazardous materials)
- [ ] Two buttons side by side

### Responsive Design
- [ ] Try on mobile size (DevTools → responsive mode)
- [ ] All elements stack properly
- [ ] No horizontal scrolling
- [ ] Buttons readable and clickable

## 🧪 Edge Cases to Test

### Authentication
```
1. Log out (click user dropdown → Sign Out)
2. Try to access http://localhost:3000/scan
3. ✅ Should redirect to /login
4. Log back in
5. ✅ Should work normally
```

### Form Validation
```
1. Leave item name empty
2. Click "Classify Item"
3. ✅ Browser validation: "Please fill out this field"
```

### Error Recovery
```
1. Stop backend server: Ctrl+C in backend terminal
2. Try to classify an item
3. ✅ Red error box: "Failed to fetch" or similar
4. ✅ Form stays usable
5. Restart backend: uvicorn main:app --host 127.0.0.1 --port 8000 --reload
6. Try again
7. ✅ Should work normally
```

### Reset Functionality
```
1. Enter item name + select image
2. Click "Reset"
3. ✅ Item name cleared
4. ✅ File selection cleared
5. ✅ Preview removed
6. ✅ Ready for new input
```

## 📸 Screenshot Checklist

Take screenshots of:
1. [ ] Initial form (empty state)
2. [ ] Form with data entered + preview
3. [ ] Loading state (with spinner)
4. [ ] Classification results (success state)
5. [ ] Error state (file validation error)
6. [ ] Mobile responsive view

## 🐛 Common Issues & Solutions

### Issue: "Not authenticated" error
**Solution**: Make sure you're logged in. Check if token exists:
```javascript
// Open browser console
localStorage.getItem('token')
// Should return a JWT token string
```

### Issue: Image preview not showing
**Solution**:
- Check file size (<10MB)
- Check file type (JPG, PNG, WEBP only)
- Try different image file

### Issue: Classification takes too long
**Solution**:
- Check backend logs for errors
- Verify database connection
- Should normally complete in <1 second

### Issue: Results not displaying
**Solution**:
- Check browser console for errors (F12)
- Verify API response in Network tab
- Check backend logs

### Issue: "Schedule Pickup" does nothing
**Solution**:
- This is expected - /pickups page not yet implemented
- It should navigate but show empty/placeholder page
- Check URL contains `?classification_id=...`

## 📊 Success Criteria

All features working if:
- ✅ Authentication required
- ✅ Form accepts item name (required)
- ✅ Image upload works (optional)
- ✅ File validation prevents invalid types
- ✅ Preview displays before submit
- ✅ Loading state shows during API call
- ✅ Results display all classification data
- ✅ Safety tips and warnings highlighted
- ✅ "Schedule Pickup" navigates correctly
- ✅ "Classify Another" resets form
- ✅ No JavaScript errors in console
- ✅ Mobile responsive

## 🔍 DevTools Inspection

### Check Network Tab
1. Open DevTools (F12) → Network tab
2. Submit a classification
3. Look for request: `POST /api/classify`
4. ✅ Status: 200 OK
5. ✅ Response contains classification data

### Check Console Tab
1. Open DevTools (F12) → Console tab
2. Navigate to /scan and use the feature
3. ✅ No red error messages
4. ✅ No warning messages (except expected React DevTools)

### Check Application Tab
1. Open DevTools (F12) → Application tab
2. Look at Local Storage
3. ✅ Should see `token` key with JWT value
4. This is how authentication persists

## 🎉 What to Expect

### Working Features
✅ Item name input with validation
✅ Image upload with preview
✅ File type and size validation
✅ Loading states and animations
✅ Complete classification results
✅ Safety tips and warnings
✅ Schedule pickup navigation
✅ Form reset functionality
✅ Error handling and recovery
✅ Authentication enforcement
✅ Responsive mobile design

### Known Limitations
⚠️ **Baseline Classifier**: Uses keyword matching, not ML
⚠️ **Images**: Accepted but not processed (future ML feature)
⚠️ **Confidence**: Estimates, not real ML confidence scores
⚠️ **/pickups Page**: Not yet implemented (shows placeholder)

## 🚦 Testing Status

| Feature | Status | Notes |
|---------|--------|-------|
| Authentication | ✅ Ready | Redirects work |
| Item name input | ✅ Ready | Validation working |
| Image upload | ✅ Ready | Preview functional |
| File validation | ✅ Ready | Type & size checks |
| Classification API | ✅ Ready | Backend working |
| Results display | ✅ Ready | All fields shown |
| Safety tips | ✅ Ready | Bullet list format |
| Special warnings | ✅ Ready | Orange alert box |
| Schedule pickup | ✅ Ready | Navigation works |
| Form reset | ✅ Ready | Clean state |
| Error handling | ✅ Ready | Graceful degradation |
| Loading states | ✅ Ready | Spinner + disabled |
| Mobile responsive | ✅ Ready | Tested in DevTools |
| TypeScript types | ✅ Ready | No errors |
| Compilation | ✅ Ready | No warnings |

## 🎓 Next Steps After Testing

1. **Document Issues**: Note any bugs or UX problems
2. **User Feedback**: Have team members test
3. **Performance**: Monitor API response times
4. **Analytics**: Track classification success rate
5. **Iterate**: Based on user feedback

## 💡 Pro Tips

### Test with Real E-Waste Items
Try realistic item names:
- "2018 MacBook Pro 13-inch"
- "Samsung Galaxy S10 broken screen"
- "Old desktop computer tower"
- "CRT TV from 1990s"
- "Microwave oven not working"

### Verify Baseline Classifier Logic
The classifier matches keywords:
- "phone" → Smartphone
- "laptop" → Laptop
- "monitor" → Monitor
- "printer" → Printer
- "battery" → Battery

### Check Different Browsers
Test in:
- Chrome (primary)
- Safari (macOS)
- Firefox
- Mobile Safari (responsive mode)

---

## 🔗 Quick Links

- **Frontend**: http://localhost:3000/scan
- **Login**: http://localhost:3000/login
- **Register**: http://localhost:3000/register
- **Backend API Docs**: http://127.0.0.1:8000/docs
- **Backend Health**: http://127.0.0.1:8000/health

## 📝 Testing Checklist

Copy this checklist for your testing session:

```
[ ] Login successful
[ ] Navigation to /scan works
[ ] Warning banner displays
[ ] Item name input works
[ ] Image file picker works
[ ] Image preview shows
[ ] File validation catches invalid types
[ ] Classification request sends
[ ] Loading state displays
[ ] Results display correctly
[ ] Category shows properly
[ ] Confidence bar renders
[ ] Weight displayed
[ ] Safety tips listed
[ ] Special warnings shown (when applicable)
[ ] "Schedule Pickup" navigates
[ ] "Classify Another" resets form
[ ] No console errors
[ ] Mobile responsive
[ ] All data persists correctly
```

---

**Start Time**: _________
**End Time**: _________
**Status**: ✅ Pass / ❌ Fail / ⚠️ Issues Found

**Issues Found**:
1. _______________________
2. _______________________
3. _______________________

**Overall Assessment**: _______________________
