---
name: Crystal AI
colors:
  surface: '#faf9f6'
  surface-dim: '#dbdad7'
  surface-bright: '#faf9f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f1'
  surface-container: '#efeeeb'
  surface-container-high: '#e9e8e5'
  surface-container-highest: '#e3e2e0'
  on-surface: '#1a1c1a'
  on-surface-variant: '#444654'
  inverse-surface: '#2f312f'
  inverse-on-surface: '#f2f1ee'
  outline: '#757686'
  outline-variant: '#c5c5d7'
  surface-tint: '#3250d5'
  primary: '#2f4ed2'
  on-primary: '#ffffff'
  primary-container: '#4c68ec'
  on-primary-container: '#fffbff'
  inverse-primary: '#b9c3ff'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fc'
  on-secondary-container: '#5c647a'
  tertiary: '#5c5c58'
  on-tertiary: '#ffffff'
  tertiary-container: '#757571'
  on-tertiary-container: '#fefcf7'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dee1ff'
  primary-fixed-dim: '#b9c3ff'
  on-primary-fixed: '#001258'
  on-primary-fixed-variant: '#0c34bd'
  secondary-fixed: '#dae2fc'
  secondary-fixed-dim: '#bec6df'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3e465b'
  tertiary-fixed: '#e4e2dd'
  tertiary-fixed-dim: '#c8c6c2'
  on-tertiary-fixed: '#1b1c19'
  on-tertiary-fixed-variant: '#474744'
  background: '#faf9f6'
  on-background: '#1a1c1a'
  surface-variant: '#e3e2e0'
typography:
  headline-xl:
    fontFamily: Geist
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-xl-mobile:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 30px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 26px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Geist
    fontSize: 17px
    fontWeight: '400'
    lineHeight: 28px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Geist
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-sm:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0.005em
  label-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0em
  label-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  code-inline:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style
The design system establishes a warm, editorial, and profoundly focused ambient interface tailored for high-cognition knowledge work, strategic inquiry, and deep synthesis. Departing from the sterile cold gray palettes and neon techno-futurism typical of modern AI utilities, this interface adopts an ivory paper tactile sensibility paired with the precision of contemporary minimalist typography. 

The aesthetic marries classical editorial calm with the responsiveness of modern generative platforms. Interfaces must feel serene, quiet, and deeply unhurried. Generous negative space acts as a functional buffer against cognitive fatigue, allowing text, code, and generative outputs to hold authoritative physical presence on the canvas. Visual noise is actively suppressed: decorative flourishes, heavy shadows, and harsh structural lines are excluded in favor of tonal surfaces, whispering hairline boundaries, and restrained slate-lavender accents.

## Colors
The color hierarchy is anchored by a warm paper ecosystem, punctuated only by a calm, calibrated slate-lavender tint for focal interactions and semantic states.

- **Background Canvas (`#FAF9F6`)**: The foundation of all views. A warm, non-glare alabaster ivory that softens long-form reading sessions.
- **Surface Elevation 1 (`#FFFFFF`)**: Pure warm white reserved for active conversational cards, elevated composer inputs, floating menus, and modals.
- **Surface Elevation 2 (`#F3F1EC`)**: Tonal stone beige applied to sidebars, inactive chips, contextual toolbars, system message bubbles, and nested code blocks.
- **Borders & Dividers (`#E6E3DD`)**: Hairline warm gray delineating structural divisions without creating visual friction.
- **Primary Text (`#202124`)**: Deep charcoal with warm undertones, yielding crisp contrast while avoiding the harsh pitch-black contrast ratio.
- **Secondary / Supporting Text (`#6B6B6B`)**: Neutralized stone gray for timestamps, secondary labels, metadata, and keyboard shortcuts.
- **Brand Accent (`#506CF0`)**: A restrained, desaturated slate-lavender blue used with intentional scarcity—reserved exclusively for active focus rings, send triggers, citation badges, and progressive streaming indicators.

## Typography
Geist serves as the primary typographic backbone across all roles, providing surgical geometric clarity, low tracking noise, and modern vertical alignment. 

- **Hierarchy & Proportion**: Generative responses and primary outputs rely on `body-lg` (17px with 28px leading), engineered to provide optimal optical tracking across multi-paragraph explanations and technical reads.
- **Monospace Pairing**: Technical syntaxes, inline tokens, model telemetry, and code snippets pair with `JetBrains Mono` at 13px, inheriting contextual baseline alignment without distorting paragraph line rhythms.
- **Optical Weighting**: Headlines remain restrained between 500 (Medium) and 600 (Semi-bold). Heavy, aggressive weights (700+) are avoided to preserve the soft, intellectual atmosphere of the interface.

## Layout & Spacing
The layout architecture centers around an editorial reading column calibrated for optimal line lengths (680px to 768px maximum content width for conversational threads), flanked by collapsible peripheral panels.

