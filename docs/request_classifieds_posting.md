# Request for Solutions — Anonymous Classifieds Posting for Static Site

## Context

Paradisio has a classifieds board (rooms, jobs, gigs, for sale, services, events, rideshare) at `paradisio_app/classifieds/`. It's a static site on GitHub Pages — no server, no database, no backend.

Currently, users "post" via a mailto: link that opens their email client. The email goes to `paradisio@example.com`. I manually copy the ad into `classifieds.json`, rebuild, and push. This doesn't scale.

## Requirements

1. **Poster anonymity**: Poster's real email should not be exposed on the public listing page
2. **Spam resistance**: Must have some barrier to prevent automated spam posts
3. **Moderation**: I must review posts before they go live (no auto-publish)
4. **Zero infrastructure**: No server, no database — GitHub Pages only
5. **Low cost**: Ideally free, or very low cost
6. **Puerto Viejo context**: Many posters may not have email but have WhatsApp. The flow should match how locals actually communicate

## Constraints

- Static site on GitHub Pages (no server-side code)
- Current stack: Python stdlib build pipeline, vanilla HTML/CSS/JS
- Poster demographic: mostly Spanish-speaking, phone-first, WhatsApp-native
- Volume: low (maybe 1-5 posts per week)

## Research Questions

1. What approaches do other static-site classifieds boards use for posting?
2. What third-party form services work with static sites and support moderation queues?
3. Can WhatsApp serve as the primary contact layer instead of email?
4. Are there lightweight issue-tracker-as-CMS patterns that work for this?
5. What's the simplest possible approach that isn't manual copy-paste?

Please research and recommend the top 3 approaches with tradeoffs.
