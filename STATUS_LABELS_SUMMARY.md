# SSE Status → Frontend Label Complete Mapping

## At a Glance: All 20+ Statuses

### **PHASE 1: ANALYSIS & CLARIFICATION**
| Status | Frontend Label | Message | UI |
|--------|---|---|---|
| `started` | Starting Analysis | ℹ️ "AI received your request..." | Info |
| `analyzing` | Analyzing System | ℹ️ "AI is analyzing..." | Info |
| `analysis_complete` | Analysis Complete | ✅ "Analysis complete..." | Success |
| `clarifying` | Needs Clarification | ℹ️ "AI needs more info..." | Info |
| `clarification_received` | Processing Input | ℹ️ "Clarification received..." | Info |
| `clarification_ready` | Ready for More | ✅ "Clarification ready..." | Success |
| `can_proceed` | Ready to Proceed | ✅ "Has sufficient info..." | Success |
| `waiting` | Processing... | 🔇 "⏳ AI is processing..." | **Console only** |

### **PHASE 1.5: ARCHITECTURE PARSING**
| Status | Frontend Label | Message | UI |
|--------|---|---|---|
| `generating_json` | Preparing Data | ⏳ "Preparing structured data..." | Loading |
| `json_generated` | Data Ready | ✅ "JSON ready..." | Success |
| `type_selection` | Select Diagram Type | ℹ️ "Select diagram type..." | Info |
| `diagram_type_determined` | Type Selected | ✅ "Using [Type]..." | Success |

### **PHASE 2: CODE GENERATION & VALIDATION**
| Status | Frontend Label | Message | UI |
|--------|---|---|---|
| `generating` | Generating Code | ⏳ "Generating diagram code..." | Loading |
| `code_generated` | Code Ready | ✅ "Code is ready..." | Success |
| `validating` | Validating Code | 🔇 (none) | **Silent** |
| `refining` | Refining Code | ⚠️ "Refining diagram code..." | Warning |
| `fallback_fix` | Fixing Errors | ⚠️ "Refining diagram code..." | Warning |
| `code_refined` | Code Fixed | ✅ "Refinements applied..." | Success |

### **PHASE 3: RENDERING**
| Status | Frontend Label | Message | UI |
|--------|---|---|---|
| `rendering` | Rendering SVG | 🔇 (none) | **Silent** |
| `rendered` | Preview Ready | 🔇 (none) | **Silent** |

### **TERMINAL STATES**
| Status | Frontend Label | Message | UI |
|--------|---|---|---|
| `completed` | Complete! ✅ | ✅ "Diagram generated successfully!" | **Success + Save** |
| `error` | Error ❌ | ❌ "Error: [message]" | **Error Alert** |

---

## Key Points

🎯 **Total Statuses: 20+**

📊 **Distribution:**
- Phase 1 (Analysis): 8 statuses
- Phase 1.5 (Architecture): 4 statuses  
- Phase 2 (Generation): 6 statuses
- Phase 3 (Rendering): 2 statuses
- Terminal: 2 statuses

🔔 **Message Types:**
- **ℹ️ Info (Blue)**: Auto-dismiss, informational
- **⏳ Loading**: Spinner, stays visible
- **✅ Success (Green)**: Auto-dismiss, positive
- **⚠️ Warning (Orange)**: Auto-dismiss, caution
- **❌ Error (Red)**: Stays visible, requires action
- **🔇 Silent**: Console log only, no UI notification

⚡ **Special Cases:**
- `waiting`: Console-only log (prevents UI spam)
- `validating`: Silent operation
- `rendering`/`rendered`: UI updates automatically

---

## Complete Code Reference

**File:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx`
**Lines:** 232-345

Each status is handled in a switch statement that:
1. Sets the current phase (1, 2, or 3)
2. Sets whether in analysis phase
3. Shows appropriate message or logs to console

---

## User Experience Flow

```
User selects model
    ↓
User enters description
    ↓
[started] → [analyzing] → [analysis_complete]
    ↓
[clarifying] ↔ (Q&A loop) ↔ [clarification_ready]
    ↓
[can_proceed] (user clicks proceed)
    ↓
[generating_json] → [json_generated]
    ↓
[type_selection] → [diagram_type_determined]
    ↓
[generating] → [code_generated]
    ↓
[validating] (silent) → [refining] (if needed) → [code_refined]
    ↓
[rendering] (silent) → [rendered] (silent)
    ↓
[completed] ✅ or [error] ❌
```

Between each status, `[waiting]` may appear (console only) if LLM takes >60 seconds.

---

See these files for details:
- `SSE_STATUS_FRONTEND_LABELS.md` - Detailed breakdown
- `SSE_STATUS_REFERENCE.md` - All status descriptions
- `QUICK_STATUS_REFERENCE.txt` - Quick lookup table
