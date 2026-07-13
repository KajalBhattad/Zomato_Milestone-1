---
name: Crimson Obsidian
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#e4bebc'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#ab8987'
  outline-variant: '#5b403f'
  surface-tint: '#ffb3b1'
  primary: '#ffb3b1'
  on-primary: '#680011'
  primary-container: '#ff535a'
  on-primary-container: '#5b000e'
  inverse-primary: '#bb162c'
  secondary: '#c8c6c5'
  on-secondary: '#303030'
  secondary-container: '#474746'
  on-secondary-container: '#b7b5b4'
  tertiary: '#c8c6c6'
  on-tertiary: '#303030'
  tertiary-container: '#929090'
  on-tertiary-container: '#2a2a2a'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1b1b1c'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#e4e2e1'
  tertiary-fixed-dim: '#c8c6c6'
  on-tertiary-fixed: '#1b1c1c'
  on-tertiary-fixed-variant: '#474747'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base_unit: 8px
  container_max_width: 1440px
  gutter: 24px
  margin_desktop: 40px
  margin_mobile: 16px
---

## Brand & Style

The design system is engineered for a high-performance, AI-driven culinary exploration experience. It targets food enthusiasts who value speed, precision, and a premium aesthetic. The brand personality is "Technological Sophistication meets Gastronomy"—combining the visceral energy of dining with the calm, methodical nature of artificial intelligence.

The visual style is **Modern Minimalism** with a focus on high-contrast utility. It utilizes a dark, obsidian-based environment to allow food photography and AI-generated insights to pop with maximum vibrancy. The atmosphere is sleek and focused, reducing cognitive load through generous whitespace (even in dark mode) and a strict adherence to a "content-first" hierarchy.

## Colors

This design system utilizes a tiered dark-mode palette to create depth without relying on traditional shadows.
- **Base (Neutral):** #121212 is the canvas, providing a true-black foundation that grounds the UI.
- **Surface (Secondary):** #1E1E1E is used for primary containers like cards and input fields, creating a subtle lift from the background.
- **Elevated (Tertiary):** #2D2D2D is reserved for hover states and nested elements.
- **Action (Primary):** #E23744 (Zomato Crimson) is the sole driver of intent. It is used sparingly for buttons, active states, and critical AI indicators to ensure it retains its psychological impact.

## Typography

The typography strategy employs a dual-font approach to balance character with utility.
- **Outfit** is used for headlines and display text. Its geometric nature provides a modern, "tech-forward" feel that aligns with AI branding.
- **Inter** is used for all body text, data points, and labels. Its exceptional legibility at small sizes ensures that restaurant details and AI metrics are easily digestible.

Hierarchy is maintained through weight and color rather than just size. Primary information uses High-Emphasis White (#FFFFFF), while supporting metadata uses Medium-Emphasis Slate (#A1A1AA).

## Layout & Spacing

The design system follows an **8px linear scale** for all dimensions, ensuring mathematical harmony across the dashboard.

- **Grid:** A 12-column fluid grid is used for desktop, transitioning to a 4-column grid for mobile.
- **Dashboard Structure:** A fixed left-hand navigation rail (80px collapsed, 240px expanded) persists across the experience.
- **Safe Zones:** Content containers should maintain a minimum 24px internal padding to ensure the UI feels airy and premium.
- **AI Reflow:** When AI recommendations are generated, cards should utilize a masonry-style reflow on tablet and mobile to accommodate varying lengths of "Reasoning" text.

## Elevation & Depth

In this dark-mode environment, depth is communicated through **Tonal Elevation** and **Ghost Borders** rather than heavy shadows.

- **Level 0 (Base):** #121212.
- **Level 1 (Cards/Inputs):** #1E1E1E with a 1px solid border of #2D2D2D. This creates a "cut-out" look that is cleaner than traditional drop shadows.
- **Level 2 (Modals/Popovers):** #2D2D2D with a subtle 10% white inner-glow on the top edge to simulate a light source from above.
- **Transitions:** All elevation changes (e.g., hovering over a restaurant card) must use a 200ms `cubic-bezier(0.4, 0, 0.2, 1)` transition, slightly lightening the background color and increasing the border opacity.

## Shapes

The shape language is "Softly Geometric." A 0.5rem (8px) base radius is applied to all standard components (cards, inputs, buttons). This strikes a balance between the precision of a technical dashboard and the approachability of a food-service app.

- **Buttons:** 8px radius, except for Segmented Controls which use a 6px radius for internal items.
- **Restaurant Cards:** 12px (rounded-lg) to frame food photography more elegantly.
- **Search Bars:** Fully pill-shaped (rounded-full) to distinguish the primary entry point for AI queries.

## Components

### Buttons & Controls
- **Primary Button:** Solid #E23744 with white text. No gradient. On hover, the color shifts to a slightly deeper crimson.
- **Segmented Buttons:** A #1E1E1E track with a #2D2D2D "slider" indicating the active state. Text for the active state should be White; inactive should be Slate.
- **Sliders:** The track is #2D2D2D, while the active fill and the thumb are #E23744. The thumb should have a subtle white halo on hover.

### Inputs
- **Search Input:** A large, pill-shaped #1E1E1E field with a Crimson cursor. Placeholder text is Slate.
- **Filter Chips:** Outline style (#2D2D2D) when inactive; solid Crimson when active.

### Restaurant Cards
- **Structure:** 1px border (#2D2D2D). Image at the top with a subtle 10% black-to-transparent gradient overlay to ensure the "Match Score" (AI metric) is readable in the top-right corner.
- **AI Insight:** A dedicated section at the bottom of the card using a slightly different background tint (#252525) to highlight the AI's "Why this for you" reasoning.

### Status Indicators
- **AI Match Score:** Circular progress ring using Crimson for the percentage fill.
- **Availability:** Small dot indicator—Green (#22C55E) for "Open Now," Slate for "Closed."