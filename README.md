# Lucki

**Land Utilized for Community Kindness Information**

> For a one-person acquisitions lead at a small affordable-ownership nonprofit: the ten sites in any Orange County city to call about this month, with the law that opens each one, every check and its source, the funding gap, and a drafted first call.

**Team:** Lucki
**Members:** Steve Howell
**Lane:** 1 Find it, bent to carry the Fund-it line on every site
**Built at:** Claude Impact Lab: UCI × SoCal Affordable Housing, November 7, 2026
**Tagline:** Sites are found by luck. Lucki makes it.

## The real user

A made-up person: the acquisitions lead at a small OC nonprofit that builds ownership homes. She has no GIS team. Today a site shows up when a city calls about surplus land or a pastor mentions a half-empty parking lot. The laws that opened new land (SB 4, SB 9, SB 684/1123, AB 2011) are public and so is the parcel data, but nobody has joined them in a way she can use before a market-rate buyer does.

**Before:** luck, and 34 cities each with their own maps.
**After:** she picks a city, gets ten ranked parcels with the law, the hazard checks, zoning, transit, opportunity rating, the per-home funding gap, and three drafts (call, text, email) to the organization's office. She verifies, edits, and makes the calls.

## What we built

A single page (a Claude Artifact) over a county-wide candidate set:

- **8,581 candidate parcels across all 34 OC cities**, from four public pathways: religious-use parcels (SB 4 proxy), vacant parcels (SB 9 / SB 684), adopted Housing Element sites, and Surplus Land Act notices.
- **Ranked for a small nonprofit.** Lots up to 5 open acres come first, then homes that fit count up to 24 (Habitat OC projects are 6–12 homes: W. Washington 6, Wellington 9, Fullerton 12), with hazard and pencil factors; "Most homes" is a separate sort. Parcels over 10 acres are flagged for review (campuses, parks, road-crossing parcels).
- **Homes that fit.** For every church, city-approved and public parcel, Lucki asks the county's building-footprint layer which buildings sit on the lot and subtracts their roof area. What's left is open land (parking, dirt, lawn). Homes that fit = the city's own Housing Element capacity where it gave one; otherwise open acres × 20 homes/acre (ASSUMPTION), church land using half its open land (ASSUMPTION), empty single-family lots capped at 4 (SB 9) and other empty lots at 10 (SB 684). Sites in a hazard zone rank as if they had 60% of their homes, and sites that don't pencil even at 0% as if they had 70% (both ASSUMPTIONS). The old seven-part point score is still shown under "Old point score".
- **Checks with sources**: flood (OC Floodplains / FEMA zones), liquefaction (CGS), fire (OC FHSZ LRA), transit (Caltrans HQTA), opportunity (TCAC/HCD 2021), zoning (SCAG 2024). Each shows pass / check / unknown.
- **The Fund-it line**: typical condo value in that city (Zillow), what a four-person family at the bottom of the HCD low band can pay at 6.625%, 3% and 0%, the city's verified per-unit program if one exists, and the resulting gap.
- **Orange County's own 3-inch aerials** (2022) for every ranked site with the parcel outline drawn on top, plus a 2025 county overview.
- **Draft the outreach**: Claude writes a call script, a text and an email to the organization's office, from the facts on the card only. Marked "Draft · never sent". Copy buttons; nothing is sent.

### Does it pencil? (per site, adjustable)

