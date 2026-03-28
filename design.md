# Design Blueprint

Source reference captured from `https://www.stampmail.ai/` on 2026-03-28 using Firecrawl.

Goal: reproduce the same high-level landing-page UI structure, visual hierarchy, and component rhythm for this project.

## Brand Direction

- Style: modern SaaS, light theme, polished, product-first
- Tone conveyed by UI: calm, capable, premium, operator-focused
- Primary audience feel: busy professionals, founders, executives

## Design Tokens

### Colors

- Primary ink: `#001229`
- Accent blue: `#0145F2`
- Background: `#FFFFFF`
- Primary text/link emphasis: `#0145F2`
- Supporting neutrals: use soft gray borders and section dividers around product cards and pricing blocks

### Typography

- Primary font family: `Suisse`
- Fallback stack: `ui-sans-serif, system-ui, sans-serif`
- Visual behavior: bold geometric headlines, clean sans-serif body copy, generous whitespace

### Spacing + Shape

- Base spacing unit: `4px`
- Standard card/button radius: `8px`
- Primary CTA radius: `12px`
- Layout feel: wide sections, large vertical padding, centered content, screenshot-led composition

## Structural Rules

### Header

- Left-aligned wordmark/logo
- Right-aligned nav links
- Nav order: Features, Pricing, Contact, Sign In
- Primary CTA in header: Get Started
- Header should feel minimal, airy, and fixed to the top visual rhythm of the page

### Hero

- Short eyebrow-style headline above a larger promise
- Large value statement centered on the page
- One short supporting paragraph
- One clear CTA button
- Product screenshots immediately below the hero copy in a staggered multi-image strip

### Demo Section

- Demo callout label
- Play interaction as secondary action
- Large product screenshot/video still

### Feature Trio

- Three stacked value blocks, each using:
  - small category label
  - bold feature headline
  - short explanatory paragraph
- Messaging pattern:
  - autopilot / approval workflow
  - personal secretary / delegation
  - AI labeling / workflow learning

### Feature Gallery

- Section intro headline + supporting sentence + CTA
- Repeating screenshot cards with this pattern:
  - feature title
  - one-paragraph benefit copy
  - large screenshot directly underneath
- Use large full-width product visuals between text groupings

### Mobile App Section

- Single device-oriented showcase
- Availability message + app-store badges
- One large mobile product visual

### FAQ

- Section eyebrow plus clear FAQ title
- Accordion-style Q&A list
- Short, direct answers

### Final CTA

- Strong closing headline
- Trial-oriented supporting sentence
- Primary CTA button
- Decorative/product imagery adjacent to CTA

### Footer

- Brand mark/logo
- Link columns:
  - Pages
  - Company
  - Data
  - Media
- Copyright row at bottom

## Component Inventory

### Buttons

- Primary CTA:
  - background `#0145F2`
  - rounded corners `12px`
  - visually prominent, filled
- Secondary action:
  - darker ink treatment using `#001229`
  - lower emphasis than primary CTA

### Cards

- Screenshot-first cards
- Rounded edges
- Light borders or subtle containment
- Minimal shadow or no shadow

### Screenshots

- Product imagery is the dominant visual device
- Use multiple overlapping or sequential screenshots to create momentum
- Keep screenshots crisp and large; they do most of the persuasion work

### Pricing Blocks

- Three-column pricing structure
- Middle tier marked as recommended
- Toggle for monthly/yearly billing
- Each card includes plan name, audience fit, price, feature list, CTA

## Page Blueprints

### Homepage Blueprint

1. Header
2. Hero with centered copy and screenshot strip
3. Demo/video still
4. Three-value proposition block
5. Feature gallery with repeated screenshots
6. Mobile app callout
7. FAQ accordion
8. Final CTA
9. Footer

### Features Page Blueprint

1. Header
2. Features hero
3. Screenshot strip
4. Autopilot workflow callout
5. Long vertical feature gallery
6. Footer

### Pricing Page Blueprint

1. Header
2. Pricing hero
3. Monthly/yearly toggle
4. Three pricing cards
5. Screenshot strip reused below pricing
6. FAQ
7. Footer

## Implementation Guardrails

- Preserve a white/light background base
- Preserve strong blue brand accents
- Keep copy blocks short and headline-led
- Lead with screenshots before dense explanation
- Favor centered layouts and obvious CTA flow
- Maintain the same section order and page rhythm across homepage, features, and pricing

## Firecrawl Capture Summary

- Homepage value proposition: AI secretary for email and calendar
- Primary repeated CTA: Get Started
- Core themes: autopilot inbox, delegation, learned workflows, context-aware drafting, mobile access
- Navigation footprint discovered: home, features, pricing, privacy, terms, login/auth
