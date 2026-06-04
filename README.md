
<h1 align="center">🚀 Frontend Launchpad Agent</h1>

<p align="center">
  <em>One-click install. Zero AI slop. Production-ready frontend, on demand.</em>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/skills-21-blue?style=flat&logo=react" alt="Skills"></a>
  <a href="#"><img src="https://img.shields.io/badge/agents-2-green?style=flat&logo=openai" alt="Agents"></a>
  <a href="#"><img src="https://img.shields.io/badge/MCP%20servers-8-orange?style=flat" alt="MCP Servers"></a>
  <a href="#"><img src="https://img.shields.io/badge/rules-8-purple?style=flat&logo=checkmarx" alt="Rules"></a>
  <a href="#"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="License"></a>
</p>

---

## What Is This?

This is an **AI Frontend Launchpad** — a complete, portable environment for building production-quality frontends using AI.

It bundles **21 specialized skills**, **2 review agents**, **8 MCP servers**, **8 coding rules**, and a full **design system** into one project. Clone it, run one setup command, and your AI assistant becomes a senior frontend designer capable of:

- Building entire pages and dashboards from a single prompt
- Generating design systems with tokens, palettes, and typography scales
- Auditing existing UI for anti-patterns and AI slop
- Creating polished presentations, brand kits, and animations
- Reviewing React code for hooks correctness, a11y, and performance
- Deploying to Webflow, Vercel, or Supabase

