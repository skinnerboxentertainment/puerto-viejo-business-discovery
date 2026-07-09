# Paradisio — Workspace Setup Guide

## Step 1: Discord

### Create the server
1. Open Discord → `+` (Add a Server) → `Create My Own` → `For a community or club`
2. Name: `Paradisio`
3. Click `Create`

### Create channels

**Text channels:**
```
#welcome             — pinned: turnover doc, app URL, roles
#general             — daily chatter, quick questions
#bugs                — report issues with the app/data
#ideas               — feature suggestions, brainstorming
#decisions           — logged decisions with rationale
#data-questions      — specific dataset/CID/enrichment questions
#classifieds-queue   — new classifieds submissions for review
#dev-log             — build updates, deployments, status changes
#resources           — links to Notion, GitHub, analytics, tools
```

**Voice channels (optional):**
```
General
```

### Roles
- `Admin` — full server control
- `Contributor` — can post in all channels
- `Viewer` — read-only, can suggest in #ideas

### Integration: Notion webhook
1. In Notion page, click `Share` → `Copy webhook URL`
2. In Discord channel settings → `Integrations` → `Webhooks` → paste Notion webhook URL
   → This posts Notion updates into `#dev-log`

### Integration: GitHub
1. Go to `github.com/skinnerboxentertainment/mekatelyu/settings/hooks`
2. Add a webhook pointing to your Discord channel via Discord's GitHub integration
   → This posts commits, issues, and PRs into `#dev-log`

---

## Step 2: Notion

### Create the workspace
1. Go to `notion.so` → sign up with your email
2. Create a new workspace called `Paradisio`

### Create the page structure

```
Paradisio Workspace
├── 📋 Project Board
│   ├── 🟢 Backlog
│   ├── 🟡 In Progress
│   │   ├── Classifieds posting flow
│   │   └── v2 CID re-scan
│   ├── 🔵 Review
│   └── 🟢 Done
│
├── 📚 Knowledge Base
│   ├── 📄 Unified Turnover Doc (link to turnover_unified.md on GitHub)
│   ├── 📄 Design Direction (link to direction doc)
│   ├── 📄 Enrichment Strategy (link to CID report)
│   ├── 📄 FAQ — common questions about the dataset
│   └── 📄 Glossary — terms used in the project
│
├── 🐞 Bug Tracker
│   ├── — trust badges always show verified
│   ├── — Instagram fields can disagree
│   └── — placeholder email in claim flow
│
├── 💡 Ideas
│   ├── — Premium listings ($100/$200)
│   ├── — QR affiliate network
│   ├── — AI service upsells
│   └── — Town API
│
└── 📅 Meeting Notes
    └── 2026-07-09 — Kickoff / direction setting
```

### Share with collaborators
- Click `Share` on each page → `Invite` → enter email addresses
- Role: `Editor` for contributors, `Viewer` for read-only

### Template for classifieds submissions (from Discord #classifieds-queue)
Create a database with fields:
- `Business Name` (text)
- `Category` (select)
- `WhatsApp` (phone)
- `Title` (text)
- `Description` (text)
- `Status` (select: pending / approved / rejected)
- `Submitted by` (text)
- `Date` (date)

---

## Step 3: Link Discord + Notion

### Notion → Discord (page updates post to #dev-log)
1. In Notion page, click `...` → `Add connections` → `Discord`
2. Select the `#dev-log` channel
3. Now when anyone updates a Notion page, it posts to Discord

### Discord → Notion (save messages as tasks)
1. Right-click any message in Discord
2. `Apps` → `Save to Notion`
3. Requires the Notion bot installed in your Discord server

### GitHub → Discord (webhook for commits/issues)
1. In your Discord server: `Server Settings` → `Integrations` → `Webhooks`
2. Copy the webhook URL
3. Go to `github.com/skinnerboxentertainment/mekatelyu/settings/hooks` → `Add webhook`
4. Paste URL, select `Let me select individual events` → check `Pushes`, `Issues`, `Pull requests`

---

## Step 4: Invite Your Cohorts

### Discord invite
```text
https://discord.gg/YOUR_INVITE_LINK
```
Generate from: Discord → Server Settings → Invite → set expiration to Never

### What to tell them
> You've been invited to the Paradisio project workspace.
> - **Discord** is for daily chat, bug reports, and quick decisions
> - **Notion** is for the knowledge base, project board, and structured docs
> - **GitHub** is the code, data, and live app — everything is public
>
> Start here:
> - Read #welcome for pinned context
> - Browse the Notion Knowledge Base
> - Check the Project Board for what's active
> - Post in #ideas if something's missing

---

## Quick Reference

| Tool | URL | Purpose |
|------|-----|---------|
| Live App | https://skinnerboxentertainment.github.io/mekatelyu/paradisio_app/ | The product |
| GitHub | https://github.com/skinnerboxentertainment/mekatelyu | Code + data |
| Discord | https://discord.gg/YOUR_INVITE_LINK | Daily chat |
| Notion | https://notion.so/YOUR_WORKSPACE | Knowledge base + project board |
| Analytics | https://paradisio.goatcounter.com | Traffic stats |
