# Issues: Tailwind v4 + shadcn/ui Implementation

**Parent PRD**: [#20](https://github.com/rznies/autonomous-communication-manager/issues/20)

## Issue Breakdown

### Slice 1: Tailwind v4 foundation + shadcn/ui init + icon swap
**Issue**: [#21](https://github.com/rznies/autonomous-communication-manager/issues/21)
**Type**: AFK | **Blocked by**: None

Set up the Tailwind v4 build pipeline and component library foundation:
- Install `@tailwindcss/vite`, add to `vite.config.js`
- Rewrite `index.css` — `@import "tailwindcss"` + `@theme` block with all 60+ color tokens
- Delete `tailwind.config.js`
- Create `jsconfig.json` with `@/*` path alias
- Initialize shadcn/ui with `--vite` flag
- Install all 12 shadcn components: Card, Badge, Button, Avatar, Separator, ScrollArea, Dialog, Sheet, DropdownMenu, Tooltip, Tabs, Skeleton
- Install Lucide React, remove Material Symbols from `index.html`

**Acceptance criteria**:
- [ ] `@tailwindcss/vite` installed and in `vite.config.js` plugins
- [ ] `index.css` uses `@import "tailwindcss"` (v3 directives removed)
- [ ] All 60+ color tokens preserved in CSS `@theme` block
- [ ] Custom utilities (`.mono-numeric`, `.glass-panel`, scrollbar) preserved
- [ ] `tailwind.config.js` deleted
- [ ] `jsconfig.json` with `@/*` → `src/*` alias
- [ ] shadcn initialized, `components.json` + `lib/utils.js` created
- [ ] All 12 components in `src/components/ui/`
- [ ] Lucide React installed
- [ ] Material Symbols font link removed from `index.html`
- [ ] Dev server starts without errors

**User stories**: 1, 2, 3, 4, 5, 19, 20

---

### Slice 2: Dashboard refactor — Card, Badge, Button, Skeleton, Dialog
**Issue**: [#22](https://github.com/rznies/autonomous-communication-manager/issues/22)
**Type**: AFK | **Blocked by**: #21

Refactor `Dashboard.jsx` to use shadcn/ui primitives instead of raw `div` compositions.

**Acceptance criteria**:
- [ ] Metric cards (IDRR, Automated Actions, Agent Load) wrapped in `Card`
- [ ] Priority labels (HIGH/MED/LOW) rendered as `Badge` variants
- [ ] Approve button uses `Button variant="outline"`
- [ ] Edit Draft button uses `Button variant="secondary"`
- [ ] Approve opens `Dialog` confirmation before API call
- [ ] `Skeleton` shown during initial API loading
- [ ] All Material Symbols replaced with Lucide icons
- [ ] API data from `/api/metrics` and `/api/queue` renders correctly
- [ ] Smooth hover transitions on queue cards
- [ ] No console errors

**User stories**: 6, 7, 8, 12, 17, 21, 22, 23

---

### Slice 3: Sidebar refactor — ScrollArea, Separator, Lucide icons
**Issue**: [#23](https://github.com/rznies/autonomous-communication-manager/issues/23)
**Type**: AFK | **Blocked by**: #21

Refactor `Sidebar.jsx` to use shadcn/ui primitives.

**Acceptance criteria**:
- [ ] Navigation wrapped in `ScrollArea`
- [ ] Bottom divider uses `Separator`
- [ ] New Task button uses shadcn `Button`
- [ ] All icons use Lucide React (`Inbox`, `BarChart3`, `Contact`, `HelpCircle`, `FileText`, `Plus`, `Bot`)
- [ ] Active nav link styling preserved
- [ ] NavLink routing works (Queue, Analytics, Contacts)
- [ ] No console errors

**User stories**: 10, 11, 15

---

### Slice 4: TopBar refactor — Avatar, Button, Tooltip, Lucide icons
**Issue**: [#24](https://github.com/rznies/autonomous-communication-manager/issues/24)
**Type**: AFK | **Blocked by**: #21

Refactor `TopBar.jsx` to use shadcn/ui primitives.

**Acceptance criteria**:
- [ ] User avatar uses `Avatar` with `AvatarImage` + `AvatarFallback`
- [ ] Notification button wrapped in `Tooltip`
- [ ] All icons use Lucide React (`Search`, `Bell`, `ChevronDown`)
- [ ] TopBar positioning unchanged
- [ ] No console errors

**User stories**: 9, 14, 15

---

### Slice 5: Final visual QA + responsive verification
**Issue**: [#25](https://github.com/rznies/autonomous-communication-manager/issues/25)
**Type**: HITL | **Blocked by**: #22, #23, #24

Full visual QA pass. Human review required.

**Acceptance criteria**:
- [ ] Dashboard screenshot at 1280px matches or exceeds original quality
- [ ] No light-mode flashes or theme inconsistencies
- [ ] All color tokens render correctly
- [ ] Grid adapts at 768px
- [ ] Lucide icons render everywhere
- [ ] Confirm dialog opens/closes
- [ ] Loading skeleton on page load
- [ ] Zero console errors
- [ ] Material Symbols font not loaded (check Network tab)

**User stories**: 18, 21, 22

## Dependency Graph

```
#21 (Foundation)
 ├── #22 (Dashboard)
 ├── #23 (Sidebar)
 └── #24 (TopBar)
       └── #25 (Visual QA)
```

## Execution Order

1. Start with #21 (no blockers)
2. #22, #23, #24 can run in parallel after #21
3. #25 runs after all three refactor slices are complete
