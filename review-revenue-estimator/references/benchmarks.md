# Benchmark priors

Starting points only. Override ticket from a local menu, rate card, or typical job price whenever you can. Review rates below are **per transaction / visit / stay**, not survey “have you ever reviewed.”

## Unit definition

`review_rate` = reviews_on_primary_platform / transactions_in_same_window.

BrightLocal and similar surveys measure “did you write a review this year” (often 60–80% say they have, and 65–83% say they comply when asked). That is not a per-visit rate. Unprompted per-visit rates are typically mid-single-digits; prompted programs can push well into the teens. Hotels run higher because booking sites ask every stay.

These priors are calibrated to **Google as the sole volume series**. A 4–12% “reviewed on any platform” figure, applied to Google monthly velocity, implies a 48-seat restaurant would need ~150–200 Google reviews per month to be full. Observed independent restaurants more often do 8–25 Google reviews/month at 1–2 turns. Do not paste all-platform or “ever reviewed” survey percentages into `--rate-*`.

## Review-rate priors (primary platform)

| Key | Vertical | Rate low–high (base) | Why |
|---|---|---|---|
| qsr | Quick-service | 0.4–1.2% (0.7%) | Google-only; high visit frequency |
| cafe | Cafe / coffee / bakery | 0.4–1.2% (0.7%) | Habit visits rarely reviewed |
| full_service_restaurant | Full-service restaurant | 0.5–1.8% (0.9%) | Calibrated to covers vs Google velocity |
| fine_dining | Fine dining | 1.0–3.0% (1.8%) | Occasion dining, higher write rate |
| bar | Bar / nightlife | 0.4–1.5% (0.8%) | Repeat locals under-review |
| restaurants | Umbrella F&B | 0.5–2.0% (1.0%) | Use only if subtype unknown |
| salon | Salon / barber | 2–8% (4%) | Often asked at checkout |
| spa | Spa / medspa | 2–8% (4.5%) | High ticket, often solicited |
| gym | Gym (per member-month) | 0.4–1.5% (0.8%) | Ticket = monthly dues; rate is members who review in a month |
| personal_care | Umbrella personal care | 2–8% (4%) | |
| home_services | General contractors | 3–9% (5.5%) | Low job count, medium ask rate |
| hvac | HVAC / plumbing / electrical | 4–11% (7%) | Post-job texts common |
| house_cleaning | House cleaning | 3–10% (6%) | Recurring jobs under-review |
| medical | Clinic / medical | 1.5–6% (3.5%) | Privacy suppresses reviews |
| dental | Dental | 2–7% (4%) | |
| vet | Veterinary | 2–8% (4.5%) | |
| professional | Legal / accounting / similar | 1.5–6% (3.5%) | Relationship, low review culture |
| retail | Brick-and-mortar retail | 0.3–1.2% (0.6%) | Most baskets never reviewed |
| auto_services | Auto repair | 4–10% (6.5%) | |
| hotels | Hotels / lodging | 3–10% (6%) | Google-only; OTAs capture much of the rest |
| default | Unknown | 3–8% (5.5%) | |

Push toward the high end of the range (or pass `--solicited`) when QR cards, SMS follow-ups, or staff scripts are visible. Push down when the shop never replies and has no ask.

Geography: the script multiplies rate by 1.15 in `major_metro` and 0.85 in `rural` because review culture is denser in cities.

## Ticket priors (USD, mid-2020s, national)

Search locally first. These are fallbacks.

