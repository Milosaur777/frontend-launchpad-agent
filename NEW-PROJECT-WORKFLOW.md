# New Website Project Workflow

## Rules (MANDATORY)

1. **Always create a new folder** for each project — never modify another project's files
2. **Always push to a new Vercel address** — each project gets its own deployment URL
3. **Ask first** — confirm project name, folder name, and Vercel project name before creating anything
4. **Never delete** — if something needs to change, ask the user. Don't delete files, folders, or projects without explicit permission

## Step 1: Get Project Details

Before writing any code, ask the user:

- **Project name** (e.g., "DadTV", "Portfolio", "Landing Page")
- **Folder name** (e.g., `IPTV/DadTV`, `Projects/Portfolio`)
- **Vercel project name** (auto-generated from folder name, but confirm)
- **Tech stack** (Next.js + Tailwind is default, but ask if they want something different)

## Step 2: Create Project Structure

```
ProjectFolder/
├── package.json
├── next.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
├── .vercelignore          # ignore node_modules, .next
└── src/
    ├── app/
    │   ├── layout.tsx     # root layout with metadata
    │   ├── globals.css    # tailwind imports
    │   ├── page.tsx       # home page
    │   └── [route]/
    │       └── page.tsx
    └── lib/
        └── [utilities]
```

## Step 3: Install Dependencies

```bash
cd ProjectFolder
npm install
```

## Step 4: Build & Verify

```bash
npx next build
```

Fix any errors before deploying.

## Step 5: Deploy to Vercel

```bash
npx vercel --prod --yes
```

This creates a new Vercel project automatically on first deploy.

If deployment fails due to vulnerability checks:
1. Check `npm audit` for the issue
2. Update the affected package version
3. Rebuild and redeploy

## Step 6: Confirm

- Verify the site is live at the Vercel URL
- Tell the user the URL
- Ask if any changes are needed

## Common Issues

### "Vulnerable version of Next.js"
- Run `npm audit` to see what's affected
- Update the package to the latest patch version
- Clean reinstall: delete `node_modules` and `package-lock.json`, then `npm install`

### Build errors
- Check TypeScript types match
- Check imports are correct
- Check for missing dependencies

### Vercel deploy fails silently
- Use `npx vercel ls` to check deployment status
- Use `npx vercel inspect [url]` for details
- Try `--no-wait` flag to see the deployment URL