Each new-build site has a small pro forma you can change: homes on the lot, land deal (donated or $1 lease vs bought at market), mortgage rate (0%, 3%, today's 6.6%) and family incomes (low $93,050, moderate $148,850, or a mix).

| Per home (1,000 sq ft) | Amount | Source |
|---|---|---|
| Building | $334,000 | Terner Center, *Making Missing Middle Pencil*, June 2024, LA fourplex-condo hard cost $334/sq ft (2023 $) |
| City fees and hookups | $40,000 | same report, baseline |
| Design, permits, financing | $66,800 | **ASSUMPTION**: 20% of building |
| Land | $125/sq ft of land ÷ homes | same report, LA land; no OC figure found, **ASSUMPTION** for OC |
| Family can pay | $254k at 6.6% · $362k at 3% · $502k at 0% (low income) | HCD 2026 OC limits; 30% of income covers loan, 1.1% tax, $350 HOA, $120 insurance (**ASSUMPTION**) |

What it shows: more families on one lot shrink the land share per home (1 acre bought: $1.36M of land per home at 4 homes, $136k at 40), but the building share stays about $441k per home. Donated or leased land plus a 0% loan is what makes a home pencil for a low-income family; density matters most when land is bought.

### Apartments to convert (the 425 E. Wellington model)

2,791 existing low-rise apartment buildings (SCAG land use 1123) on 0.15–0.45 acres, the size of Habitat OC's 2025 Wellington Ave deal (9 units on 0.21 acres; City of Santa Ana letter A-2025-094: $720k down-payment help for 9 units, $200k relocation). Units estimated at Wellington's density, 43/acre (**ASSUMPTION**). The same land-use code includes condos people already own: confirm it's a rental. Tenants: Wellington gave renters under 120% AMI first right to buy and set aside relocation money.

**Demo video:** uploaded on the hub
**Live demo:** https://claude.ai/artifact/VrgsLJftrxpbRD7cYCKLff (shared for the judges; ask if it won't open)

## How Claude is used

- Built with Claude Code: data pulls, scoring, the page, this README, the video script.
- Inside the tool: the "Draft outreach" button asks Claude (through the artifact viewer's own Claude access, no API key) for three drafts, with only the site's facts as input and an instruction to say "unknown" rather than invent. A person reads and sends.

## Try it

```bash
git clone https://github.com/stevenhowell/lucki-oc
cd lucki-oc
python3 -m http.server 8080 -d site      # open http://localhost:8080
```

That runs the prebuilt site on the cached public data (Python 3.10+, no packages, no keys). Everything works except **Draft the first call** and the **shared** My list, which need the Claude artifact viewer; locally My list saves in your browser.

To rebuild the data: `python3 score.py && python3 add_conversions.py && python3 rank.py`. `score.py` needs the county flood layer at `cache/oc_flood.geojson` (26 MB, not committed): download it from `https://www.ocgis.com/arcpub/rest/services/Map_Layers/Floodplains/MapServer/0/query?where=1%3D1&outFields=FLD_ZONE&outSR=4326&f=geojson` in pages of 1,000 (`resultOffset`). `footprints.py` re-measures open land (slow; be gentle with the county server). The `patch_*.py` files are the edits applied to `site/index.html` during the day.

## Sources and assumptions

| Item | Source or assumption | Date checked |
|---|---|---|
| Religious-use parcels (SB 4 proxy) | SCAG Existing Land Use 2024, `LU24 = 1245` (Religious Facilities per SCAG 2016 legend; 2024 code list not re-verified) | 2026-11-07 |
| Vacant parcels | SCAG Existing Land Use 2024, `LU24 = 3100` | 2026-11-07 |
| Housing Element sites | SCAG `HousingElementSite_poly_scag`, `COUNTY='Orange'` (2,126 sites; Santa Ana and a few cities absent from SCAG's copy) | 2026-11-07 |
| Surplus public land | HCD Surplus Land Act Notices of Availability, data.ca.gov (modified 2026-10-30); all 229 OC rows are status Archive | 2026-11-07 |
| Zoning | SCAG `Zoning_poly_OR` 2024 (`ZN24_CITY`, `ZN24_SCAG`) | 2026-11-07 |
| Flood | OC Public Works Floodplains (FEMA zones); zone X treated as minimal risk | 2026-11-07 |
| Liquefaction | OC Public Works Liquefaction (CGS zones) | 2026-11-07 |
| Fire | OC Fire Hazard Severity Zones, LRA | 2026-11-07 |
| Transit | Caltrans CA High-Quality Transit Areas | 2026-11-07 |
| Opportunity | SCAG TCAC/HCD 2021 Opportunity Areas (2026 map not loaded) | 2026-11-07 |
| Aerials | County of Orange `22_OC_3IN_SP6` (3-inch, 2022) and `Eagle_Aerial_2025_OC_1FT_sid` (overview) | 2026-11-07 |
| Home values | Zillow ZHVI, condo and all-homes, by city, Sep 2026 | 2026-11-06 |
| Income limits | HCD 2026 State Income Limits, Orange County (AMI $138,600; 4-person low band $93,050–$148,850) | 2026-11-06 |
| Mortgage rate | CalHFA FHA 6.625% (rate sheet 2026-11-06) | 2026-11-06 |
| City program | Santa Ana Inclusionary Housing Fund silent seconds, $80k/unit (pre-commitment letter A-2025-094, 2025-07-01). Other cities: unknown | 2026-11-06 |
| Laws | HCD fact sheets for SB 4, SB 9, SB 684/1123, AB 2011; Surplus Land Act guidelines 2024; HCD sites-inventory page | 2026-11-07 |
| Affordability math | **ASSUMPTION**: 4-person household at $93,050; 30% of income covers P&I + 1.1% tax + $350 HOA + $120 insurance; 30-year term | — |
| Open land | County of Orange `Building_Footprints` (754,811 roofs), lot minus roofs whose center is on the lot | 2026-11-07 |
| Homes that fit | **ASSUMPTION**: 20 homes/acre of open land; churches keep half; SB 9 cap 4, SB 684 cap 10 (HCD fact sheets); under 400 m² open = 0 | — |
| Rank | **ASSUMPTION**: homes × 0.6 if in a hazard zone × 0.7 if it doesn't pencil at 0% | — |
| Aerial framing | **ASSUMPTION**: parcel bounding box padded 1.7× | — |

## What is real and what is mocked

| Part | Status |
|---|---|
| Candidate parcels, zoning, hazards, transit, opportunity | working, real public data, cached in `cache/` |
| Scoring | working; weights are an assumption |
| Aerials | working for the ranked sites (top 10 county-wide, top 10 per city, top 3 per pathway per city); other parcels show a Google Maps link |
| Fund-it line | working; income, rate, values and the Santa Ana program are sourced; the household and cost assumptions are labelled |
| Institution name and office contact | partly working: surplus-land notices carry the agency contact (person's name omitted); faith-land parcels show "owner unknown" unless an OpenStreetMap place of worship sits on the parcel (the county-wide OSM pull failed on the day, so most show unknown) |
| Draft outreach | working inside the Claude viewer; nothing is sent |
| Historic-district check, SB 9 exclusion tests, utility capacity | not loaded: shown as unknown |

## Where it gets things wrong

- "Religious Facilities" in land-use data is not proof of religious ownership; SB 4 needs the owner to be a religious institution or an independent college. Treat it as a lead.
- Housing Element sites can be stale: a city listed them at adoption; some have sold or been built.
- All OC surplus-land notices in the state file are archived (the notice window closed). The agency may still hold the land, or may not.
- Hazard checks use the parcel centroid, not the whole polygon.
- Open land counts every unroofed square foot, including parking a congregation or agency needs; the church share assumption only partly corrects for that.
- Footprints may be a few years old; a lot built on since will look emptier than it is.
- Closed school sites and county-owned land were tried and left out: the state school layer lists only open schools, and the county property list is points (mostly parks and offices) with no lot outline.
- Values are city-wide typical condo values, not an appraisal of the site.

## Next steps

- Load the County Assessor roll (by request) to confirm ownership for faith-land parcels.
- Add each city's inclusionary / down-payment program with a source; today only Santa Ana is verified.
- Run the hazard tests on the full polygon and add historic districts and SB 9 exclusion layers.
- Let the user mark "called / meeting / passed" so the list becomes a pipeline. Next 100 projects: run the same scorer for the 33 other cities' staff, who already have the data we joined.

## Data and privacy

This project uses only public or provided data. It contains no personal information about real tenants, buyers or residents. Owner names are not loaded. Surplus-land contacts keep only the agency and its phone number; the staff member's name and email from the state notice file were removed from every data file. It does not file applications or contact any city or person: drafts are shown for a human to edit and send.

## License

MIT, see LICENSE.
