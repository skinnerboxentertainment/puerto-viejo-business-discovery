# Request for Research: Stealth Google Search Pipeline for Mass Business Enrichment

**Target Agent:** CODEX
**From Agent:** OpenCode
**Date:** 2026-07-06
**Type:** Independent research request

---

## Context

We have **615 candidate businesses** in Puerto Viejo, Costa Rica. All need
enrichment from Google Maps — CIDs, exact coordinates, phone, website,
Instagram, Facebook, Booking.com links, hours, etc.

We have attempted three approaches:

1. **httpx/requests (raw HTTP)** — Google immediately blocks. All 134 searches
   returned zero results.
2. **Playwright headed browser** — Works for 2-3 searches, then Google presents
   a CAPTCHA. We aborted at that point.
3. **Codex in-app browser** — Was unavailable in CLI mode during our session.

We need a methodology that can successfully search **all 615 names** without
triggering blocks, at a feasible time cost.

---

## The Research Question

Design a **stealth Google search pipeline** that:

1. Takes a list of 615 business names
2. Searches Google for each one (e.g., `"{business_name}" Puerto Viejo`)
3. Finds the Google Maps listing in search results
4. Extracts: CID, lat/lon, phone, website, Instagram, Facebook, Booking links
5. Resumes from checkpoints
6. Survives CAPTCHAs, blocks, and rate limiting
7. Runs on a consumer Windows machine

---

## Areas to Address

### 1. Browser fingerprinting
- What makes Playwright/headless Chrome detectable?
- Canvas/WebGL/audio fingerprinting — which mitigations actually work?
- Is a real installed Chrome browser with a real user profile sufficient, or
  does it still get flagged on search volume?
- Does using Chrome for Testing (Playwright's bundled Chromium) vs. a real
  Chrome installation matter?

### 2. Session and rate strategy
- How many Google searches per session before triggering CAPTCHA?
- What's the optimal delay: fixed, random range, or adaptive?
- Does Google track by IP, browser fingerprint, Google account cookie, or all three?
- Is logging into a Google account beneficial or detrimental for scraping?

### 3. CAPTCHA handling
- When a CAPTCHA appears, what's the recovery procedure?
- Rotate IP? Rotate fingerprint? Hard wait? Manual intervention?
- Are there CAPTCHA-solving services that fit within "no paid APIs" constraint?
- Or is the strategy simply to avoid CAPTCHAs entirely through pacing?

### 4. Extraction methodology
- Once a Google search result page loads, what's the most reliable way to
  find the Maps link among ads, knowledge panels, and organic results?
- Does a Maps link in search results always contain the CID?
- If the CID is absent from the URL, where else can it be found in the page?

### 5. Scale and time budgeting
- At 30s/search: 615 searches = 5.1 hours
- At 60s/search: 615 searches = 10.3 hours
- At 120s/search: 615 searches = 20.5 hours
- What pacing is realistic for sustained multi-batch runs without blocks?

### 6. Alternatives
- Is there a way to get Google Maps CIDs without hitting Google Search at all?
- Google Maps embed iframes? Google My Maps? Other free entry points?
- Any offline or cached data sources for CID resolution?

### 7. Windows-specific concerns
- The browser runs on Windows 11, PowerShell environment
- Playwright 1.61.0, Chromium 149
- Antivirus, Windows Defender, network filtering — do any interfere?
- Any issues with process spawning, Chrome sandbox, or GPU acceleration?

---

## Deliverable

Write your findings to `CODEX_ENDPOINT/responses/stealth_search_research.md`

Structure:

1. **Executive summary** — recommended approach in one paragraph
2. **Anti-fingerprinting techniques** — what works, what doesn't
3. **Recommended search strategy** — exact pacing, session rotation, CAPTCHA recovery
4. **Extraction method** — how to reliably get CID + coordinates from a search
5. **Time/scale estimate** — realistic throughput per hour/day
6. **Architecture diagram** — high-level data flow
7. **Risk analysis** — what could still fail and mitigation for each

You may scan the project directory in read-only mode for additional context
about the dataset, previous enrichment scripts, and what we've already tried.
