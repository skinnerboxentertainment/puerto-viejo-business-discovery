# Paradisio — The Puerto Viejo Operating System

## Thesis

A persistent web application that is the town's commercial and cultural operating system. Every business is listed by default (opt-out, not opt-in). Every local artist, photographer, musician, poet, and creator has a profile alongside them. The whole thing is fed by a live Instagram capture of 452+ handles, a QR code affiliate network, a quarterly print magazine, a middleman service layer, and AI-augmented upsells. It is Craigslist for a single town, but reversed — everyone is already on it, and we sell them premium tools to own their presence.

---

## Core Principles

1. **Opt-out, not opt-in.** The 750 businesses are already listed with their data. The burden is on them to leave, not to join.
2. **Persistent web app.** One URL. Works on any device. No app store. The town's surface.
3. **Craigslist aesthetic, not SaaS.** Text-first, fast, ugly in a way that signals authenticity. Works on a $30 smartphone in 2G.
4. **Local contact layer, not a booking engine.** The transaction happens on WhatsApp. We route intent into conversation.
5. **Physical + digital hybrid.** QR codes on doors, a quarterly magazine in lobbies, and a live web app behind it all.
6. **The dataset is the moat.** 750 businesses, 452 IG handles, 611 phones, 699 CIDs, 361 Facebook URLs, 191 websites, 106 WhatsApps, 75 emails — all in one normalized graph. Nobody else has this.

---

## Data Sources

| Source | Records | Key fields |
|--------|---------|------------|
| PV Satellite crawl | 450 | Names, categories, areas, coordinates, CIDs, phone, IG, FB, Booking, TripAdvisor |
| OSM cross-reference | +31 | Coordinates, phone, website, OSM tags |
| Maps grid scan (Playwright + vision) | +134 | Business names discovered via screenshots |
| PVS SQLite cache | +139 | Additional contact data |
| Website crawl | 81 sites | IG, FB, email, WhatsApp from 191 websites |
| Instagram verification (Playwright) | 452 verified | Working IG handles with confidence scores |
| Stealth Maps search | 265 resolved | CIDs, coords, phone, website |
| **Unified master** | **750** | **34 columns per record** |

---

## Products & Revenue

### Tier 1 — Premium Listing ($100/yr year 1, $200/yr year 2)

What the business gets:
- A permanent page on the platform with their data, photos, contact channels, and map pin
- A physical QR code sticker for their door/window (SINPE trackable)
- Featured placement in their category and neighborhood
- Monthly scan/view analytics
- Auto-generated business page (AI takes their existing data and produces a one-page site)

The $100 is not revenue — it is a commitment mechanism. Year 1 hooks them. Year 2 is a renewal they'll pay because by then the platform is generating inbound.

### Tier 2 — AI Service Add-ons ($10-30/mo each)

| Service | Description | Price |
|---------|-------------|-------|
| WhatsApp auto-reply | AI answers common questions (hours, menu, prices, location) in Spanish/English | $20/mo |
| IG content pack | 4 AI-generated posts/month from their business data | $30/mo |
| Menu/price translation | Spanish/English/French translation of menu or service list | $50 one-time |
| Review response drafts | Auto-generate replies to TripAdvisor/Google reviews | $15/mo |
| Booking link integration | Connect Booking.com/Airbnb calendar to their page | $10/mo |
| Photo refresh | AI-enhanced or commissioned photography of their space | $75 one-time |

### Tier 3 — Middleman Service Fee (10-20% per transaction)

The platform intermediates specific service bookings:

| Category | Service | Our cut |
|----------|---------|---------|
| Transport | Airport shuttle, van driver SJ↔PV, taxi, boat transfer | 10-15% |
| Tours | Snorkeling, sloth sanctuary, chocolate, night walk, ATV | 10-20% |
| Dining | Reservation with pre-order, chef's table coordination | 5-10% |
| Activities | Surf lessons, yoga, bike rental, photography session | 10-15% |
| Services | Massage, laundry, bike repair, Spanish tutor, medical | 15-20% |

The platform confirms both sides, sends reminders, handles bilingual coordination, and manages fallback. The transaction happens on WhatsApp + SINPE. We take our cut.

---

## The Affiliate QR Code Network

### How it works

Local salespeople (students, surf instructors, bartenders, ticos) walk the town. They already know the business owners. They say:

> *"Your restaurant is already on the Puerto Viejo board. 50 people saw your page this month. Put this QR code on your door and every tourist Instagramming their food can message you directly. First year, we do sticker + setup — 10 mil colones (SINPE)."*

### QR code tiers

| Variant | What it does | Price |
|---------|-------------|-------|
| Basic | Opens listing page (WhatsApp, IG, phone, map) | $100/yr |
| Menu | Opens menu + WhatsApp | $150/yr |
| Booking | Opens Booking/Airbnb page + WhatsApp | $200/yr |
| Review | Opens TripAdvisor/Google review prompt | $50/yr add-on |