- **Grid & Columns**: A fluid multi-pane desktop arrangement composed of a 260px collapsible session sidebar, an infinite-feel center stage, and an optional 380px contextual inspector drawer. The active conversational thread is horizontally centered within the center stage to maintain consistent focal balance.
- **Rhythm & Padding**: Vertical spacing between assistant conversational turns conforms to `space-xl` (2.5rem), creating distinct semantic breaks without requiring horizontal rules. 
- **Adaptive Breakpoints**:
  - **Mobile (< 768px)**: The navigation sidebar transitions into a full-height off-canvas drawer. Outer margins compress to `margin-mobile` (1rem). The unified prompt composer anchors persistently to the viewport bottom with safe-area padding.
  - **Desktop (>= 1024px)**: Sidebar locks into fixed standard view; thread margins expand to `margin` (2rem) with spacious gutters around conversational clusters.

## Elevation & Depth
Elevation within this design system is rendered through tonal stepping and diffused ambient occlusion rather than synthetic directional drop shadows.

- **Tonal Stepping**: Depth is conveyed primarily through background tone shift:
  - Base layer canvas sits on `#FAF9F6`.
  - Recessed sections (sidebar, metadata panels, code container blocks) sit on `#F3F1EC`.
  - Floating elevated items (chat composer, interactive tooltips, dropdown menus) sit on `#FFFFFF`.
- **Ghost Outlines**: Every elevated element pairs its `#FFFFFF` surface with a 1px border of `#E6E3DD` (or `rgba(32, 33, 36, 0.06)`). This hairline boundary preserves clean spatial separation without dark outline artifacts.
- **Ambient Shadow**: Modals and floating prompt docks utilize an ultra-diffused, dual-layer ambient shadow:
  - `box-shadow: 0 4px 20px -2px rgba(32, 33, 36, 0.04), 0 12px 32px -4px rgba(32, 33, 36, 0.06);`
  - Zero colored or saturated shadows; shadows only mimic warm light falling through clean frosted glass onto parchment.

## Shapes
The shape language implements an intentional, calibrated 10px to 12px radius standard (`roundedness: 2`), delivering a warm, approachable human touch while avoiding juvenile pill-shaped exaggeration.

- **Primary Cards & Modals**: Standardized at `rounded-lg` (16px) to house complex multi-line generative responses and data tables with architectural posture.
- **Interactive Controls & Inputs**: Standardized at `rounded` (10px to 12px) across text inputs, prompt boxes, and interactive utility blocks.
- **Micro Elements**: Filter chips, inline citation tags, and small prompt recommendation pills utilize 8px to 10px rounding. Complete circular/pill rounding is strictly limited to avatar badges, status dots, and floating icon buttons (e.g., audio dictation or scroll-to-bottom buttons).

## Components

### Buttons
- **Primary**: Background `#506CF0`, text `#FFFFFF`, border none, 10px corner radius, padding `10px 18px`. Hover: `#435CD8`. Active state deepens slightly without transform jumps.
- **Secondary / Ghost**: Background `transparent`, text `#202124`, border 1px solid `#E6E3DD`, hover background `#F3F1EC`. 
- **Icon Actions (Copy, Regenerate, Edit)**: 32x32px square targets, 8px radius, text `#6B6B6B`, hover text `#202124`, hover background `#F3F1EC`.

### Prompt Input Composer
- Centered dock floating over the conversational canvas.
- Background `#FFFFFF`, 12px corner radius, border 1px solid `#E6E3DD`.
- Subtle elevation via ambient shadow token.
- Multi-line expanding textarea with 0px inner border, 15px font size, and placeholder in `#6B6B6B`.
- Integrated bottom utility bar holding model picker, attachment trigger, and a circular or 10px rounded primary send button.

### Chips & Citation Badges
- **Prompt Suggestion Chips**: Background `#FFFFFF`, border 1px solid `#E6E3DD`, text `#202124`, 8px radius, padding `6px 12px`. Hover shifts border to `#506CF0` with 10% opacity wash.
- **Citation Badges**: Background `#F3F1EC`, border 1px solid `#E6E3DD`, text `#6B6B6B`, font size `11px`, font weight `500`, 6px radius. Displays source index numbers or domain favicons.

### Lists & Chat Stream
- **User Message**: Aligned flush right or right-biased with a soft tonal shell: background `#F3F1EC`, border 1px solid `transparent`, text `#202124`, 12px radius.
- **Assistant Message**: Spans the full editorial width without a heavy enclosure, resting directly on canvas `#FAF9F6` with crisp typography, leading-relaxed line height, and actionable metadata at the tail.

### Input Fields & Controls
- **Form Inputs**: Background `#FFFFFF`, border 1px solid `#E6E3DD`, text `#202124`, padding `10px 14px`, 10px radius. Focus state adds 1px border `#506CF0` and a 3px ring of `rgba(80, 108, 240, 0.12)`.
- **Checkboxes & Radios**: 18px dimensions, 4px radius (checkbox) or circular (radio), border 1.5px solid `#E6E3DD`. Checked state transitions background to `#506CF0` with white vector checkmark.

### Cards & Code Blocks
- **Cards**: Background `#FFFFFF`, border 1px solid `#E6E3DD`, 12px radius, padding `16px 20px`.
- **Code Blocks**: Background `#F3F1EC`, border 1px solid `#E6E3DD`, 10px radius. Header strip contains language identifier in uppercase `label-sm` along with a quick-copy icon button. Code text set in `JetBrains Mono` (`code-inline`).