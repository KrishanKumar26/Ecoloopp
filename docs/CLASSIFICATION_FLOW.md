# E-Waste Classification User Flow

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  User visits /scan                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ Authenticated? │
        └───────┬────────┘
                │
        ┌───────┴───────┐
        │               │
       No              Yes
        │               │
        ▼               ▼
┌───────────────┐  ┌──────────────────────────────────────┐
│ Redirect to   │  │ Display Form                         │
│ /login        │  │ • Baseline Classifier Warning        │
└───────────────┘  │ • Item Name Input (required)         │
                   │ • Image Upload (optional)            │
                   │ • Classify Item Button               │
                   └──────────────┬───────────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────────────┐
                   │ User Enters Data                     │
                   │ • Types item name                    │
                   │ • (Optional) Selects image file      │
                   │ • Image preview appears              │
                   └──────────────┬───────────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────────────┐
                   │ File Validation (if image selected)  │
                   │ • Check file type (JPG/PNG/WEBP)     │
                   │ • Check file size (<10MB)            │
                   └──────────────┬───────────────────────┘
                                  │
                   ┌──────────────┴──────────────┐
                   │                             │
              Invalid                        Valid
                   │                             │
                   ▼                             ▼
        ┌──────────────────┐        ┌──────────────────────┐
        │ Show Error       │        │ User Clicks "Classify"│
        │ • Stay on form   │        └──────────┬───────────┘
        │ • Can try again  │                   │
        └──────────────────┘                   ▼
                              ┌────────────────────────────────┐
                              │ Loading State                  │
                              │ • Spinner animation            │
                              │ • "Classifying..." text        │
                              │ • Buttons disabled             │
                              └────────────┬───────────────────┘
                                           │
                                           ▼
                              ┌────────────────────────────────┐
                              │ API Call                       │
                              │ POST /api/classify             │
                              │ • Authorization: Bearer token  │
                              │ • Body: FormData (item + image)│
                              └────────────┬───────────────────┘
                                           │
                              ┌────────────┴────────────┐
                              │                         │
                         Success                    Error
                              │                         │
                              ▼                         ▼
            ┌─────────────────────────────┐  ┌────────────────────┐
            │ Display Results             │  │ Show Error Message │
            │ ✅ Success Icon             │  │ • Red alert box    │
            │ • Item Name                 │  │ • Error text       │
            │ • Category                  │  │ • Form still shown │
            │ • Confidence (progress bar) │  │ • Can retry        │
            │ • Estimated Weight          │  └────────────────────┘
            │ • Safety Tips (bullets)     │
            │ • Special Care Warning ⚠️   │
            │ • Schedule Pickup Button    │
            │ • Classify Another Button   │
            └────────────┬────────────────┘
                         │
            ┌────────────┴─────────────┐
            │                          │
  Schedule Pickup              Classify Another
            │                          │
            ▼                          ▼
┌────────────────────────┐  ┌──────────────────┐
│ Navigate to /pickups   │  │ Reset Form       │
│ ?classification_id=... │  │ • Clear inputs   │
└────────────────────────┘  │ • Remove preview │
                            │ • Hide results   │
                            │ • Ready for new  │
                            └──────────────────┘
```

## State Transitions

### Initial State
```
- Auth: Required ✓
- Form: Empty
- Preview: None
- Results: Hidden
- Error: None
```

### Data Entry State
```
- Auth: Validated ✓
- Form: Item name entered, image selected
- Preview: Image displayed
- Results: Hidden
- Error: None
```

### Loading State
```
- Auth: Validated ✓
- Form: Disabled
- Preview: Visible
- Results: Hidden
- Error: None
- Spinner: Visible ⏳
```

### Success State
```
- Auth: Validated ✓
- Form: Hidden
- Preview: Hidden
- Results: Displayed ✅
- Error: None
- Actions: Schedule Pickup, Classify Another
```

### Error State
```
- Auth: Validated ✓
- Form: Enabled
- Preview: Visible (if was selected)
- Results: Hidden
- Error: Displayed ❌
- Actions: Can retry
```

## Component Structure

```
<ScanPage>
├── <Navigation />
│   └── Shows auth state, user info
│
├── <main>
│   ├── Header
│   │   ├── Title: "E-Waste Classification"
│   │   └── Subtitle
│   │
│   ├── Baseline Classifier Warning Banner
│   │   └── Yellow alert with ⚠️ icon
│   │
│   └── {!result ? (
│       <Form>
│         ├── Item Name Input (required)
│         ├── Image Upload Section
│         │   ├── Choose File button
│         │   ├── File name display
│         │   └── Image preview
│         ├── Error Message (conditional)
│         └── Action Buttons
│             ├── Classify Item (primary)
│             └── Reset (secondary)
│       </Form>
│     ) : (
│       <Results>
│         ├── Success Header
│         │   ├── ✓ Icon
│         │   ├── "Classification Complete"
│         │   └── Item name
│         ├── Results Grid
│         │   ├── Category
│         │   ├── Confidence (progress bar)
│         │   ├── Estimated Weight
│         │   ├── Safety Tips (bullet list)
│         │   └── Special Care Warning (conditional)
│         └── Action Buttons
│             ├── Schedule Pickup (primary)
│             └── Classify Another (secondary)
│       </Results>
│     )}
│
└── <Footer />
```

## Data Flow

### Frontend → Backend
```typescript
// User Input
{
  item_name: "iPhone 12",
  image?: File
}

// Transform to FormData
const formData = new FormData();
formData.append('item_name', 'iPhone 12');
formData.append('image', fileObject);

