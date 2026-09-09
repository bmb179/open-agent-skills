# Collecting review signals

The script only multiplies. Bad velocity in → confident-looking garbage out.

## Platform roles

- **Google Business Profile / Maps** — default primary demand series for US local businesses. Google holds the majority of local-review inventory (industry trackers often put it around 50–75% depending on category).
- **Yelp** — corroboration. Often 10–30% of the Google count for the same shop. Still useful for restaurants and some urban home-services. A 5:1 Google:Yelp ratio is normal, not evidence the shop is dying on Yelp.
- **Meta / Facebook recommendations** — weak volume series. Use for community businesses; do not add to Google velocity.
- **TripAdvisor / Booking** — first-class for hotels. Record in `--notes`. Script volume still prefers Google unless Google is empty.
- **Angi / Thumbtack / HomeAdvisor** — home services. Notes only.
- **Healthgrades / Zocdoc / Vitals** — medical. Notes only.
- **Apple Maps** — usually a subset of Google; skip unless Google is missing.

Treat a missing platform as information (never listed, unclaimed, or too new).

## How to estimate Google velocity

Google rarely prints “reviews in the last 30 days.”

1. Open the most-recent reviews sort.
2. Count dated reviews in the last ~30 days (or 90 days / 3). Ignore “a year ago” stacked on page 1 if the sort failed.
3. First page is recency-biased. If the first 10 reviews span 3 days at a shop with 40 lifetime reviews, that is a burst, not a run-rate — prefer 90-day or note `--solicited`.
4. If dates are only relative (“2 months ago”), bucket them.
5. If you cannot see dates at all, leave `--google-velocity` at 0 and pass `--years-open` (or first-review year). The script will impute from min(years_open, 4) so a 20-year stock does not get divided by 240 months.

Do not divide lifetime reviews by 3.5 years by hand. That is what `--years-open` is for.

## Ratings vs reviews vs recommendations

- Google shows a rating count that can exceed the written-review count. Prefer **written reviews** for velocity. If only the headline rating count is visible, say so in notes and treat velocity as softer.
- Facebook “recommend” is not a star review. Pass it as `--meta-reviews` but expect Low/Medium confidence if it is the only series.
- Yelp “not currently recommended” filtered reviews are hidden from the public count — do not try to add them back.

## Disambiguation

- Chains: scrape the **this location** pin, set `--chain`, and only pass `--locations N` if you are deliberately scaling a typical-unit estimate.
- Duplicate GBP listings, “permanently closed,” and service-area businesses that hide a real address all distort counts.
- Food trucks / pop-ups / ghost kitchens: Google pin may represent a commissary. Flag in notes.
- Same trade name in two cities: confirm the Maps pin matches the user’s location.

## Solicitation and fakes

Signs of a review program (pass `--solicited`): QR table tents, “review us and get 10%” language (also a ToS risk), SMS receipts, every review arriving in the same week, near-100% 5-star with generic one-liners, owner replies that are identical.

Localo and similar GBP studies find Google removes a disproportionate share of 5-star reviews — a sudden drop in count is not always lost demand.

Womply’s 3.5–4.5★ revenue sweet spot is another reason not to treat 5.00★ / 12 reviews as a high-volume shop.

## Capacity tells you can usually find without asking the owner

- Restaurants: seat count from photos, OpenTable, or “about.” Hours → `--days-open-month`.
- Hotels: room count from Booking/OSM/brand page. Pair with market ADR.
- Salons: chair count from interior photos.
- Auto: bay count from street view / interior.
- Dental: operatory count sometimes on the practice site.

If implied daily covers exceed seats × reasonable turns, pass the seat count so the high case clamps.

## Sources that are not substitutes for this scrape

GBP Insights (calls, direction requests) are first-party and usually unavailable. Do not invent them.

County sales-tax or alcohol-permit data, franchise AUVs, and health-department peer lists are the right *external* sanity checks after the script runs.
