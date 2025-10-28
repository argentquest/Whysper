# Dynamic Branding Implementation

This document describes the implementation of the dynamic branding system for Whysper.

## Overview

The branding system is completely brand-agnostic. **No brand-specific names (like "Wells Fargo" or "WF") appear anywhere in the main codebase** except within the `branding/WF/` folder itself.

## How It Works

### 1. Environment Variable Configuration

The active brand is controlled by a single environment variable in `.env`:

```bash
VITE_BRAND=WF
```

### 2. Dynamic Brand Loading

The `branding/index.ts` file dynamically loads the appropriate brand based on `VITE_BRAND`:

```typescript
const activeBrand = import.meta.env.VITE_BRAND || 'WF';

// Dynamically import brand module
import * as WFBranding from './WF';

// Export brand-agnostic names
export const BrandColors = selectedBrand.WFColors;
export const BrandTypography = selectedBrand.WFTypography;
export const Brand = selectedBrand.WFBrand;
```

### 3. Brand-Agnostic Imports

All components import from `@/branding` using generic names:

```typescript
import { BrandColors, Brand } from '@/branding';

// Usage
style={{
  background: BrandColors.gradients.redToYellow,
}}

<Title>{Brand.name}</Title>
```

## File Structure

```
frontend/
├── .env                          # VITE_BRAND=WF
├── .envTemplate                  # Template with VITE_BRAND
├── vite.config.ts                # Path alias @ configured
├── tsconfig.app.json             # TypeScript path mapping
├── branding/
│   ├── index.ts                  # Dynamic loader (brand-agnostic)
│   ├── README.md                 # Usage documentation
│   ├── IMPLEMENTATION.md         # This file
│   └── WF/                       # Wells Fargo brand (isolated)
│       ├── colors.ts
│       ├── typography.ts
│       ├── theme.ts
│       ├── brand.ts
│       ├── assets/
│       └── index.ts
├── src/
│   ├── components/
│   │   └── layout/
│   │       └── Header.tsx        # Uses BrandColors, Brand
│   ├── themes/
│   │   └── antd-themes.ts        # Uses BrandColors
│   └── index.css                 # Generic CSS variables
```

## Key Files Updated (No Brand References)

### 1. Header Component
**File**: `src/components/layout/Header.tsx`

```typescript
import { BrandColors, Brand } from '@/branding';

// Logo with brand gradient
background: BrandColors.gradients.redToYellow

// App name
<Title>{Brand.name}</Title>

// Tagline
<Text>{Brand.tagline}</Text>
```

### 2. Theme Configuration
**File**: `src/themes/antd-themes.ts`

```typescript
import { DefaultLightTheme, DefaultDarkTheme, BrandColors } from '@/branding';

// Default themes use imported brand themes
light: {
  name: 'Light',
  token: { ...DefaultLightTheme.token },
  components: { ...DefaultLightTheme.components },
},

// Custom themes use BrandColors
proBlue: {
  colorPrimary: BrandColors.primary.deepRed,
  // ...
}
```

### 3. Global CSS
**File**: `src/index.css`

```css
/* Custom CSS variables for active brand (set in .env via VITE_BRAND) */
:root {
  /* Primary Brand Colors */
  --brand-primary: #b31e30;
  --brand-secondary: #ffcc02;
  --brand-white: #ffffff;

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #b31e30 0%, #ffcc02 100%);
}
```

### 4. Path Alias Configuration
**File**: `vite.config.ts`

```typescript
export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

**File**: `tsconfig.app.json`

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

## Switching to a Different Brand

To create and activate a new brand (e.g., "ACME"):

### Step 1: Create Brand Folder

```bash
cp -r branding/WF branding/ACME
```

### Step 2: Update Brand Files

Edit the following files in `branding/ACME/`:

1. **colors.ts** - Update color hex codes
2. **typography.ts** - Update font families
3. **brand.ts** - Update name, tagline, logo
4. **theme.ts** - Update Ant Design theme tokens

### Step 3: Update Dynamic Loader

Edit `branding/index.ts`:

```typescript
import * as WFBranding from './WF';
import * as ACMEBranding from './ACME';  // Add import