This repo aggregates work from many open-source projects — see [Credits](#-credits--thanks) for the full list.

---

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USER/frontend-launchpad-agent.git
cd frontend-launchpad-agent

# 2. Install dependencies
npm install

# 3. Verify the agent is loaded
# If you use OpenCode: opencode will auto-load opencode.json
# If you use Claude Code: copy .agents/ into your ~/.claude/agents/
```

That's it. You now have a complete frontend design agent.

---

## Capabilities

###  Design System Generation

| Skill | What It Does |
|---|---|
| `design-system` | Generate DESIGN.md with tokens, audit UI visual consistency, detect AI slop (purple gradients, glassmorphism, generic hero layouts) |
| `stitch-design-taste` | Generate Google Stitch-compatible DESIGN.md with encoded color calibration, typography architecture, anti-generic bans |
| `frontend-design-direction` | Infer purpose/audience/tone before writing a single line of code |

###  Component Development

| Skill | What It Does |
|---|---|
| `frontend-patterns` | React composition, compound components, custom hooks, state management (Context + Reducer), Framer Motion animations, virtualization, error boundaries |
| `emil-design-eng` | Emil Kowalski's UI polish philosophy — animation decision framework, spring physics, clip-path reveals, gesture handling, CSS transform mastery |
| `image-to-code` | Generate premium design images first, then implement pixel-perfect code from them |
| `gan-style-harness` | GAN-inspired generator-evaluator feedback loop — Planner → Generator → Evaluator with scoring across design quality, originality, craft, and functionality |
| `3d-pie-chart` | Build 3D extruded donut/pie charts with React Three Fiber — per-segment THREE.Shape + ExtrudeGeometry, gold/glass materials, clip-plane reveal animations, mobile optimization |

###  Design Auditing & Anti-Pattern Detection

| Skill | What It Does |
|---|---|
| `redesign-existing-projects` | Scan existing codebases, diagnose generic patterns, apply targeted upgrades without breaking functionality. Covers typography, color, layout, interactivity, content, icons, code quality |
| `design-taste-frontend` | Anti-slop enforcement — bans Inter font, purple gradients, 3-column equal cards, centered heroes, generic placeholder text |
| `design-taste-frontend-v1` | Original v1 taste-skill with HIGH_DESIGN_VARIANCE / MOTION_INTESITY / VISUAL_DENSITY controls |

###  Visual Style Specializations

| Skill | What It Does |
|---|---|
| `high-end-visual-design` | Awwwards-tier output — Double-Bezel nested card architecture, Button-in-Button CTAs, cinematic spring motion, Fluid Island nav |
| `minimalist-ui` | Clean editorial interfaces — warm monochrome palette, bento grids, Phosphor icons, ultra-diffuse shadows |
| `industrial-brutalist-ui` | Swiss typographic print × military terminal — rigid grids, extreme scale contrast, CRT scanlines, halftone dithering |

###  Brand & Presentation

| Skill | What It Does |
|---|---|
| `brandkit` | Premium brand identity image generation — logo concept boards, color systems, typography specimens, application mockups |
| `frontend-slides` | Zero-dependency HTML presentations — keyboard nav, swipe, viewport-fit enforcement, PPTX conversion |
| `gpt-taste` | Awwwards GSAP motion engineering — ScrollTrigger pinning, gapless bento grids, Python-driven randomization for layout variance |

###  Image Generation

| Skill | What It Does |
|---|---|
| `imagegen-frontend-web` | Generate one separate horizontal image per website section — premium composition variety, narrative concept spine, consistent palette |
| `imagegen-frontend-mobile` | Premium mobile app screen concepts — onboarding, auth, dashboards, fintech, ecommerce, inside device mockup frames |

###  Code Quality & Enforcement

| Skill / Agent | What It Does |
|---|---|
| `full-output-enforcement` | Override LLM truncation — complete code generation, bans `// ...`, `// TODO`, skeleton outputs |
| `react-reviewer` | React/JSX code review — hooks rules, server/client boundary, render performance, `dangerouslySetInnerHTML`, form validation |
| `a11y-architect` | WCAG 2.2 compliance architect — semantic HTML, ARIA, focus management, keyboard navigation, color contrast |

###  Rules (Always-Follow Guidelines)

| Rule | Focus |
|---|---|
| `design-quality.md` | Visual consistency, anti-pattern prevention |
| `web-coding-style.md` | TypeScript strict, naming conventions, file organization |
| `web-hooks.md` | React hooks discipline, exhaustive deps |
| `web-patterns.md` | Composition, containers, error boundaries |
| `web-performance.md` | Next.js Image, lazy loading, bundle optimization |
| `web-security.md` | XSS prevention, CSP headers, auth patterns |
| `web-testing.md` | Playwright, Vitest, testing strategy |
| `web-images.md` | AVIF conversion, size budgets, alt text |

###  MCP Servers (Extend the Agent's Reach)

| Server | Purpose |
|---|---|
| **21st.dev** | Search and generate React/Tailwind components from a library of premium UI |
| **shadcn/ui** | Access the shadcn component registry — add Button, Card, Dialog, etc. |
| **Webflow** | Two-way sync: manage CMS, build pages, upload assets, deploy sites |
| **Supabase** | Database schema, migrations, Edge Functions, RLS policies |
| **n8n** | Workflow automation — connect APIs, schedule tasks, process data |
| **Obsidian** | Knowledge management — read/write/search notes in your vault |
| **VPS** | SSH server management — deploy and manage remote infrastructure |
| **ts-lsp** | TypeScript Language Server — hover info, go-to-definition, find references, diagnostics, symbol search |

The **first three** (21stdev, shadcn, ts-lsp) are pre-configured in `.opencode/mcp_servers.json` and work out of the box. The rest (Webflow, Supabase, n8n, Obsidian, VPS) require user-provided API keys or local paths — see [MCP_WALKTHROUGH.md](./MCP_WALKTHROUGH.md) for setup instructions.

---

## Project Structure

```
frontend-launchpad-agent/
├── opencode.json                 # Agent configuration (auto-loaded by OpenCode)
├── AGENTS.md                     # Next.js agent rules
├── DESIGN.md                     # Design system tokens (dark-first portfolio)
├── ROADMAP.md                    # Project plan & architecture
├── MCP_WALKTHROUGH.md            # Complete MCP setup guide
├── Netlify_insights.md           # Netlify CLI & analytics reference
│
├── .opencode/
│   └── mcp_servers.json          # MCP servers (21stdev, shadcn, ts-lsp)
│
├── .agents/
│   ├── skills/                   # 21 specialized skills
│   │   ├── design-system/               # Generate & audit design systems
│   │   ├── frontend-design-direction/   # Purpose/audience inference
│   │   ├── frontend-patterns/           # React component patterns
│   │   ├── frontend-a11y/               # Accessibility patterns
│   │   ├── frontend-slides/             # HTML presentation builder
│   │   ├── gan-style-harness/           # Generator-evaluator loop
│   │   ├── stitch-design-taste/         # Google Stitch design system
│   │   ├── redesign-existing-projects/  # Upgrade existing UI
│   │   ├── high-end-visual-design/      # Awwwards-tier UI
│   │   ├── minimalist-ui/               # Editorial minimalism
│   │   ├── industrial-brutalist-ui/     # Swiss × military UI
│   │   ├── brandkit/                    # Brand identity generation
│   │   ├── emil-design-eng/             # Emil Kowalski's philosophy
│   │   ├── full-output-enforcement/     # Complete code generation
│   │   ├── gpt-taste/                   # GSAP motion engineering
│   │   ├── image-to-code/               # Image-first implementation
│   │   ├── imagegen-frontend-web/       # Web design image gen
│   │   ├── imagegen-frontend-mobile/    # Mobile app image gen
│   │   ├── design-taste-frontend/       # Anti-slop v2
│   │   ├── design-taste-frontend-v1/    # Anti-slop v1 (original)
│   │   └── 3d-pie-chart/                # 3D extruded donut charts
│   │
│   ├── react-reviewer.md         # React/JSX code review agent
│   ├── a11y-architect.md         # WCAG 2.2 compliance agent
│   │
│   └── rules/                    # Always-follow guidelines
│       ├── design-quality.md
│       ├── web-coding-style.md
│       ├── web-hooks.md
│       ├── web-patterns.md
│       ├── web-performance.md
│       ├── web-security.md
│       ├── web-testing.md
│       └── web-images.md
│
├── src/                          # Next.js 16 app (pre-scaffolded)
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   └── components/
│       └── ui/                   # shadcn components (pre-installed)
│           ├── button.tsx
│           ├── card.tsx
│           ├── dialog.tsx
│           ├── dropdown-menu.tsx
│           ├── input.tsx
│           ├── tabs.tsx
│           └── ... (25+ components)
│
├── package.json                  # Next.js 16 + React 19 + shadcn/ui
├── components.json               # shadcn configuration
├── tsconfig.json                 # TypeScript strict mode
├── next.config.ts                # Next.js configuration
├── postcss.config.mjs            # Tailwind CSS v4
└── eslint.config.mjs             # ESLint flat config
```

---

## How It Works

### The Workflow

```
1. You describe what you want
       │
       ▼
2. Design Direction (frontend-design-direction)
   → Infer purpose, audience, tone
       │
       ▼
3. Design System (design-system / stitch-design-taste)
   → Generate DESIGN.md with tokens
       │
       ▼
4. Component Sourcing
   → Check: 21st.dev → shadcn → custom build
       │
       ▼
5. Implementation (frontend-patterns + emil-design-eng)
   → React/Next.js code with Framer Motion
       │
       ▼
6. Quality Assurance
   → Anti-pattern checklist
   → react-reviewer (hooks, perf, security)
   → a11y-architect (WCAG 2.2)
       │
       ▼
7. Polish (redesign-existing-projects)
   → Targeted upgrades
```

### The GAN-Style Loop (Optional)

For high-stakes projects, the `gan-style-harness` skill runs a multi-agent feedback loop:

```
PLANNER ──► GENERATOR ──► EVALUATOR
  ▲                           │
  └───────────────────────────┘
         (5-15 iterations)
```

Each cycle scores: Design Quality, Originality, Craft, Functionality. Loop stops when the weighted score passes 7.0/10.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 16 (App Router) |
| Runtime | React 19 |
| Language | TypeScript (strict) |
| Styling | Tailwind CSS v4 |
| Components | shadcn/ui (Base UI primitives) |
| Animation | Framer Motion |
| Icons | Lucide React |
| Fonts | Geist Sans / Geist Mono |
| Notifications | Sonner |
| Component Library | 21st.dev MCP |
| Registry | shadcn/ui MCP |

---

## Anti-Pattern Checklist

This agent is trained to catch and avoid these automatically:

- ❌ Pure black (`#000000`) backgrounds — use tinted neutrals
- ❌ Inter font — use Geist, Satoshi, Cabinet Grotesk
- ❌ Gray text on colored backgrounds — use white or tinted text
- ❌ Cards nested inside cards — use spacing and borders
- ❌ Bounce/spring easing for UI — use smooth ease-out
- ❌ Emojis as icons — use Lucide React
- ❌ Missing hover/focus states
- ❌ Non-semantic HTML (`<div>` for buttons)
- ❌ Purple/blue "AI gradient" aesthetic
- ❌ 3-column equal card feature rows
- ❌ "Elevate", "Seamless", "Next-Gen" copywriting clichés
- ❌ `Lorem Ipsum` — write real draft copy

---

## Configuration

### opencode.json

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md", "DESIGN.md"],
  "skills": {
    "paths": [".agents/skills"]
  }
}
```

The agent auto-loads:
- `AGENTS.md` — Next.js 16-specific agent rules
- `DESIGN.md` — Design system tokens (read before generating UI)
- `.agents/skills/` — All 20 specialized skills

### Supported AI Harnesses

This repo works with:

- **OpenCode** — Auto-discovers `opencode.json` and `skills.paths`
- **Claude Code** — Copy `.agents/` to `~/.claude/agents/` and `~/.claude/skills/`
- **Cursor** — Use `.cursorrules` or reference rules
- **Codex CLI** — Reference `AGENTS.md` for setup
- **Gemini CLI** — Compatible with skill directory structure

---

##  Credits & Thanks

This agent is built on the shoulders of many open-source projects:

### Skills & Patterns
- **[leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill)** — 15 skills: brandkit, design-taste (v1+v2), full-output-enforcement, gpt-taste, high-end-visual-design, image-to-code, imagegen-frontend-web+mobile, industrial-brutalist-ui, minimalist-ui, redesign-existing-projects, stitch-design-taste
- **[emilkowalski/skill](https://github.com/emilkowalski/skill)** — Design engineering skill encoding Emil Kowalski's UI polish philosophy (Sonner creator, Vaul creator)

### ECC Ecosystem
- **[ECC](https://github.com/affaan-m/ECC)** — The harness-native operator system. Source of: `design-system`, `frontend-a11y`, `frontend-patterns`, `frontend-slides`, `gan-style-harness`, `frontend-design-direction`, `react-reviewer`, `a11y-architect`, and all `.agents/rules/` files

### Design Philosophy
- **[Emil Kowalski / animations.dev](https://animations.dev/)** — Animation decision framework, spring physics, CSS transform patterns
- **[Anthropic's Harness Design](https://www.anthropic.com/engineering/harness-design-long-running-apps)** — GAN-style generator-evaluator architecture (March 2026)
- **[Google Stitch](https://labs.google.com/stitch)** — Semantic design system via `stitch-design-taste` skill

### MCP Servers
- **[21st.dev](https://21st.dev)** — React/Tailwind component search and generation
- **[shadcn/ui](https://ui.shadcn.com)** — Component registry and CLI
- **[Webflow](https://webflow.com)** — No-code site builder APIs
- **[Supabase](https://supabase.com)** — Open-source backend with AI integration
- **[n8n](https://n8n.io)** — Workflow automation
- **[Obsidian](https://obsidian.md)** — Knowledge management

### Tech Stack
- **[Next.js](https://nextjs.org)** — React framework
- **[Tailwind CSS](https://tailwindcss.com)** — Utility-first CSS
- **[Framer Motion](https://motion.dev)** — Animation library
- **[Lucide](https://lucide.dev)** — Icon library
- **[Sonner](https://sonner.emilkowal.ski)** — Toast notifications

---

## License

MIT — Use freely, build beautifully.

---

<p align="center">
  <sub>Built with ❤️ by combining the best frontend design tools into one agent.</sub>
</p>
