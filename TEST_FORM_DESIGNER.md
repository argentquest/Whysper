# Form Designer Testing Guide

## Quick Test Steps

### 1. Verify Servers are Running
- Backend: http://localhost:8003 (or check the port in backend config)
- Frontend: http://localhost:5173 (or check the terminal output)

### 2. Open the Application
- Navigate to the frontend URL in your browser
- You should see the landing page or existing tabs

### 3. Create a Form Designer Tab
- Click the "New Tab" button in the TabManager (top right)
- You should see a dropdown menu with options:
  - New Chat
  - Diagram Wizard
  - Form System
  - **Form Designer** ← New option

### 4. Test Form Designer Features

#### Tab Creation
- [ ] Click "Form Designer" from the dropdown
- [ ] A new tab appears with title "Form Designer 1"
- [ ] Tab shows a dirty indicator (*) when changes are made

#### FormDesignerView Interface
- [ ] Component loads without errors
- [ ] Four tabs are visible: Designer, Preview, JSON Schema, UI Schema
- [ ] "Designer" tab is active by default

#### Designer Tab (Visual Form Builder)
- [ ] FormBuilder component renders
- [ ] Visual interface is displayed
- [ ] Can interact with form builder (add fields, edit properties)
- [ ] Changes update the schema automatically
- [ ] Check browser console for any errors

#### Preview Tab
- [ ] Click "Preview" tab
- [ ] Form preview renders based on current schema
- [ ] Form is functional (can fill fields)
- [ ] Preview updates when schema changes

#### JSON Schema Tab
- [ ] Click "JSON Schema" tab
- [ ] Monaco editor displays the schema JSON
- [ ] Can edit the JSON directly
- [ ] Invalid JSON shows error alert
- [ ] Valid JSON updates the preview

#### UI Schema Tab
- [ ] Click "UI Schema" tab
- [ ] Monaco editor displays the UI schema JSON
- [ ] Can edit the UI schema
- [ ] Changes affect form rendering

### 5. Test State Management
- [ ] Make changes in Designer tab
- [ ] Tab shows dirty indicator (*)
- [ ] Switch to another tab and back - state persists
- [ ] Create multiple FormDesigner tabs - each maintains separate state

### 6. Error Scenarios
- [ ] Try entering invalid JSON in schema editors
- [ ] Verify error alerts appear
- [ ] Check browser console for any JavaScript errors

## Expected Behavior

### Successful Implementation
✅ FormDesigner tab creates successfully
✅ FormBuilder renders and is interactive
✅ All tabs work correctly
✅ Schema changes are tracked
✅ No console errors

### Potential Issues

#### If FormBuilder doesn't render:
- Check browser console for errors
- May need Bootstrap CSS (library has Bootstrap as peer dependency)
- Check if FormBuilder component is imported correctly

#### If styling looks broken:
- FormBuilder uses Bootstrap, which may conflict with Ant Design
- May need to add Bootstrap CSS imports

#### If tabs don't switch:
- Check for JavaScript errors in console
- Verify state management is working

## Browser Console Commands

Open browser DevTools (F12) and check:
```javascript
// Check if FormBuilder is loaded
console.log(typeof FormBuilder);

// Check for React errors
// Look for red error messages in console

// Check network tab for failed requests
```

## Manual Verification Checklist

1. ✅ Tab appears in "New Tab" dropdown
2. ✅ Tab creates successfully
3. ✅ FormDesignerView component renders
4. ✅ All four tabs (Designer, Preview, JSON Schema, UI Schema) work
5. ✅ FormBuilder component displays and functions
6. ✅ Schema changes are tracked (dirty state)
7. ✅ State persists when switching tabs
8. ✅ No console errors
9. ✅ Styling is acceptable (may need Bootstrap CSS)

## Next Steps if Issues Found

1. Check browser console for specific errors
2. Verify package installation: `npm list @ginkgo-bioworks/react-json-schema-form-builder`
3. Check if Bootstrap CSS is needed
4. Review component imports and props