Every scan is trackable. After 6 months: *"Your QR code got scanned 300 times. 45 people opened WhatsApp. You paid 10mil. That's 22mil per new conversation."*

### Affiliate commission

Commission on each QR code sale. Paid instantly via SINPE. The affiliate network is the sales force. No salaries, no benefits, no overhead.

---

## The Instagram Capture Engine

### Live aggregation

452 verified Instagram handles. Every post, every story, every hashtag. Captured continuously.

### What it feeds

| Output | What it does |
|--------|-------------|
| Event detection | 3 hotels IG'd the same thing = there's a festival, wedding, retreat |
| Dinner rush signal | Restaurants posting specials in real time |
| Beach/conditions | Surf schools posting wave pics = surf report |
| Dead zone detection | Areas with no posts this week = invisible businesses |
| Hashtag analytics | #PuertoViejo, #Cocles, #Cahuita, #PuntaUva, #CaribbeanCostaRica trending |
| Magazine content | Aggregated IG data becomes editorial |

### Business-facing dashboard

- Your post reach this month
- Your hashtag performance vs. competitors
- Best times to post by category
- "You're the most Instagrammed coffee shop in Cocles"

---

## The Quarterly Magazine

A beautiful, high-gloss, bilingual printed magazine. Distributed to every hotel lobby, hostel common room, rental villa, tour desk, and bar in town.

### Content sourced from the data stream

- "The 20 Most Instagrammed Tables in Puerto Viejo This Season"
- "What Cocles Ate in July" — aggregated from restaurant Instagrams
- "Wave Report" — surf spots ranked by IG story frequency
- "The Quiet Places" — businesses with amazing service but zero social presence
- "New in Town" — detected from new Instagram accounts appearing in the area
- Full-page premium member ads
- QR code on every page → deep link to the business on the platform

### Why businesses host it

It makes their lobby feel curated. They don't realize they're also distributing a sales catalog that trains every tourist to use the platform. The FOMO is built in: businesses that didn't pay see their name next to ones that did.

---

## The Creative Layer

### Profiles alongside businesses

The platform isn't just hotels and restaurants. It includes:

- Local photographers
- Musicians and bands
- Poets and writers
- Muralists and visual artists
- Surf instructors (as performers, not just services)
- Chefs (as artists, not just restaurant listings)
- Models and content creators
- International artists who want to collaborate

### Why it matters

The creative layer is the content engine that makes the business board *interesting.* A tourist doesn't just look for a hotel — they look for what's happening tonight. The artists posting their gigs, the photographer offering a sunset shoot, the poet doing a reading at the hostel bar — this is what makes a town feel alive.

### Cross-listing

> *"You're a bar. Your musician plays here every Thursday. We cross-list them. Their fans find you, your guests find them."*

---

## The Community Layer

| Surface | Purpose |
|---------|---------|
| Reddit (r/PuertoViejo) | Visitor questions, trip reports, "is this place still good?" |
| Discord | Real-time chat: live music tonight, surf conditions, rideshares, event chatter |
| Blog | Long-form profiles, deep interviews, photo essays, history pieces |
| Magazine | Quarterly print version of the best content |

All populated from the same data stream. Instagram capture feeds the blog. Event detection feeds the Discord. Business listings feed the subreddit wiki. Magazine content gets republished as blog posts.

---

## The Flywheel

```
Instagram posts → aggregated analytics & event detection
  → magazine editorial + real-time web app updates
    → physical distribution + QR code scans
      → tourist uses platform
        → business gets booked
          → business upgrades to premium
            → more Instagram posts
```

Every quarter, the magazine is the physical artifact proving the network is alive.

---

## Pricing Summary

| Product | Year 1 | Year 2 |
|---------|--------|--------|
| Premium listing + QR sticker | $100 | $200 |
| AI add-ons (per month) | $10-30 | $10-30 |
| Middleman transaction | 10-20% | 10-20% |
| Magazine full-page spread | $150 | $250 |
| Affiliate commission | 20-40% of sale | 20-40% of sale |

---

## The One-Page Pitch

> **Paradisio is the default operating system for Puerto Viejo commerce and culture.**
>
> Every business and artist in town is already listed. QR codes on every door route tourists into WhatsApp conversations. A live Instagram engine detects events, trends, and dead zones. A quarterly magazine proves the network is real. AI augments every business's digital presence for a fraction of what a website costs.
>
> Year 1 is $100 to own your page. Year 2 is $200. The sticker on your door never stops working. The platform never stops feeding you inbound. Opt out if you want — but why would you?

---

*Built on the Puerto Viejo Business Discovery dataset — 750 businesses, 452 IG handles, 611 phones, 699 CIDs. Zero API costs. Full audit trail.*
