# Stampmail UI Scrape Reference

Captured from `https://www.stampmail.ai/` with Firecrawl on 2026-03-28.

This document records the UI structure and design signals we want to mirror in our own landing experience.

## Site Map

- `/`
- `/features`
- `/pricing`
- `/privacy`
- `/tos`
- `/login`

## Extracted Brand Signals

### Firecrawl branding output

- Color scheme: light
- Primary color: `#001229`
- Accent color: `#0145F2`
- Background: `#FFFFFF`
- Font: `Suisse`
- Base radius: `8px`
- Primary CTA radius: `12px`
- Design system hint: Tailwind

## Homepage Structure

### 1. Header

- Logo at left
- Links at right: Features, Pricing, Contact, Sign In
- Header CTA: Get Started

### 2. Hero

- Headline: `Email, handled.`
- Supporting promise: AI secretary that thinks like you
- One-line explanation under headline
- Primary CTA
- Four product screenshots directly under hero copy

### 3. Demo Block

- `Watch the Demo`
- Play action
- Large product visual/video still

### 4. Three Core Benefit Blocks

- `Inbox on Autopilot` / `Enter Stamp Mode`
- `Your Personal Secretary` / `Delegate Every Task`
- `Filter Out The Noise` / `Learns Your Workflows`

Pattern: short label, larger feature title, one concise paragraph.

### 5. Mid-page Feature Gallery

- Section intro: `Designed for doers`
- Supporting line: `Because time doesn't manage itself.`
- CTA to features page
- Repeating large screenshot + caption blocks

Observed feature cards:

- Automatic Replies
- Gathers Context
- Long Term Memories

### 6. Mobile Section

- `Stamp Mobile`
- App availability statement
- App Store + Play Store badges
- Large phone/mockup visual

### 7. FAQ

- Eyebrow: `Questions & Answers`
- Heading: `Frequently Asked Questions`
- Accordion list with multiple short questions

### 8. Final CTA

- Headline: `Ready To Transform Your Email?`
- Trial-oriented supporting copy
- CTA: `Get Started Today`

### 9. Footer

- Brand mark
- Link groups: Pages, Company, Data, Media
- Copyright row

## Features Page Structure

- Reuses the same header
- Hero focused on `Features Designed for Doers.`
- Same screenshot strip treatment
- Long vertical feature catalog with a large image for each capability
- Reuses product-first storytelling rather than abstract icon blocks

## Pricing Page Structure

- Hero with pricing title and short helper sentence
- Billing toggle for monthly/yearly
- Three plans laid out side-by-side
- Middle tier visually recommended
- Same FAQ + footer language pattern reused lower on page

## UX Patterns To Mirror

- Minimal header copy, strong CTA clarity
- Screenshot-heavy persuasion instead of icon-heavy persuasion
- Large visual breaks between sections
- Short copy blocks with strong hierarchy
- Section order that tells a simple story: promise -> proof -> features -> mobile -> FAQ -> CTA
- Repeated CTA language to reduce decision load

## Asset + Link Notes

- Logo asset: `stamp-full-950.8388102a.svg`
- Footer icon/logo variations reuse the same blue brand family
- External app-store badges are placed in the mobile section
- Social links surfaced in footer: LinkedIn, X/Twitter, YouTube

## Working Interpretation For Our Project

To match this reference closely, our landing page should use:

- a light polished SaaS aesthetic
- centered hero with compact copy
- a screenshot strip immediately visible above the fold
- repeated feature sections where the product image is the main proof
- a three-card pricing section with one recommended plan
- FAQ and final CTA anchored near the bottom

The exact implementation target is documented in `design.md`.
