# Classification rubric — incoming Democratic members, 120th Congress (elected 3 Nov 2026)

Purpose: sort each incoming Democrat into one of four buckets using OBSERVABLE, CITABLE evidence.
Researchers record evidence per marker; the scores are computed afterwards from the marker values,
so record marker values honestly and conservatively. Never infer a position from party label,
district, demographics or "what Democrats usually believe". If you cannot find it, record 0.

Marker values:  1 = explicit public evidence the person holds this position (quote, questionnaire answer,
platform page, pledge, vote, bill sponsorship, endorsement acceptance)
                0 = no evidence found either way
               -1 = explicit public evidence they REJECT this position
Each marker with value 1 or -1 must carry a one-line evidence note and a source URL.

## TEST 1 — Left-Ideology Index (LI)  → Category 1 "Ideological left"
| Code | Marker (value 1 if they publicly support…) | Points if 1 |
|---|---|---|
| L1 | A wealth tax / annual tax on net worth, OR a top income-tax rate ≥ 50%, OR corporate rate above 28%. (Generic "make billionaires pay their fair share" = 0.) | 1 |
| L2 | Substantially lowering the estate-tax exemption (e.g. to ≤ $3.5M, "For the 99.5% Act") or raising estate-tax rates | 1 |
| L3 | Medicare for All / single-payer that replaces private insurance (a public option alone = 0) | 1 |
| L4 | Public ownership / nationalisation of an industry or major assets (utilities, pharma, energy, rail, etc.), public/social housing at national scale as an ownership model, OR self-identifies as a democratic socialist / DSA member | 2 |
| L5 | Green New Deal, or a ban on fracking / new fossil-fuel production | 1 |
| L6 | Aggressive anti-corporate measures beyond the party mainstream: statutory break-ups of big tech/banks, banning stock buybacks, federal price controls, worker seats on corporate boards, federal jobs guarantee, UBI | 1 |
| L7 | A contested trans-policy position: trans women/girls in female sports, OR opposes any age limits on medical gender transition for minors, OR similar. (Supporting the Equality Act / generic "protect trans people" = 0) | 1 |
| L8 | Government regulation of online "misinformation / disinformation / hate speech" (platform liability for misinformation, Fairness-Doctrine revival, etc.) | 1 |
| L9 | Defund/abolish the police, abolish ICE as an agency, or decriminalise unauthorised border crossing | 1 |
| L10 | Expanding the number of Supreme Court seats (term limits / ethics code alone = 0) | 1 |
| L11 | DC and/or Puerto Rico statehood, or abolishing the Electoral College | 1 |
| L12 | Calls Israel's Gaza campaign a "genocide" or backs a full arms embargo on Israel | 1 |
| L13 | Left movement endorsements: Justice Democrats or DSA (national or local chapter) = 2 each; Working Families Party, Our Revolution, Sunrise, Bernie Sanders personally, AOC personally, Congressional Progressive Caucus PAC, Progressive Change Campaign Committee, Leaders We Deserve = 1 each. Cap 3. Record the list. | 0–3 |

LI = sum. **LI ≥ 6 → Category 1.**  LI 4–5 = progressive-leaning (not enough on its own).

