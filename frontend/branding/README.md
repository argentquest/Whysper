# Whysper Branding System

This folder contains all branding configurations for the Whysper application. The branding system is designed to be modular and easily switchable between different brand identities.

## Structure

```
branding/
├── WF/                    # Wells Fargo branding (currently active)
│   ├── colors.ts         # Color palette and gradients
│   ├── typography.ts     # Font definitions
│   ├── theme.ts          # Ant Design theme configuration
│   ├── brand.ts          # Brand metadata and messaging
│   ├── assets/           # Logo, images, icons
│   └── index.ts          # Main export
└── index.ts              # Active brand selector
```

## Current Active Brand: Wells Fargo

The application is currently configured with Wells Fargo branding:

### Brand Colors
- **Deep Red**: `#b31e30` - Primary brand color (passion, energy, power)
- **Golden Yellow**: `#ffcc02` - Secondary brand color (wealth, prosperity, optimism)
- **White**: `#ffffff` - Background and contrast

### Color Psychology
- **Deep Red**: Symbolizes passion, energy, power, commitment, and dedication
- **Golden Yellow**: Represents wealth, prosperity, and optimism (Wells Fargo's gold rush heritage)

### Where Branding is Applied

1. **Header Component** ([src/components/layout/Header.tsx](../src/components/layout/Header.tsx))
   - Logo with red-to-yellow gradient background
   - Button gradients using brand colors
   - App name and tagline from brand config

2. **Theme System** ([src/themes/antd-themes.ts](../src/themes/antd-themes.ts))
   - All themes updated with WF colors
   - Primary color: Deep Red (#b31e30)
   - Warning color: Golden Yellow (#ffcc02)

3. **Global CSS** ([src/index.css](../src/index.css))
   - CSS variables for WF brand colors
   - Light and dark mode variations
   - Gradient definitions

## How to Use Branding in Components

### Import Brand Configuration

```typescript
// Import specific brand elements
import { WFColors } from '@/branding/WF/colors';
import { WFBrand } from '@/branding/WF/brand';
import { WFTypography } from '@/branding/WF/typography';

// Or import from the active brand
import { BrandColors, Brand, BrandTypography } from '@/branding';
```

### Use Brand Colors

```typescript
// Direct usage
style={{
  background: WFColors.primary.deepRed,
  color: WFColors.primary.goldenYellow,
}}

// Gradients
style={{
  background: WFColors.gradients.redToYellow,
}}

// Text colors
style={{
  color: WFColors.text.primary,
}}
```

### Use Brand Metadata

```typescript
// App name and tagline
<Title>{WFBrand.name}</Title>
<Text>{WFBrand.tagline}</Text>

// Logo
<span>{WFBrand.logo.emoji}</span>

// Version info
<Text>{WFBrand.version}</Text>
```

### Use CSS Variables

```css
/* In CSS files */
.custom-element {
  background: var(--wf-deep-red);
  color: var(--wf-golden-yellow);
  background-image: var(--gradient-primary);
}
```

## Switching Brands

To switch to a different brand identity:

1. **Create a new brand folder** (e.g., `branding/ACME/`)
2. **Copy the structure** from the `WF` folder
3. **Update the configuration files** with new colors, typography, and branding
4. **Update the main export** in `branding/index.ts`:

```typescript
// Change from WF to ACME
export {
  ACMEColors as BrandColors,
  ACMEBrand as Brand,
  // ... etc
} from './ACME';
```

5. **Rebuild the application** - all components will automatically use the new branding!

## Theme Configuration

The branding system integrates with Ant Design's theme system. Each brand can define:

- **Light Theme**: Optimized for light backgrounds
- **Dark Theme**: Optimized for dark backgrounds
- **Custom Themes**: Additional theme variants

Theme files are located in `WF/theme.ts` and are automatically imported into the main theme configuration.

## Best Practices

1. **Always use brand constants** instead of hardcoded colors
2. **Import from `branding/index.ts`** for easier brand switching
3. **Use semantic color names** (primary, secondary) over specific colors
4. **Document new brand additions** in this README
5. **Test both light and dark themes** when adding new branding

## Data Visualization Colors

Wells Fargo provides additional colors for charts and data visualization:

```typescript
WFColors.dataViz.studentLoans      // #E84E2A - Orange-Red
WFColors.dataViz.dailyExpenses     // #F9A655 - Orange
WFColors.dataViz.nonStudentLoans   // #B8B8B8 - Gray
WFColors.dataViz.retirement        // #8B4F9F - Purple
WFColors.dataViz.healthCare        // #C4B5E8 - Lavender
WFColors.dataViz.other             // #2C2968 - Navy
```

## Support

For questions or issues related to branding:
1. Review the configuration files in `branding/WF/`
2. Check the implementation in `Header.tsx` and `antd-themes.ts`
3. Consult the Wells Fargo brand guidelines (if available)

## Version History

- **v2.0.0**: Initial Wells Fargo branding implementation
  - Modular branding system
  - Complete color palette
  - Typography definitions
  - Ant Design theme integration
