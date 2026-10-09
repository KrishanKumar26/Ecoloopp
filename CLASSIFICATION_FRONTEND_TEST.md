# E-Waste Classification Frontend - Testing Guide

## Overview
Complete frontend interface for e-waste classification has been implemented on the `/scan` page.

## What Was Implemented

### 1. API Client Functions (`lib/api.ts`)
- ✅ `classifyItem()` - Submit item name and optional image for classification
- ✅ `getCategories()` - Get available e-waste categories
- ✅ `getClassificationHistory()` - Get user's classification history
- ✅ TypeScript interfaces for all classification data structures

### 2. Scan Page UI (`app/scan/page.tsx`)
- ✅ Item name input field (required)
- ✅ Image upload with file picker (optional)
- ✅ File validation (JPG, JPEG, PNG, WEBP, max 10MB)
- ✅ Image preview before submission
- ✅ Loading states during classification
- ✅ Error handling and display
- ✅ Classification results display with:
  - Category name
  - Confidence score with progress bar
  - Estimated weight
  - Safety tips (bullet list)
  - Special care warnings (highlighted)
- ✅ "Schedule Pickup" button (navigates to /pickups with classification_id)
- ✅ "Classify Another Item" button to reset form
- ✅ Baseline classifier warning banner
- ✅ Authentication check (redirects to login if not authenticated)

## Testing Steps

### Prerequisites
1. Backend server running: `http://127.0.0.1:8000`
2. Frontend server running: `http://localhost:3000`
3. User account registered and logged in

### Test 1: Authentication Check
1. Navigate to `http://localhost:3000/scan` without being logged in
2. **Expected**: Redirect to `/login` page
3. Log in with valid credentials
4. **Expected**: Redirect back to `/scan` page

### Test 2: Basic Classification (Item Name Only)
1. Navigate to `/scan` (while logged in)
2. **Expected**: See form with:
   - Baseline classifier warning banner (yellow)
   - Item name input field
   - Image upload section
   - "Classify Item" button
3. Enter item name: `iPhone 12`
4. Click "Classify Item"
5. **Expected**:
   - Loading spinner appears
   - After ~1 second, results display shows:
     - ✓ Success checkmark
     - Category: "Smartphone"
     - Confidence: ~85%
     - Estimated weight: ~0.17 kg
     - Safety tips (3-4 items)
     - Special care warning about battery
     - "Schedule Pickup" button
     - "Classify Another Item" button

### Test 3: Classification with Image Upload
1. Click "Classify Another Item" to reset form
2. Enter item name: `Dell Laptop`
3. Click "Choose File" button
4. Select a valid image file (JPG/PNG)
5. **Expected**:
   - File name appears next to button
   - Image preview displays below
6. Click "Classify Item"
7. **Expected**:
   - Same successful classification flow
   - Category: "Laptop"
   - Confidence: ~90%
   - Results include safety tips

### Test 4: File Validation
1. Reset form
2. Enter item name: `Monitor`
3. Try uploading an invalid file type (e.g., `.txt` or `.pdf`)
4. **Expected**: Error message: "Please upload a valid image file (JPG, JPEG, PNG, or WEBP)"
5. Try uploading a very large image (>10MB)
6. **Expected**: Error message: "File size must be less than 10MB"

### Test 5: Form Validation
1. Reset form
2. Leave item name empty
3. Click "Classify Item"
4. **Expected**: Browser validation message: "Please fill out this field"
5. Enter item name but leave it blank (spaces only)
6. Click "Classify Item"
7. **Expected**: Error message: "Please enter an item name"

### Test 6: Different E-Waste Categories
Test various item names to verify classifier coverage:

| Item Name | Expected Category | Expected Confidence |
|-----------|------------------|---------------------|
| `Samsung TV` | Television | ~90% |
| `HP Printer` | Printer | ~88% |
| `Computer Mouse` | Peripherals | ~75% |
| `AAA Battery` | Battery | ~95% |
| `Electric Kettle` | Small Appliance | ~70% |
| `Old Fridge` | Large Appliance | ~85% |
| `LED Bulb` | Lighting | ~80% |
| `Desktop Computer` | Desktop PC | ~90% |

### Test 7: Schedule Pickup Flow
1. Classify an item successfully
2. Click "Schedule Pickup" button
3. **Expected**:
   - Navigate to `/pickups` page
   - URL contains query param: `?classification_id=<uuid>`
   - (Pickup form will be implemented separately)

