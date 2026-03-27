# PRD: Fix Tailwind v4 Setup + Add shadcn/ui Component Library

**GitHub Issue**: [#20](https://github.com/rznies/autonomous-communication-manager/issues/20)

## Problem Statement

The frontend renders as unstyled HTML because Tailwind CSS v4.2.2 is installed but configured with v3 syntax. The `@tailwind` directives, `tailwind.config.js`, and missing Vite plugin mean the Tailwind compiler never runs. All utility classes (`bg-*`, `text-*`, `flex`, `grid`, etc.) are ignored by Vite. Additionally, the UI uses custom `div`+class compositions for cards, buttons, badges, and other primitives that should come from a component library.

## Solution

Fix Tailwind v4 with the `@tailwindcss/vite` plugin and CSS-first config, then add shadcn/ui for production-quality component primitives. Replace Material Symbols with Lucide React icons for tree-shaking and consistency. Refactor existing components (Dashboard, Sidebar, TopBar, Layout) to use shadcn Card, Badge, Button, Avatar, Separator, ScrollArea, Dialog, Sheet, DropdownMenu, Tooltip, Tabs, and Skeleton.

## User Stories

1. As a developer, I want Tailwind CSS utility classes to compile correctly via Vite, so that the UI renders with proper styling instead of unstyled HTML
2. As a developer, I want to configure Tailwind v4 using CSS-first `@theme` blocks instead of a JS config file, so that the setup follows v4 conventions
3. As a developer, I want shadcn/ui installed with the `--vite` flag, so that path aliases and component generation work with my Vite project
4. As a developer, I want Lucide React as the icon library, so that icons are tree-shakeable and consistent with shadcn/ui defaults
5. As a developer, I want my existing Material Symbol icon references replaced with Lucide equivalents, so that the icon library is uniform across the app
6. As a developer, I want the Dashboard metric cards wrapped in shadcn `Card` components, so that they have consistent spacing, borders, and theming
7. As a developer, I want the queue item priority labels (HIGH/MED/LOW) rendered as shadcn `Badge` variants, so that severity levels are visually distinct
8. As a developer, I want the Approve and Edit Draft buttons replaced with shadcn `Button` variants (`outline` and `secondary`), so that buttons have consistent sizing, hover states, and accessibility
9. As a developer, I want the user avatar in the TopBar replaced with shadcn `Avatar`, so that fallback initials render when the image fails
10. As a developer, I want the sidebar navigation wrapped in shadcn `ScrollArea`, so that overflow content scrolls with a styled scrollbar
11. As a developer, I want section dividers in the sidebar and activity feed using shadcn `Separator`, so that visual boundaries are consistent
12. As a developer, I want a shadcn `Dialog` for the approve confirmation flow, so that destructive actions require explicit user confirmation
13. As a developer, I want shadcn `Sheet` available for future slide-out panels (contact details, action history), so that the component is ready when those views are built
14. As a developer, I want shadcn `DropdownMenu` available for the topbar user profile and notification actions, so that overflow menus are accessible
15. As a developer, I want shadcn `Tooltip` for icon-only buttons (notifications, sidebar items), so that users understand actions on hover
16. As a developer, I want shadcn `Tabs` for the Analytics and Contacts placeholder views, so that content switching follows a consistent pattern
17. As a developer, I want shadcn `Skeleton` for loading states on the Dashboard, so that the UI doesn't flash empty content while fetching from the API
18. As a developer, I want the custom color tokens (Material You dark palette) preserved in the Tailwind v4 `@theme` block, so that the existing design language is maintained
19. As a developer, I want a `@/` path alias configured in `vite.config.js` and `jsconfig.json`, so that shadcn component imports resolve correctly
20. As a developer, I want `tailwind.config.js` deleted, so that there's no confusion about which config system is active
21. As a user, I want the Dashboard to look like a polished dark-mode dashboard after the refactor, so that the app feels professional and trustworthy
22. As a user, I want smooth hover transitions on queue item cards, so that the UI feels responsive
23. As a user, I want the approve action to show a confirmation dialog before executing, so that I don't accidentally approve drafts

## Implementation Decisions

### Modules to build/modify

| Module | Action | Details |
|--------|--------|---------|
| `vite.config.js` | Modify | Add `@tailwindcss/vite` plugin + `@` path alias |
| `jsconfig.json` | Create | Path alias `@/*` → `src/*` |
| `index.css` | Rewrite | `@import "tailwindcss"` + `@theme` block with all color tokens |
| `tailwind.config.js` | Delete | v4 uses CSS config |
| `lib/utils.js` | Create | shadcn `cn()` utility (clsx + tailwind-merge) |
| `components.json` | Create | shadcn project config |
| `components/ui/*` | Create | 12 shadcn components |
| `Dashboard.jsx` | Refactor | Card, Badge, Button, Skeleton, Dialog |
| `Sidebar.jsx` | Refactor | Button, ScrollArea, Separator, Lucide icons |
| `TopBar.jsx` | Refactor | Avatar, Button, Tooltip, Lucide icons |
| `Layout.jsx` | Minor update | Remove Material Symbols import |

### Architecture decisions
- **Tailwind v4 CSS-first config**: All design tokens in `@theme {}` block inside `index.css`. No JS config file.
- **shadcn/ui components**: Copied into `src/components/ui/` — not a package dependency. Fully owned code.
- **Icon migration**: Replace all `material-symbols-outlined` with Lucide React `<Icon />` components. Remove Material Symbols font link from `index.html`.
- **Color tokens**: Preserve the existing Material You dark palette (60+ tokens). These move from `tailwind.config.js` → CSS `@theme` block.
- **Component organization**: shadcn `ui/` folder for primitives, existing `components/` for app-level compositions (Layout, Sidebar, TopBar).

### API contracts
No backend changes. The frontend continues to call `http://127.0.0.1:8000/api/metrics`, `/api/queue`, `/api/queue/{id}/approve`.

### Schema changes
None.

## Testing Decisions

- **Visual regression**: After each component refactor, screenshot the Dashboard and verify it matches the original design
- **API integration**: Verify `/api/metrics` and `/api/queue` data still renders correctly in the refactored Dashboard
- **Interactive elements**: Verify Approve button triggers the confirm dialog, Edit Draft button is clickable, sidebar nav links route correctly
- **Responsive layout**: Screenshot at 375px, 768px, and 1280px to confirm the grid layout adapts
- **Dark mode**: Verify all shadcn components respect the dark theme (no light-mode flashes)
- **Loading state**: Verify Skeleton components appear while API data is fetching

No automated test framework is set up in this project. Manual visual QA via browser screenshots.

## Out of Scope

- Backend changes (API server stays as-is)
- Building the Analytics and Contacts views (they remain placeholder divs)
- Adding a test framework (Jest/Vitest setup)
- Performance optimization or bundle analysis
- Accessibility audit beyond what shadcn/ui provides by default
- Mobile-specific responsive redesign (current layout works at tablet+, not mobile-first)

## Further Notes

- The `@tailwindcss/vite` plugin replaces both PostCSS and autoprefixer — no separate postcss config needed
- shadcn/ui v4 support via `--vite` flag is stable for Vite + React projects
- Lucide React is ~1400 icons, all tree-shakeable — only imported icons are bundled
- The existing `mono-numeric`, `glass-panel` utility classes and scrollbar styles in `index.css` must be preserved during the rewrite