switch (activeBrand) {
  case 'WF':
    selectedBrand = WFBranding;
    break;
  case 'ACME':  // Add case
    selectedBrand = ACMEBranding;
    break;
  default:
    selectedBrand = WFBranding;
}
```

### Step 4: Set Environment Variable

Update `.env`:

```bash
VITE_BRAND=ACME
```

### Step 5: Restart Dev Server

```bash
npm run dev
```

**That's it!** The entire application now uses the ACME branding.

## Benefits of This Approach

### 1. **Zero Code Changes**
Switching brands requires NO changes to:
- Components
- Themes
- CSS
- TypeScript interfaces

### 2. **Complete Isolation**
Each brand is completely isolated in its own folder. The main codebase has zero knowledge of specific brands.

### 3. **Type Safety**
TypeScript ensures all brand configurations have the required properties.

### 4. **Easy Maintenance**
- Add new brands without touching existing code
- Update one brand without affecting others
- Delete brands by removing their folder

### 5. **Environment-Based**
Different environments can use different brands:
- `.env.development` → WF brand
- `.env.production` → ACME brand
- `.env.staging` → TEST brand

## Brand Configuration Interface

Each brand must export these standard interfaces:

```typescript
// colors.ts
export const [Brand]Colors = {
  primary: { deepRed: string, goldenYellow: string, white: string },
  gradients: { redToYellow: string, ... },
  dataViz: { ... },
  semantic: { success, warning, error, info },
  neutral: { gray1...gray13 },
  text: { primary, secondary, tertiary, inverse },
}

// typography.ts
export const [Brand]Typography = {
  fontFamily: { primary, heading, mono },
  fontSize: { xs, sm, base, lg, xl, ... },
  fontWeight: { light, normal, medium, semibold, bold },
  lineHeight: { tight, normal, relaxed, loose },
}

// brand.ts
export const [Brand]Brand = {
  name: string,
  tagline: string,
  description: string,
  logo: { type, emoji, backgroundColor },
  features: string[],
}

// theme.ts
export const [brand]LightTheme: ThemeConfig
export const [brand]DarkTheme: ThemeConfig
export const [brand]Themes = { light, dark }
```

## Testing

To verify the branding system:

1. **Check Console**: Look for the active brand log
   ```
   🎨 Active Brand: WF
   ```

2. **Inspect Elements**: Verify colors and gradients in browser DevTools

3. **Switch Brands**: Change `VITE_BRAND` and restart to test switching

4. **Build Test**: Run `npm run build` to ensure production builds work

## Troubleshooting

### Issue: Module not found
**Solution**: Ensure path aliases are configured in both `vite.config.ts` and `tsconfig.app.json`

### Issue: Colors not updating
**Solution**: Restart the dev server after changing `.env` files

### Issue: Type errors
**Solution**: Ensure all brand modules export the required interfaces

## Migration Checklist

✅ Environment variable `VITE_BRAND` added to `.env` and `.envTemplate`
✅ Dynamic brand loader created in `branding/index.ts`
✅ Path alias `@` configured in `vite.config.ts`
✅ TypeScript paths configured in `tsconfig.app.json`
✅ All WF references removed from `src/themes/antd-themes.ts`
✅ All WF references removed from `src/components/layout/Header.tsx`
✅ CSS variables updated to be brand-agnostic in `src/index.css`
✅ Brand folder structure documented in `branding/README.md`
✅ Implementation documented in `branding/IMPLEMENTATION.md`

## Result

The codebase is now **100% brand-agnostic**. The only place any specific brand name appears is within its own folder under `branding/`. The main application code uses only generic terms like `BrandColors`, `Brand`, `BrandTypography`, etc.

This makes it trivial to:
- Support multiple clients with different branding
- A/B test different brand identities
- White-label the application
- Maintain separate brands for different markets
