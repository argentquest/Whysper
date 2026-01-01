# Whysper Branding System - Complete Guide

## Overview

Whysper uses a **server-controlled, build-time branding system** that allows you to:
- Control branding from the backend `.env` file
- Switch brands without touching any code
- Maintain type safety and performance
- Support multiple brand identities

## Architecture

### Backend Controls Branding

The backend `.env` file contains:
```bash
ACTIVE_BRAND="WF"
```

This is exposed via the `/api/v1/settings` endpoint:
```json
{
  "activeBrand": "WF",
  "theme": "light",
  "timeout": 120,
  ...
}
```

### Frontend Uses Branding

The frontend has two ways to get the active brand:

#### Option 1: Build-Time (Recommended)
Set in `frontend/.env`:
```bash
VITE_BRAND=WF
```

The brand is loaded at module initialization in `branding/index.ts`:
```typescript
const activeBrand = import.meta.env.VITE_BRAND || 'WF';
```

#### Option 2: Runtime (Advanced)
Fetch from backend API (already implemented in `src/api/settings.ts`):
```typescript
import { getActiveBrand } from '@/api/settings';
const brand = await getActiveBrand();  // Returns "WF"
```

## File Structure

```
Whysper/
├── backend/
│   ├── .env                          # ACTIVE_BRAND=WF
│   └── app/
│       ├── core/
│       │   └── config.py             # Loads ACTIVE_BRAND
│       └── services/
│           └── settings_service.py   # Exposes activeBrand
│
├── frontend/
│   ├── .env                          # VITE_BRAND=WF
│   ├── branding/
│   │   ├── index.ts                  # Dynamic brand loader
│   │   ├── WF/                       # Wells Fargo brand
│   │   │   ├── colors.ts
│   │   │   ├── typography.ts
│   │   │   ├── theme.ts
│   │   │   ├── brand.ts
│   │   │   └── assets/
│   │   └── README.md
│   └── src/
│       ├── api/
│       │   └── settings.ts           # Backend settings API
│       ├── components/
│       │   └── layout/
│       │       └── Header.tsx        # Uses branding
│       └── themes/
│           └── antd-themes.ts        # Uses branding
```

## How to Switch Brands

### Step 1: Create New Brand Folder

```bash
cd frontend/branding
cp -r WF ACME
```

### Step 2: Update Brand Configuration

Edit files in `frontend/branding/ACME/`:

**colors.ts**:
```typescript
export const ACMEColors = {
  primary: {
    blue: '#0066CC',
    orange: '#FF6600',
    white: '#ffffff',
  },
  gradients: {
    blueToOrange: 'linear-gradient(135deg, #0066CC 0%, #FF6600 100%)',
  },
  // ... rest of colors
};
```

**brand.ts**:
```typescript
export const ACMEBrand = {
  name: 'ACME Corp',
  tagline: 'Innovation Delivered',
  logo: {
    type: 'emoji',
    emoji: '🚀',
    backgroundColor: '#0066CC',
  },
  // ... rest of brand config
};
```

### Step 3: Update Brand Loader

Edit `branding/index.ts`:
```typescript
// Import all available brands
import * as WFBranding from './WF';
import * as ACMEBranding from './ACME';  // Add this

// Select the active brand
switch (activeBrand) {
  case 'WF':
    selectedBrand = WFBranding;
    break;
  case 'ACME':  // Add this
    selectedBrand = ACMEBranding;
    break;
  default:
    selectedBrand = WFBranding;
}
```

### Step 4: Update Environment Variables

**Backend** (`backend/.env`):
```bash
ACTIVE_BRAND="ACME"
```

**Frontend** (`frontend/.env`):
```bash
VITE_BRAND=ACME
```

### Step 5: Rebuild

```bash
cd frontend
npm run dev
```

That's it! The entire application now uses ACME branding.

## Brand Configuration Requirements

Each brand folder must export these interfaces:

### colors.ts
```typescript
export const [Brand]Colors = {
  primary: { /* primary colors */ },
  gradients: { /* gradient definitions */ },
  dataViz: { /* chart colors */ },
  semantic: { success, warning, error, info },
  neutral: { gray1...gray13 },
  text: { primary, secondary, tertiary, inverse },
};
```

### typography.ts
```typescript
export const [Brand]Typography = {
  fontFamily: { primary, heading, mono },
  fontSize: { xs, sm, base, lg, ... },
  fontWeight: { light, normal, medium, semibold, bold },
  lineHeight: { tight, normal, relaxed, loose },
};
```