### Test 8: Reset and Retry
1. After viewing results, click "Classify Another Item"
2. **Expected**:
   - Form resets to initial state
   - Item name input cleared
   - No file selected
   - No preview shown
   - No results displayed
3. Classify a new item
4. **Expected**: Works normally

### Test 9: Loading State
1. Submit a classification
2. During the ~1 second API call:
   - **Expected**:
     - "Classify Item" button disabled
     - Text changes to "Classifying..."
     - Spinning loader icon appears
     - Cannot click "Reset" button

### Test 10: Error Handling
1. Stop the backend server: `Ctrl+C` in backend terminal
2. Try to classify an item
3. **Expected**:
   - Error message displays in red box
   - Error text: "Failed to fetch" or "Classification failed"
   - Form remains usable
4. Restart backend server
5. Try again
6. **Expected**: Works normally

## Visual Verification Checklist

### Layout
- ✅ Page header with title "E-Waste Classification"
- ✅ Subtitle explaining the feature
- ✅ Yellow warning banner about baseline classifier
- ✅ White card with form (shadow and rounded corners)
- ✅ Proper spacing between elements
- ✅ Responsive design (test on different screen sizes)

### Form Elements
- ✅ Item name input has red asterisk (required)
- ✅ Placeholder text in item name field
- ✅ "Choose File" button styled correctly
- ✅ File name appears after selection
- ✅ Image preview centered and properly sized
- ✅ Green "Classify Item" button, full width
- ✅ Gray "Reset" button appears when data entered

### Results Display
- ✅ Green checkmark icon centered
- ✅ "Classification Complete" heading
- ✅ Item name displayed
- ✅ Category shown with proper capitalization
- ✅ Confidence progress bar (green) with percentage
- ✅ Estimated weight displayed
- ✅ Safety tips as bullet list with green bullets
- ✅ Special care warning in orange box with ⚠️ icon
- ✅ Two buttons side-by-side at bottom

## API Integration Verification

### Request Format
```typescript
// Classification request
POST http://127.0.0.1:8000/api/classify
Headers: { Authorization: "Bearer <token>" }
Body: FormData {
  item_name: string,
  image?: File
}
```

### Response Format
```json
{
  "classification_id": "uuid",
  "item_name": "string",
  "category": "string",
  "confidence": 0.85,
  "estimated_weight_kg": 0.5,
  "safety_tips": ["tip1", "tip2"],
  "special_care_warning": "string or null",
  "image_url": "string or null",
  "classified_at": "2024-01-01T00:00:00"
}
```

## Known Behaviors (Not Bugs)

1. **Baseline Classifier Warning**: Always displayed - this is intentional to set expectations
2. **Image Upload**: Images are accepted but not processed (placeholder for future ML model)
3. **Confidence Scores**: Estimates from keyword matching, not real ML confidence
4. **Classification Speed**: Usually <1 second (keyword matching is fast)
5. **Category Names**: Use underscore_case from backend, displayed with proper formatting

## Next Steps (Future Enhancements)

1. **Pickup Form**: Implement `/pickups` page to accept classification_id from URL
2. **Classification History**: Add a section showing past classifications
3. **Category Browser**: Display available categories with examples
4. **Bulk Upload**: Allow multiple items at once
5. **Export Results**: Download classification results as PDF
6. **ML Model Integration**: Replace baseline classifier with trained model

## Success Criteria

All tests pass if:
- ✅ Authentication required and working
- ✅ Form accepts item name and optional image
- ✅ File validation prevents invalid uploads
- ✅ Loading states display correctly
- ✅ Classification results display all fields
- ✅ "Schedule Pickup" navigates with classification_id
- ✅ Reset functionality works
- ✅ Error handling graceful
- ✅ UI matches design specifications
- ✅ No console errors in browser DevTools

## Browser Testing
Test in:
- ✅ Chrome (primary)
- ✅ Safari (macOS)
- ✅ Firefox
- ✅ Mobile Safari (responsive)
- ✅ Mobile Chrome (responsive)

---

## Quick Test Command

```bash
# Ensure both servers are running
cd ~/Desktop/ecoloop/backend
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# In another terminal
cd ~/Desktop/ecoloop/frontend
npm run dev
```

Then visit: http://localhost:3000/scan

**Login credentials** (from previous testing):
- Email: test@example.com
- Password: password123

Or register a new account at: http://localhost:3000/register
