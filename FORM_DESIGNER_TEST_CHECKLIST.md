# Form Designer Testing Checklist

## Prerequisites
- [ ] Development server is running (`npm run dev`)
- [ ] Browser console is open (F12)
- [ ] No console errors on initial load

## Tab Creation
- [ ] Click "New Tab" button in the TabManager
- [ ] "Form Designer" option appears in the dropdown menu
- [ ] Clicking "Form Designer" creates a new tab
- [ ] Tab title shows "Form Designer 1" (increments for multiple tabs)
- [ ] Tab appears with correct styling

## FormDesignerView Component
- [ ] Component loads without errors
- [ ] Default tabs are visible: Designer, Preview, JSON Schema, UI Schema
- [ ] "Designer" tab is active by default

## Designer Tab
- [ ] FormBuilder component renders
- [ ] Visual form builder interface is visible
- [ ] Can drag and drop form elements (if supported by library)
- [ ] Can add new form fields
- [ ] Can edit field properties
- [ ] Changes to the form update the schema automatically
- [ ] No console errors when interacting with FormBuilder

## Preview Tab
- [ ] Clicking "Preview" tab switches view
- [ ] Form preview renders correctly based on current schema
- [ ] Form is functional (can fill in fields, submit, etc.)
- [ ] Preview updates when schema changes in Designer tab

## JSON Schema Tab
- [ ] Clicking "JSON Schema" tab shows Monaco editor
- [ ] Schema JSON is displayed and editable
- [ ] Changes in editor update the form preview
- [ ] Invalid JSON shows error alert
- [ ] Valid JSON updates preview correctly

## UI Schema Tab
- [ ] Clicking "UI Schema" tab shows Monaco editor
- [ ] UI Schema JSON is displayed and editable
- [ ] Changes in editor affect form rendering
- [ ] Invalid JSON shows error alert

## State Management
- [ ] Schema changes are tracked (tab shows dirty indicator *)
- [ ] Tab state persists when switching between tabs
- [ ] Multiple FormDesigner tabs can be open simultaneously
- [ ] Each tab maintains its own schema state

## Tab Operations
- [ ] Tab can be closed
- [ ] Tab can be saved (if save functionality is implemented)
- [ ] Tab can be duplicated (if duplication is implemented)
- [ ] Closing tab with unsaved changes prompts confirmation (if implemented)

## Error Handling
- [ ] Invalid schema JSON shows error message
- [ ] Component handles missing tab data gracefully
- [ ] Component handles parse errors gracefully
- [ ] No crashes when switching tabs rapidly

## Integration
- [ ] FormDesigner integrates with existing tab system
- [ ] Header component recognizes FormDesigner tab type
- [ ] Theme applies correctly to FormDesigner
- [ ] Styling matches app design system

## Browser Compatibility
- [ ] Test in Chrome/Edge
- [ ] Test in Firefox
- [ ] Test in Safari (if available)

## Performance
- [ ] Component loads in reasonable time (< 2 seconds)
- [ ] No memory leaks when opening/closing multiple tabs
- [ ] Smooth interactions with form builder

## Notes
- Test with different form complexities (simple forms, complex nested forms)
- Test with various field types (text, number, select, checkbox, etc.)
- Verify schema output matches expected format

