---
name: Vibrant Marketplace
colors:
  surface: '#fbf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fbf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae8e7'
  surface-container-highest: '#e4e2e1'
  on-surface: '#1b1c1c'
  on-surface-variant: '#5b4042'
  inverse-surface: '#303030'
  inverse-on-surface: '#f3f0f0'
  outline: '#8f6f72'
  outline-variant: '#e3bdc0'
  surface-tint: '#bd0043'
  primary: '#b90041'
  on-primary: '#ffffff'
  primary-container: '#df2457'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb2ba'
  secondary: '#5b5d6f'
  on-secondary: '#ffffff'
  secondary-container: '#dfe1f7'
  on-secondary-container: '#616376'
  tertiary: '#00685d'
  on-tertiary: '#ffffff'
  tertiary-container: '#008376'
  on-tertiary-container: '#f4fffb'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffd9dc'
  primary-fixed-dim: '#ffb2ba'
  on-primary-fixed: '#400011'
  on-primary-fixed-variant: '#910031'
  secondary-fixed: '#dfe1f7'
  secondary-fixed-dim: '#c3c5da'
  on-secondary-fixed: '#181b2a'
  on-secondary-fixed-variant: '#434657'
  tertiary-fixed: '#71f8e4'
  tertiary-fixed-dim: '#4fdbc8'
  on-tertiary-fixed: '#00201c'
  on-tertiary-fixed-variant: '#005048'
  background: '#fbf9f8'
  on-background: '#1b1c1c'
  surface-variant: '#e4e2e1'
typography:
  display:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Outfit
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Outfit
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Outfit
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Outfit
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  price-lg:
    fontFamily: Outfit
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  container-max: 1280px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style
This design system captures a high-energy, fashion-forward retail atmosphere. It utilizes a **Corporate Modern** style infused with **Minimalist** sensibilities to ensure the product remains the hero. The aesthetic is clean, trustworthy, and trendy, aimed at a style-conscious audience that expects a seamless, high-performance shopping experience. 

The interface relies on heavy white space and a precise typographic hierarchy to organize dense information, while using "Myntra Pink" as a strategic focal point for conversion and brand recognition.

## Colors
The palette is dominated by a crisp white foundation to allow product photography to pop. 
- **Primary Action:** The signature Pink (#FF3F6C) is reserved strictly for primary buttons, selection states, and brand-heavy moments.
- **Typography:** Dark Charcoal (#333333) provides high legibility for headings, while Medium Grey (#666666) is used for secondary metadata and descriptions.
- **Accents:** Indigo and Emerald are used for data visualization, price drops, or secondary badges to provide visual variety without competing with the primary brand color.
- **Status Badges:** Use a soft-tinted background (5-10% opacity of the base color) with high-contrast text for status indicators.

## Typography
Outfit is the sole typeface for this design system, chosen for its geometric clarity and modern, approachable feel. 
- **Headings:** Use bold weights (700) for product titles and section headers to create a strong vertical rhythm.
- **Body:** Standardize on 14px for general UI text to maintain a high information density typical of e-commerce.
- **Price Display:** Always use a bold weight for prices to ensure they are the first thing a user notices in a product card.
- **Labels:** Use uppercase for category tags and small badges to create visual distinction from body copy.

## Layout & Spacing
The layout follows a 12-column fluid grid for desktop and a 4-column grid for mobile. 
- **Grid:** Use a 16px gutter globally. 
- **Rhythm:** All spacing (padding/margins) must be multiples of 4px.
- **Margins:** Desktop views should maintain a generous 40px outer margin to keep the content centered and breathable. Mobile views should utilize a 16px margin to maximize screen real estate for product images.
- **Containers:** Content should be capped at a maximum width of 1280px for optimal readability on ultra-wide monitors.

## Elevation & Depth
Depth is created through **Tonal Layers** and **Ambient Shadows**.
- **Surface 0 (Background):** #F8F9FA (Subtle grey).
- **Surface 1 (Cards/Containers):** #FFFFFF (Pure white).
- **Shadows:** Use extremely soft, diffused shadows to lift cards from the background. Avoid heavy black shadows; instead, use a 4% - 8% opacity of the text color (#333333) with a large blur radius (12px - 20px) and a subtle Y-offset (4px).
- **Interactive States:** On hover, cards should slightly increase their shadow spread or lift (Y-offset) by 2px to signal interactivity.

## Shapes
The shape language is friendly and approachable.
- **Standard Cards:** Use a 16px corner radius (`rounded-lg` in this system) to create a soft, high-end feel.
- **Buttons & Inputs:** Use an 8px corner radius to maintain a structural, functional look.
- **Badges/Chips:** Use a fully rounded (pill-shaped) style for category tags and status indicators to differentiate them from functional buttons.

## Components
- **Buttons:** 
  - *Primary:* Solid #FF3F6C with white text. 8px border radius. Heavy bold weight.
  - *Secondary:* Transparent background with a 1px border of #D4D5D9. Text in #333333.
- **Cards:** 
  - White background, 16px radius, subtle 1px border (#F5F5F6) + soft shadow. 
  - Product cards should have no internal padding for the image container, but 12px-16px padding for the text/pricing area.
- **Input Fields:** 
  - 1px border (#D4D5D9), 8px radius. Use #94969F for placeholder text. On focus, the border color shifts to #333333 (not the primary pink, to keep the UI grounded).
- **Status Badges:** 
  - Small, pill-shaped, using the P1-P3 color tokens defined in the color section. Font size should be 10px-12px bold.
- **Lists:** 
  - Use 16px vertical padding for list items with a 1px horizontal separator in #F5F5F6.
- **Chips:** 
  - 4px padding (horizontal) and 2px (vertical) for small metadata tags, usually with a light grey background (#F0F0F0).