## TEST 4 — Centrism Index (CI) → Category 4 "Clinton-style centrist"
| Code | Marker (value 1 if…) | Points |
|---|---|---|
| C1 | Centrist coalition ties: Blue Dog endorsement/membership = 2; New Democrat Action Fund endorsement or stated intent to join New Democrat Coalition = 1; WelcomePAC / Majority Democrats / Problem Solvers / No Labels / Third Way backing = 1. Cap 3. Record the list. | 0–3 |
| C2 | Explicitly opposes Medicare for All / single payer; favours fixing/building on the ACA | 1 |
| C3 | Fiscal centrism: emphasises deficit reduction / balanced budget / opposes raising taxes on all but the very top AND does not back a wealth tax or large rate hikes | 1 |
| C4 | Border/immigration hawkish for a Democrat: campaigns on border security/enforcement, backed Laken Riley-type measures, explicitly rejects "abolish ICE" | 1 |
| C5 | Explicitly rejects "defund the police", campaigns on funding police, or endorsed by police unions/FOP | 1 |
| C6 | Publicly breaks with progressive cultural positions (e.g. supports limits on trans athletes in female sports, parental-rights framing, criticises "woke" politics, notably pro-gun-owner) | 1 |
| C7 | Independence from party: said they won't back Schumer/Jeffries for leader, criticised the party as too far left, got Republican endorsements, or has a documented bipartisan voting record | 1 |
| C8 | Pro-growth / pro-business: "all of the above" energy incl. oil & gas, permitting reform / pro-housing-supply ("abundance"), pro-trade, business-group endorsements (e.g. Chamber of Commerce) | 1 |

CI = sum. **CI ≥ 5 and LI ≤ 3 → Category 4.**

## TESTS 2 & 3 — for members who are neither clearly left (Cat 1) nor clearly centrist (Cat 4)

### EPD — Experience & Policy Depth (0–7)  [proxy for "experience/intellectual heft"; we do NOT assess intelligence]
- EPD_office (0–3): 0 no prior office or senior public role; 1 local office (city council, school board, county commission, party post, neighbourhood council); 2 state legislature, mayor of a mid/large city, county executive, senior federal staff/appointee, prosecutor/DA, military O-5/O-6; 3 statewide office, former member of Congress, cabinet-level/senior federal executive, flag officer (general/admiral)
- EPD_cred (0–2): 0 no degree / thin professional record; 1 bachelor's + mid-level career; 2 advanced professional degree (JD, MD, PhD, MBA, MPP from a strong programme) OR a senior professional career
- EPD_policy (0–2): 0 slogans only, generic or missing issues page, little substance in interviews; 1 some concrete proposals; 2 detailed, specific proposals with numbers/bill names, or an authored legislative record

### EO — Engagement & Openness (0–5)  [proxy for "aloof / dismissive / won't debate"]
- EO_debate (0–2): 0 declined or avoided all general-election debates they were invited to (or the only debates were ones they skipped); 1 did some but ducked others; 2 debated in all/most offered (primary and general)
- EO_media (0–2): 0 largely avoided unscripted press / town halls; 1 mainly friendly or controlled settings; 2 regular unscripted interviews and town halls, incl. hostile / cross-partisan outlets
- EO_substance (0–1): 1 if they engage the substance of opposing arguments; 0 if they mostly dismiss opponents with labels without engaging, or refuse to state positions on contested issues when asked

### FD — Base dependence (descriptive; pre-computed from FEC where available)
- small_dollar_share = unitemized (<$200) individual contributions ÷ all individual contributions (FEC, through 14 Oct 2026). ≥ 0.40 = high; 0.20–0.40 = typical; < 0.20 = large-donor funded.
- Also record major outside-spending/organisational backers for the candidate (both left groups like WFP/JD/MoveOn/Indivisible/Sunrise/Leaders We Deserve and others like DCCC Red-to-Blue, House Majority PAC, AIPAC/UDP, DMFI, Fairshake crypto, unions, EMILY's List, VoteVets).

### Decision sequence (applied centrally)
1. LI ≥ 6 → **Cat 1**
2. else CI ≥ 5 and LI ≤ 3 → **Cat 4**
3. else EPD ≤ 3 → **Cat 2** (thin experience/substance; follows the party line; base funding strengthens the call)
4. else EO ≤ 2 → **Cat 3** (credentialed, but avoids debate/scrutiny and stays vague)
5. else (credentialed, engaged, mainstream) → nearest of Cat 1 / Cat 4 by LI vs CI, flagged "imperfect fit"
Confidence is lowered where evidence is thin or markers conflict.