| Key | Ticket low–base–high | Notes |
|---|---|---|
| qsr | 8 / 13 / 20 | Check only, not combo-for-a-family |
| cafe | 7 / 12 / 18 | |
| full_service_restaurant | 22 / 38 / 60 | Per person |
| fine_dining | 70 / 120 / 200 | Per person |
| bar | 12 / 22 / 40 | |
| restaurants | 25 / 45 / 70 | Umbrella |
| salon | 40 / 75 / 130 | |
| spa | 80 / 140 / 250 | |
| gym | 30 / 55 / 90 | Monthly dues |
| personal_care | 50 / 80 / 120 | |
| home_services | 180 / 320 / 550 | Blend of small jobs |
| hvac | 220 / 400 / 700 | Service call / typical ticket |
| house_cleaning | 130 / 220 / 350 | Per visit |
| medical | 140 / 240 / 400 | Patient visit, not surgery |
| dental | 180 / 280 / 450 | Mix of hygiene + treatment |
| vet | 120 / 220 / 380 | Wellness + typical sick visit |
| professional | 200 / 450 / 900 | Matter / engagement slice |
| retail | 25 / 60 / 140 | Highly category-dependent |
| auto_services | 280 / 480 / 750 | |
| hotels | 110 / 170 / 280 | ≈ ADR × typical stay (US ADR ~$160 in 2025 per CoStar; stay often 1.3–1.8 nights) |
| default | 80 / 150 / 300 | |

Location ticket multipliers in the script: major_metro 1.25, secondary_city 1.10, suburban 1.00, rural 0.85.

Hotel alternative when rooms are known: rooms × 30 × occupancy × ADR. Pass `--rooms` and a ticket close to ADR × stay length. US 2025 CoStar snapshot: occupancy 62.3%, ADR $160.54, RevPAR $100.02.

Restaurant alternative when seats are known: seats × turns/day × days_open × ticket. Pass `--seats`. Default turns in the script: QSR 4, cafe 6, full-service 2.2, fine dining 1.2, bar 3.

## What the research does and does not justify

**Use**

- Luca, M. (2011), *Reviews, Reputation, and Revenue: The Case of Yelp.com* (HBS). Independent Seattle restaurants: +5–9% revenue per displayed Yelp star, identified off rounding thresholds. Chains ≈ 0. Consumers respond more when review count and Elite reviews are higher.
- Luca / Nagaraj / Subramani work on Texas alcohol-permit venues: getting listed on Yelp at all is associated with ~5–10% revenue.
- Womply (2019): ~200–210k US SMBs, reviews matched to card transactions. Review *count* tracks revenue better than stars. Shops with above-average review counts earned ~54% more than average; 200+ reviews ~2×. Star sweet spot 3.5–4.5; 5.0★ shops were not the highest-revenue group (often smaller, possibly solicited). Claimed listings and review replies also correlate with revenue — treat as professionalism / scale signals, not extra multipliers.
- BrightLocal Local Consumer Review Survey (2024–2026): recency dominates (74% look at last 90 days in 2026). Supports using velocity, not lifetime stock.
- CoStar / STR hotel KPIs for lodging capacity checks.
- National Restaurant Association operations abstracts for check-size bands and sales-per-seat order of magnitude.

**Do not use as inputs**

- Marketing posts that assign a dollar value to “each new Google review” or claim “50 reviews → +$180k/year.” Those are ranking-lift sales pitches, not a volume identity.
- Survey “26% of restaurant customers leave reviews” / “42% of local-business customers leave reviews” figures as per-visit rates. Those are usually “have you reviewed this category.”
- Applying Luca’s 5–9% on top of a velocity-implied revenue number. That double-counts demand.

## Rating

Default: do not multiply. Use rating to flag mix (sub-3.5 may be distressed; persistent 5.0 with thin volume may be gated or fake).

`--apply-rating-effect` implements `1 + (avg − 4.1) × 0.06`, clamped 0.85–1.20, and is skipped for `--chain`.

## Confidence heuristics (script-enforced, plus your judgment)

High: two+ platforms, ≥80 reviews, observed (not imputed) velocity ≥3/month, tickets from local source, velocities agree within ~3×.

Medium: one solid platform, ≥30 reviews, or imputed velocity with decent stock.

Low: thin data, imputed velocity, capacity clamp, or primary series is not Google.

Drop a grade if delivery/wholesale is likely large, if the GBP pin is one of many, or if first-page review dates are all from a two-week burst.