### brand.ts
```typescript
export const [Brand]Brand = {
  name: string,
  tagline: string,
  description: string,
  logo: { type, emoji, backgroundColor },
  features: string[],
};
```

### theme.ts
```typescript
export const [brand]LightTheme: ThemeConfig;
export const [brand]DarkTheme: ThemeConfig;
export const [brand]Themes = { light, dark };
```

## Usage in Components

All components import from `branding` using generic names:

```typescript
import { BrandColors, Brand, BrandTypography } from 'branding';

// Use brand colors
<div style={{ background: BrandColors.gradients.redToYellow }}>
  {Brand.name}
</div>

// Use brand metadata
<Title>{Brand.name}</Title>
<Text>{Brand.tagline}</Text>
<img src={Brand.logo.emoji} />
```

## Benefits

✅ **Server-Controlled** - Change `ACTIVE_BRAND` in backend `.env`
✅ **No Code Changes** - Switch brands via environment variables only
✅ **Type-Safe** - Full TypeScript support
✅ **Performance** - No runtime overhead, brand compiled into bundle
✅ **Maintainable** - Each brand completely isolated
✅ **Scalable** - Add unlimited brands

## Deployment Scenarios

### Scenario 1: Single Brand (Production)
```bash
# backend/.env
ACTIVE_BRAND="WF"

# frontend/.env
VITE_BRAND=WF
```

Build once, deploy everywhere with WF branding.

### Scenario 2: Multi-Brand (Different Environments)
```bash
# Development
ACTIVE_BRAND="WF"
VITE_BRAND=WF

# Staging
ACTIVE_BRAND="ACME"
VITE_BRAND=ACME

# Production
ACTIVE_BRAND="ACME"
VITE_BRAND=ACME
```

Build different bundles for each environment.

### Scenario 3: White-Label SaaS
Build separate Docker images for each client:
```dockerfile
# Dockerfile.wf
ENV ACTIVE_BRAND=WF
ENV VITE_BRAND=WF

# Dockerfile.acme
ENV ACTIVE_BRAND=ACME
ENV VITE_BRAND=ACME
```

## Testing Brand Switching

1. **Update backend `.env`**:
   ```bash
   ACTIVE_BRAND="ACME"
   ```

2. **Update frontend `.env`**:
   ```bash
   VITE_BRAND=ACME
   ```

3. **Restart both servers**:
   ```bash
   # Backend
   cd backend
   python main.py

   # Frontend
   cd frontend
   npm run dev
   ```

4. **Verify** in browser console:
   ```
   🎨 Active Brand: ACME
   ```

5. **Check API response**:
   ```bash
   curl http://localhost:8003/api/v1/settings
   ```
   Should show:
   ```json
   {
     "activeBrand": "ACME",
     ...
   }
   ```

## Troubleshooting

### Brand Not Changing
- Clear browser cache
- Restart Vite dev server (it caches environment variables)
- Check console for `🎨 Active Brand: ...` message

### TypeScript Errors
- Ensure all brand exports match the required interfaces
- Run `npm run type-check` to verify

### Module Not Found
- Verify path aliases in `vite.config.ts` and `tsconfig.app.json`
- Check that `branding` folder is in `frontend/` directory

## API Reference

### Backend Endpoints

**GET `/api/v1/settings`**
Returns application settings including active brand:
```json
{
  "activeBrand": "WF",
  "theme": "light",
  "timeout": 120,
  "values": { ... },
  "masked": { ... }
}
```

### Frontend API

**`import { BrandColors } from 'branding'`**
```typescript
BrandColors.primary.deepRed      // "#b31e30"
BrandColors.gradients.redToYellow  // "linear-gradient(...)"
```

**`import { Brand } from 'branding'`**
```typescript
Brand.name          // "Whysper"
Brand.tagline       // "AI Code Assistant"
Brand.logo.emoji    // "🧠"
```

**`import { BrandTypography } from 'branding'`**
```typescript
BrandTypography.fontFamily.primary  // Font stack
BrandTypography.fontSize.lg         // "18px"
```

## Summary

The Whysper branding system provides **server-controlled, type-safe, performant** branding that can be switched via environment variables without any code changes. The backend controls which brand is active, and the frontend builds with that brand compiled in for optimal performance.
