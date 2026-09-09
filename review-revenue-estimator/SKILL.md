---
name: review-revenue-estimator
description: Estimate absolute monthly and annual revenue for local businesses with a public Google, Yelp, or Meta presence using review velocity, ticket size, and industry priors. Trigger when the user asks to estimate revenue, sales, or run-rate from reviews, Yelp, Google Business, Facebook, or Meta, or supplies a business name plus location for a private-company revenue estimate. Do not use for public-company earnings, ETFs, pure e-commerce with no local footprint, marketplaces, or franchisor system-wide sales.
---

# Review Revenue Estimator

Estimate monthly and annual revenue *ranges* for businesses that appear on Google Business Profile, Yelp, and/or Meta using public review flow as a proxy for transaction volume.

**Final numbers MUST come from** `scripts/estimate_revenue.py`. Do not hand-calculate the published range.

## Model (read this before collecting data)

```
monthly_transactions = primary_review_velocity / review_rate
monthly_revenue      = monthly_transactions × average_ticket × location_ticket_mult
```

- **Review rate** = share of *transactions / visits / stays* that produce a review on the primary platform (usually Google). It is not “percent of people who have ever left a review.”
- **Average ticket** = dollars per transaction (or per stay for hotels, per member-month for gyms). Prefer a local menu, rate card, or invoice override over the national prior.
- **Primary platform** = Google when present. Yelp and Meta corroborate confidence; they are not added into volume. Do not blend velocities.
- **Rating is not a default revenue scalar.** Luca (2011) finds +5–9% revenue per Yelp star for *independent restaurants* via a rounding discontinuity. That is a counterfactual, and velocity already embeds realized demand. Pass `--apply-rating-effect` only when the user asks “what if this shop were X stars.” Chains get no rating effect.
- Always publish low / base / high plus Low / Medium / High confidence.

Womply (2019, ~200k US SMBs) found review *count* correlates with revenue more than star rating, and that 3.5–4.5★ shops out-earn both 5.0★ and very low-rated shops on average. Treat that as a confidence prior, not a second multiplier.

## Do not use this skill when

- The target is a public company, ETF, or “earnings this quarter”
- There is no consumer review footprint (pure B2B, wholesale, marketplace)
- The user wants franchisor or banner-level system sales from one pin
- The listing is closed, duplicate, or clearly the wrong entity

## Required inputs

Minimum from the user: business name + location (city/state or address).

Collect if possible: industry/sub-vertical, local ticket, years open / first-review year, number of locations, chain vs independent, seats/rooms/chairs/bays, evidence of review solicitation.

## Process

### 1. Collect review data

Follow `references/collection.md`. For each of Google, Yelp, Meta record total reviews, average rating, and monthly velocity (last 30–90 days from dated reviews). Missing platforms are a signal. Hotels — also check TripAdvisor and put the count in `--notes` (script volume still uses Google unless Google is empty).

### 2. Classify

Map to an exact script key (aliases exist for a few synonyms; do not invent keys):

`qsr`, `cafe`, `full_service_restaurant`, `fine_dining`, `bar`, `restaurants` (legacy umbrella), `salon`, `spa`, `gym`, `personal_care` (umbrella), `home_services`, `hvac`, `house_cleaning`, `medical`, `dental`, `vet`, `professional`, `retail`, `auto_services`, `hotels`, `default`

Location tier: `major_metro`, `secondary_city`, `suburban`, `rural`.

Prefer a specific key (`qsr`, `dental`) over an umbrella.

### 3. Run the script

```bash
python3 scripts/estimate_revenue.py \
  --name "Exact Business Name" \
  --location "City, State" \
  --industry "auto_services" \
  --location-tier "rural" \
  --google-reviews 151 --google-rating 4.8 --google-velocity 6.0 \
  --yelp-reviews 5 --yelp-rating 0 --yelp-velocity 0 \
  --meta-reviews 0 \
  --years-open 8 \
  --bays 3 \
  --notes "Independent shop; first Google review ~2018"
```

Useful flags:

- Ticket override (preferred when you found a local menu or typical job price): `--ticket-low 400 --ticket-base 550 --ticket-high 750 --ticket-source "local invoices / menu"`
- Legacy aliases `--aro-low/base/high` still work
- Rate override: `--rate-low 0.04 --rate-base 0.06 --rate-high 0.09`
- Scale / type: `--locations 3 --chain --solicited --years-open 12`
- Capacity (clamps an impossible high case): `--seats 48` `--rooms 32` `--chairs 6` `--bays 4` `--crews 2 --days-open-month 26`
- Counterfactual only: `--apply-rating-effect`
- `--currency USD` (no FX; pass tickets already in local units)
- `--format json` if you need to wrap the numbers

`--json` on stdin still accepted. Copy the script’s printed report into the answer. You may add source notes around it; do not rewrite the quantitative block.

### 4. Sanity checks before sending

- Implied transactions/day vs seats × turns, rooms × occupancy, bays × jobs, or chairs × clients. If you have capacity, pass it so the script can clamp.
- Compare the base annual figure to any public analog (franchise AUV, county health-permit peer, hotel RevPAR × rooms). If they disagree by >3×, say so and drop confidence rather than silently averaging.
- Off-premise / delivery, catering, wholesale, and insurance/contract work are usually under-reviewed — mention as upside not in the range.
- Sudden velocity spikes + templated owner replies → pass `--solicited` and treat recent velocity as an upper bound.

### 5. Confidence

Do not override the script label unless you have ground-truth sales the script cannot see. If you override, state the source (tax return, franchise AUV, disclosed S-1, etc.).

## References

- `references/benchmarks.md` — review-rate and ticket priors, sources, what not to use
- `references/collection.md` — how to scrape velocity and when platforms disagree
