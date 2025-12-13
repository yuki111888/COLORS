# Color Palette Brand Guidelines

## Overview
This document outlines the color palette and usage guidelines for the brand.

## Primary Colors

### FIRE RED

**Hex:** `#e70000`  
**RGB:** `rgb(231, 0, 0)`  
**HSL:** `hsl(0.0, 100.0%, 45.3%)`  
**CSS Variable:** `var(--color-fire-red)`

**Usage:**
- Primary brand color
- Use for key CTAs and important elements
- Maintains brand identity

**Shades Available:**
- 50 (lightest) to 900 (darkest)
- Access via CSS variable: `var(--color-fire-red-[50-900])`

---

### ROYAL PURPLE

**Hex:** `#2a075b`  
**RGB:** `rgb(42, 7, 91)`  
**HSL:** `hsl(265.0, 85.7%, 19.2%)`  
**CSS Variable:** `var(--color-royal-purple)`

**Usage:**
- Primary brand color
- Use for key CTAs and important elements
- Maintains brand identity

**Shades Available:**
- 50 (lightest) to 900 (darkest)
- Access via CSS variable: `var(--color-royal-purple-[50-900])`

---

### NIGHT BLACK

**Hex:** `#0a0a0a`  
**RGB:** `rgb(10, 10, 10)`  
**HSL:** `hsl(0.0, 0.0%, 3.9%)`  
**CSS Variable:** `var(--color-night-black)`

**Usage:**
- Primary brand color
- Use for key CTAs and important elements
- Maintains brand identity

**Shades Available:**
- 50 (lightest) to 900 (darkest)
- Access via CSS variable: `var(--color-night-black-[50-900])`

---

### BRIGHT WHITE

**Hex:** `#ffffff`  
**RGB:** `rgb(255, 255, 255)`  
**HSL:** `hsl(0.0, 0.0%, 100.0%)`  
**CSS Variable:** `var(--color-bright-white)`

**Usage:**
- Primary brand color
- Use for key CTAs and important elements
- Maintains brand identity

**Shades Available:**
- 50 (lightest) to 900 (darkest)
- Access via CSS variable: `var(--color-bright-white-[50-900])`

---


## Usage Guidelines

### Do's
- Use primary colors for brand elements and CTAs
- Use lighter shades (50-300) for backgrounds
- Use medium shades (400-600) for primary actions
- Use darker shades (700-900) for text and emphasis
- Maintain sufficient contrast ratios for accessibility (WCAG AA minimum)

### Don'ts
- Don't use colors that clash with the brand palette
- Don't use colors at full opacity on light backgrounds without consideration
- Don't mix too many colors in a single design
- Don't use dark shades on dark backgrounds

## CSS Usage

Import the palette CSS file:
```css
@import 'palette.css';
```

Use CSS variables:
```css
.my-element {
    background-color: var(--color-fire-red);
    color: var(--color-fire-red-900);
}
```

Use utility classes:
```html
<div class="bg-fire-red text-white">Content</div>
```

## Accessibility

All color combinations should meet WCAG 2.1 Level AA contrast requirements:
- Normal text: 4.5:1 contrast ratio
- Large text: 3:1 contrast ratio
- UI components: 3:1 contrast ratio

Test your color combinations using tools like:
- WebAIM Contrast Checker
- Chrome DevTools Accessibility panel
