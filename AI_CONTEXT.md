# EcoLoop — AI Context & Classification Guide

**Service:** Python + FastAPI  
**Location:** `/ai/`  
**Model:** Vision-based image classification (e.g., fine-tuned MobileNetV3 or GPT-4o Vision API)

---

## Purpose

The AI service receives one or more images of electronic waste, classifies the item(s) into a normalized category, estimates weight, and returns safety tips. It is called by the backend via an internal HTTP endpoint — it is not directly accessible to the frontend.

---

## E-Waste Categories (Normalized)

| Category ID | Display Name         | Examples                                      |
|-------------|----------------------|-----------------------------------------------|
| `MOBILE`    | Mobile Phone         | Smartphones, feature phones                   |
| `LAPTOP`    | Laptop               | Notebooks, ultrabooks, Chromebooks            |
| `TABLET`    | Tablet               | iPads, Android tablets, e-readers             |
| `DESKTOP`   | Desktop Computer     | Tower PCs, all-in-ones                        |
| `MONITOR`   | Monitor / Display    | LCD, LED, CRT screens                         |
| `TV`        | Television           | LED, OLED, Plasma, CRT TVs                    |
| `PRINTER`   | Printer / Scanner    | Inkjet, laser, multifunction devices          |
| `KEYBOARD`  | Keyboard / Mouse     | Wired and wireless peripherals                |
| `BATTERY`   | Battery              | Lithium-ion, lead-acid, NiMH packs            |
| `CABLE`     | Cable / Charger      | USB, HDMI, power adapters                     |
| `APPLIANCE` | Small Appliance      | Microwaves, fans, hair dryers                 |
| `CIRCUIT`   | Circuit Board / PCB  | Motherboards, RAM, GPUs                       |
| `UNKNOWN`   | Unknown              | Unidentified or unclear item                  |

---

## AI Response Contract

The AI service must return this exact JSON structure to the backend:

```json
{
  "classification_id": "uuid-generated-by-service",
  "category": "MOBILE",
  "confidence_score": 0.92,
  "safety_tips": [
    "Remove the battery before handling if possible.",
    "Do not puncture or crush lithium-ion batteries.",
    "Store in a cool, dry place away from heat sources."
  ],
  "estimated_weight_kg": 0.18,
  "raw_label": "Samsung Galaxy S series smartphone"
}
```

---

## Safety Tips Library

Safety tips are selected based on the classified category. Each category has at least 3 tips.

### MOBILE / TABLET
- Remove the battery before handling if possible.
- Do not puncture or crush lithium-ion batteries.
- Keep away from heat sources; risk of fire or explosion.
- Wipe personal data before handing over.

### LAPTOP / DESKTOP
- Power off completely and unplug before handling.
- Do not drop; hard drives may contain recoverable data — wipe securely.
- Handle LCD screens carefully to avoid mercury exposure (older models).
- Remove lithium battery if accessible.

### MONITOR / TV (CRT)
- CRT monitors contain lead — do not break the glass.
- Wear protective gloves when handling CRTs.
- Do not incinerate; toxic phosphor compounds are present.

### MONITOR / TV (Flat Panel)
- LCD backlights may contain mercury — avoid crushing.
- Handle screens by the frame, not the display surface.

### BATTERY
- Never puncture, crush, or incinerate batteries.
- Store in a fireproof container if damaged or swollen.
- Do not mix battery chemistries in the same container.
- Keep away from children.

### PRINTER / SCANNER
- Remove ink or toner cartridges before transport.
- Avoid skin contact with toner powder — irritant.

### CABLE / CHARGER
- Check for frayed wires; damaged cables can cause electric shock.
- Bundle cables loosely to avoid stress on connectors.

### CIRCUIT / PCB
- Contains heavy metals (lead, cadmium, arsenic) — wear gloves.
- Do not burn or grind; toxic fumes are released.
- Handle in a static-safe environment.

### UNKNOWN
- Treat as potentially hazardous until identified.
- Do not attempt to disassemble.
- Contact a certified recycler for assessment.

---

## CO₂ Impact Calculation

CO₂ savings per kg by category (approximate emission factors):

| Category  | CO₂ Saved (kg per kg recycled) |
|-----------|---------------------------------|
| MOBILE    | 70                              |
| LAPTOP    | 25                              |
| DESKTOP   | 20                              |
| MONITOR   | 15                              |
| TV        | 12                              |
| BATTERY   | 8                               |
| CIRCUIT   | 50                              |
| CABLE     | 5                               |
| APPLIANCE | 6                               |
| DEFAULT   | 10                              |

**Formula:**  
`co2_saved_kg = estimated_weight_kg × emission_factor[category]`

---

## Confidence Score Thresholds

| Score Range | Behavior                                           |
|-------------|----------------------------------------------------|
| ≥ 0.80      | Auto-accept; show result to user with high confidence tag |
| 0.60–0.79   | Show result with "Please confirm this looks right" prompt |
| < 0.60      | Flag as `UNKNOWN`; ask user to retake photo or describe item |

---

## Model Integration Options

### Option A: OpenAI GPT-4o Vision (MVP / Hackathon)
- Send base64-encoded image + system prompt to GPT-4o.
- Parse structured JSON from the model response.
- Fast to integrate; no training required.

**System Prompt Template:**
```
You are an expert e-waste classifier. Analyze the provided image and return a JSON object with:
- category: one of [MOBILE, LAPTOP, TABLET, DESKTOP, MONITOR, TV, PRINTER, KEYBOARD, BATTERY, CABLE, APPLIANCE, CIRCUIT, UNKNOWN]
- confidence_score: float between 0 and 1
- estimated_weight_kg: float, your best estimate
- safety_tips: array of 3-5 safety handling instructions
- raw_label: a brief description of what you see

Respond ONLY with valid JSON. Do not include any explanation outside the JSON.
```

### Option B: Custom Fine-Tuned Model
- Train MobileNetV3 or EfficientNet on an e-waste image dataset.
- Serve via TorchServe or ONNX Runtime.
- Higher accuracy for specific categories; requires labeled training data.

---

## Internal API Endpoint

`POST /internal/classify`  
Called by the backend only. Not exposed publicly.

**Request:** `multipart/form-data` with `images[]`  
**Response:** JSON as per the AI Response Contract above.

---

## Error Handling

| Scenario             | Response                                               |
|----------------------|--------------------------------------------------------|
| No image provided    | `400 { "error": "NO_IMAGE" }`                          |
| Image unreadable     | `422 { "error": "UNPROCESSABLE_IMAGE" }`               |
| Model timeout (>5s)  | `504 { "error": "CLASSIFICATION_TIMEOUT" }`            |
| Unexpected error     | `500 { "error": "INTERNAL_ERROR" }`                    |