// API Request
POST /api/classify
Headers: { Authorization: "Bearer <token>" }
Body: formData
```

### Backend → Frontend
```typescript
// API Response
{
  classification_id: "uuid-here",
  item_name: "iPhone 12",
  category: "smartphone",
  confidence: 0.85,
  estimated_weight_kg: 0.17,
  safety_tips: [
    "Remove SIM card before disposal",
    "Back up all data",
    "Factory reset the device"
  ],
  special_care_warning: "Contains lithium-ion battery. Handle with care.",
  image_url: null,
  classified_at: "2024-01-15T10:30:00Z"
}

// Display Transformations
- Category: "smartphone" → "Smartphone" (capitalize)
- Confidence: 0.85 → 85% (percentage)
- Weight: 0.17 → "0.17 kg" (with unit)
- Tips: Array → Bullet list with green bullets
- Warning: String → Orange alert box with ⚠️
```

## Error Scenarios and Handling

### 1. Not Authenticated
```
Trigger: User not logged in
Action: Auto-redirect to /login
Recovery: User logs in → redirected back to /scan
```

### 2. Invalid File Type
```
Trigger: User selects .txt or .pdf file
Action: Show error: "Please upload a valid image file"
Recovery: User selects valid image
UI: Error in red box, form stays enabled
```

### 3. File Too Large
```
Trigger: User selects >10MB file
Action: Show error: "File size must be less than 10MB"
Recovery: User selects smaller file
UI: Error in red box, form stays enabled
```

### 4. Empty Item Name
```
Trigger: User clicks submit with blank item name
Action: Browser validation: "Please fill out this field"
Recovery: User enters item name
UI: Native browser validation tooltip
```

### 5. API Network Error
```
Trigger: Backend server down or network issue
Action: Show error: "Failed to fetch" or "Classification failed"
Recovery: User can retry when backend is back
UI: Error in red box, form stays enabled
```

### 6. API Validation Error
```
Trigger: Backend rejects invalid data
Action: Show error from API: error.detail
Recovery: User corrects input and retries
UI: Error in red box, form stays enabled
```

### 7. Token Expired
```
Trigger: JWT token expired during classification
Action: Show error: "Not authenticated"
Recovery: User logs in again
UI: May need to redirect to /login
```

## Interaction Patterns

### Progressive Disclosure
1. Start: Simple form (item name + upload)
2. After upload: Preview appears
3. After submit: Loading state
4. After success: Full results replace form

### Reversible Actions
- Reset button: Clear form anytime during entry
- Classify Another: Go back to form from results
- File selection: Can change file before submit

### Visual Feedback
- Hover states: Buttons change color
- Focus states: Inputs show green ring
- Loading: Animated spinner
- Success: Green checkmark icon
- Error: Red alert box
- Warning: Yellow/orange alert boxes

### Keyboard Navigation
- Tab through form fields
- Enter to submit (when focused on input)
- Space to click buttons (when focused)
- Escape to blur input (browser default)

## Responsive Behavior

### Desktop (>1024px)
- Max width: 1024px centered
- Form: Single column, generous spacing
- Preview: Max width 512px centered
- Results: Full-width sections

### Tablet (768px - 1024px)
- Container: Padding adjusted
- Form: Same layout, narrower
- Preview: Proportionally smaller
- Results: Same layout

### Mobile (<768px)
- Container: Full width with edge padding
- Form: Stack all elements
- Preview: Full width, smaller height
- Results: Stack all sections
- Buttons: Stack vertically or full width

## Performance Considerations

### Image Preview
- Uses FileReader API (client-side)
- Preview generated before upload
- No server round-trip for preview
- Memory cleaned up on reset

### API Calls
- Single request per classification
- FormData for efficient file upload
- Loading state prevents double-submit
- Error recovery without data loss

### State Management
- Local React state (no Redux needed)
- Minimal re-renders
- Form controlled components
- Cleanup on unmount

## Accessibility Features

### Semantic HTML
- `<form>` for form submission
- `<label>` associated with inputs
- `<button>` for actions
- Proper heading hierarchy

### Screen Reader Support
- Labels on all inputs
- Required field indicators
- Error messages associated with fields
- Alt text on images

### Keyboard Support
- Tab navigation
- Enter to submit
- Spacebar to activate buttons
- Focus indicators visible

### Color Contrast
- Text meets WCAG AA standards
- Error messages high contrast
- Focus rings clearly visible
- Icons supplement color

## Integration Points

### With AuthContext
```typescript
const { user } = useAuth();
// Provides current user and token
// Handles redirect if not authenticated
```

### With API Client
```typescript
import { classifyItem } from '@/lib/api';
// Centralized API calls
// Type-safe interfaces
// Error handling
```

### With Navigation
```typescript
import { useRouter } from 'next/navigation';
// Programmatic navigation
// Query params for classification_id
// Redirect to login/pickups
```

### With Auth Token Storage
```typescript
const token = localStorage.getItem('token');
// JWT stored in localStorage
// Included in API Authorization header
// Checked for expiration
```

## Future Enhancement Ideas

### Phase 2 (Short-term)
1. **History Display**: Show past classifications below form
2. **Category Help**: Link to category descriptions
3. **Image Optimization**: Compress before upload
4. **Offline Support**: Queue classifications when offline

### Phase 3 (Medium-term)
1. **Bulk Upload**: Multiple items at once
2. **CSV Export**: Download classification history
3. **Share Results**: Generate shareable link
4. **Notifications**: Alert when classification complete

### Phase 4 (Long-term)
1. **ML Model**: Replace baseline classifier
2. **Real-time Camera**: Live camera classification
3. **AR Overlay**: Augmented reality guidance
4. **Multi-language**: Internationalization

---

**Current Status**: Phase 1 Complete ✅
**Ready for Testing**: Yes
**Ready for Production**: After user testing and QA
