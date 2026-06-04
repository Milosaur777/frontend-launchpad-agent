# Netlify Insights — CLI Usage & Client Tracking Reference

> **Purpose:** Quick reference for using Netlify CLI and deploying Netlify Insights (analytics) for client projects.

## Installation

```bash
npm install -g netlify-cli
# Verify
netlify --version
```

## Common CLI Commands

### Authentication & Deploy

```bash
netlify login                          # Authenticate browser
netlify init                           # Link project to Netlify site
netlify deploy                         # Deploy draft URL
netlify deploy --prod                  # Deploy to production
netlify deploy --prod --dir=out        # Deploy custom directory (e.g. static export)
netlify open                           # Open site in browser
```

### Environment & Config

```bash
netlify env:list                       # List env variables
netlify env:set KEY value              # Set env variable
netlify env:unset KEY                  # Remove env variable
netlify sites:list                     # List all sites
netlify sites:create --name site-name  # Create new site
```

### Functions & Logs

```bash
netlify functions:list                 # List serverless functions
netlify functions:invoke function-name # Invoke function locally
netlify logs:deploy                    # View deploy logs
netlify deploy --trigger               # Trigger deploy without building
```

## Netlify Insights (Analytics)

Netlify Insights provides privacy-friendly, lightweight page analytics via a script snippet injected at deploy time.

### Enabling Insights

1. **Via Netlify UI:** Site Settings → Analytics → Enable Netlify Insights
2. **Via CLI:** No direct CLI toggle — enable in dashboard
3. **Manual snippet** (if you self-host the script):

```html
<script src="https://cdn.netlify.com/insights/latest.js" async></script>
```

### What Insights Tracks

- Page views (no personal data)
- Visitor geography (country-level)
- Top pages, referrers, devices
- Core Web Vitals (LCP, CLS, INP)

### Using Insights for Client Projects

When a client wants analytics but doesn't want Google Analytics:

1. Enable Insights in the Netlify dashboard
2. No cookie banner required (privacy-compliant by design)
3. The `<netlify-visitor-counter>` custom element shows a public visitor badge

```html
<netlify-visitor-counter class="text-muted text-sm" />
```

### Insights vs Google Analytics

| Feature | Netlify Insights | Google Analytics |
|---|---|---|
| Privacy | Cookieless, GDPR-compliant | Requires cookie consent |
| Page views | ✅ | ✅ |
| Core Web Vitals | ✅ | ❌ |
| Sessions / Users | ❌ | ✅ |
| Events / Conversions | ❌ | ✅ |
| Cost | Free on Netlify | Free tier available |

Use Netlify Insights for lightweight traffic monitoring; pair with a proper analytics tool (Plausible, PostHog) when clients need event tracking.

## Deploy Hooks & Automations

```bash
# Trigger deploy from CI
curl -X POST https://api.netlify.com/build/hooks/HOOK_ID

# Run local build + deploy
npm run build && netlify deploy --prod --dir=.next
```

## Quick Reference — Common Config Files

| File | Purpose |
|---|---|
| `netlify.toml` | Build settings, redirects, headers, functions |
| `_redirects` | Static redirect rules (put in publish dir) |
| `_headers` | Custom HTTP headers (put in publish dir) |

### Minimal `netlify.toml`

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

## When to Use This

- Client asks for "analytics on my Netlify site"
- Client wants to know how many visitors without a cookie banner
- You need to debug a deploy or environment variable
- You're migrating a static site to Netlify

---

*Part of the Frontend Launchpad Agent — reference for Netlify CLI workflows.*
