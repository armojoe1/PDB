---
name: daily-pdb
description: Generate a mock President's Daily Brief (PDB) as a polished PDF in the modern declassified house style — White House engraving, TOP SECRET//NOFORN banners, bold article headlines, estimative "we assess / likely / probably" prose, bulleted sub-judgments, ★★★ dividers, and "Prepared by ODNI…" source lines. Every item is REAL, built from reliable open sources covering the last ~24 hours, then written as if it came from US intelligence (a light touch, not a costume). Use this skill whenever the user asks for their PDB, the President's Daily Brief, the morning brief / intel brief / daily brief, "make today's PDB", "generate my brief", "what would the President be reading today", a daily world-events intelligence briefing, or asks to schedule/produce a recurring morning brief in this style. Defaults to a multi-article, threat-weighted, global brief.
---

# Daily President's Daily Brief (mock)

This skill produces a **mock PDB**: a real, analytically strong, well-sourced briefing on the day's most consequential world events, *formatted and written to read like* the President's actual daily intelligence brief. The intelligence-community styling is a deliberate, light dressing — **accuracy and sourcing come first, costume second.**

The look it reproduces is the **modern** declassified PDB (the post-2010s format: White House line-engraving, red corner flash, a bold article headline, single-column lead paragraph followed by bulleted sub-assessments, ★ ★ ★ section dividers, "Continued . . ." across page breaks, and an italic "Prepared by [agency] with reporting from …" source line). A bundled renderer (`scripts/render_pdb.py`) draws all of that from a small JSON file, so you never have to lay out the PDF by hand.

## The order of operations (important)

**Research first, format last.** Do all the searching, reading, and cross-checking before you touch the renderer. The quality of this product lives entirely in (a) picking the right stories and (b) getting the facts right and the analysis sharp. Concretely:

1. **Confirm the date and window — and stay strictly inside it.** Check today's date (`date`). The brief covers the **rolling ~24 hours** ending this morning (≈ yesterday 06:00 to today 06:00 US Eastern). The *news hook* of every item — the thing that makes it news *today* — **must have broken or materially advanced within that 24-hour window.** This matters a lot because this brief is generated daily: if you include a development that actually happened two or three days ago, tomorrow's brief (and the day after) will surface the same story and the editions will repeat. So for each candidate, ask: "what specifically happened in the last 24 hours?" If the honest answer is "nothing new — this is just an ongoing situation," **leave it out** and find something that genuinely moved. A running conflict only earns a slot on a day it produced a concrete new event (a strike, an announcement, a signing, a casualty figure, a leadership decision). One sentence of standing context to orient the reader is fine; the lead and the bullets must be about what changed in the window. When you cite a development, note its date in your own checking and discard anything older than ~36 hours unless it genuinely broke overnight.
2. **Scan the priority lanes and pick the lead stories** (see "What leads").
3. **Research each story to ground truth** with fresh web search — never from memory (see "Sourcing").
4. **Write each item** in the house voice (see "Voice").
5. **Assemble the brief JSON** and **render the PDF** (see "Build the PDF").
6. **Save and present** the PDF; one or two sentences on the day's top-line judgments.

Do not narrate the research blow-by-blow; work through it and deliver the brief.

## What leads (editorial judgment)

Weight the brief by **consequence to US national security and presidential decision-making**, wherever in the world that is today. Follow the news, not a fixed beat. Scan these lanes every morning and pull the genuinely most important developments:

- **Great-power competition** — China (Taiwan, South China Sea, tech/export controls), Russia (Ukraine), and Beijing–Moscow coordination.
- **Active conflicts & flashpoints** — Ukraine; the Middle East (Israel/Gaza, Iran, Red Sea/Houthis, Lebanon, Syria); the Korean Peninsula; the Sahel; any newly hot crisis.
- **Iran nuclear file; DPRK missiles/nukes.**
- **Terrorism & transnational threats** — ISIS/al-Qaeda affiliates, major plots, hostage situations.
- **Strategic economics & energy** — oil shocks, sanctions, critical-minerals/supply chains, major-economy instability, market-moving geopolitics.
- **Cyber, space, emerging tech** with security implications.
- **Artificial intelligence with national-security weight** (see the dedicated section below) — frontier-capability jumps, AI in weapons/cyber, compute/chip controls, state AI programs, and above all any credible sign of **recursive self-improvement (RSI)**. Include only when genuinely major — not every day.
- **Leadership & stability** — elections, coups, successions, mass unrest, leader health in consequential states.
- **International summits, meetings, and new alignments** — actively track major multilateral gatherings (G7, G20, BRICS, SCO, NATO, EU Councils, UN General Assembly, AUKUS/Quad, ASEAN, OPEC+, bilateral leader summits) **and their aftermath** — the joint statements, communiqués, deals, and commitments that come out of them, plus the days-after follow-through or fallout. Be **especially alert to countries grouping together**: new or deepening blocs, coalitions, and alignments (e.g., expanded BRICS membership, a new minilateral on defense or technology, coordinated sanctions or export-control regimes, a fresh security pact, states ganging up diplomatically on an issue). Realignments among major powers and middle powers are exactly what the President's brief watches, because they reshape the balance the US operates in. When a summit happens, carry what was agreed and the *"so what"* for US interests; in the days after, carry the concrete consequences. A scheduled summit by itself is calendar trivia — the news hook is a *result, statement, deal, or realignment* from within the 24-hour window.
- **Allied & partner politics with US consequences** — and this is easy to under-weight, so watch for it. The real PDB closely tracks political shifts in close allies and key partners (UK, Germany, France, Japan, South Korea, Australia, Canada, Israel, India, the Gulf, NATO members, major trading partners) because a change in government or leadership there directly affects US policy — defense spending, basing, sanctions cohesion, trade, intelligence sharing, support for Ukraine, etc. Treat as in-window and brief-worthy: **a by-election, no-confidence vote, coalition collapse, resignation, leadership challenge, snap-election call, or election result that could change who leads an allied/partner government** — and always frame the *"so what" for the United States* (what shifts in policy, what Washington should watch). Example: a UK by-election loss that threatens the Prime Minister's majority or could force a leadership change is exactly the kind of item to carry, with a line on the implications for US–UK cooperation, Ukraine support, AUKUS, and trade.

**Default shape:** a multi-article book of **at least 7 entries**, threat-weighted and global. Count the `Notes` section as one entry, so a typical brief is roughly **6 or more full articles plus a `Notes` block** of 2–4 shorter items (= 7+ entries total). Always reach 7; if a slow news day makes 7 *substantive, in-window* items hard, expand the Notes block with genuinely fresh shorter developments rather than padding with stale or trivial material — but never drop below 7, and never manufacture an item that didn't actually move in the last 24 hours. If one story clearly dominates the day (a war escalation, a summit, a major attack), let it lead and give it more space. Keep each article tight: a lead assessment paragraph plus 2–5 bulleted sub-judgments, sometimes a ★★★ break into a related sub-item.

## US carrier strike group movements (only when it fits a story naturally)

When a carrier strike group (CSG) or amphibious ready group is **genuinely relevant to one of the day's stories** — e.g. a Middle East piece where a carrier is operating in support of regional operations, or a Taiwan/South China Sea item where a CSG is on station — you may **work a brief locational line into that story**. Keep it to a sentence or two inside the relevant article; write it in the clipped, present-tense register the real product uses, naming the hull where confirmed:

> *"The Gerald R. Ford Carrier Strike Group is operating in the Eastern Mediterranean, within strike range of the theater."*

**Do not overdo it.** This is not a standing daily section and should not get its own article on a routine day — only include it when it adds something to a story that's already leading. Most days it won't appear at all, and that's correct.

It must rest on **reliable open reporting** — the **USNI News "Fleet and Marine Tracker"**, official US Navy / numbered-fleet / combatant-command releases and photo captions, or reputable defense outlets reporting confirmed movements. **Never** infer precise ship positions from rumor, ship-spotter social posts, or guesswork; naval movements are sensitive and frequently misreported. If the reporting supports only a general area, stay general — and if you can't stand it up, leave it out entirely.

## Artificial intelligence (include an AI item only when it's genuinely major)

Scan each day for AI developments with real national-security or strategic weight, and give one its own article **when — and only when — it clears a high bar.** Most days nothing will qualify, and that is the correct outcome: do not force an AI entry, and do not let a routine product launch, funding round, or benchmark bump take a slot. The President's brief would carry AI only when it could move the national-security needle.

**What clears the bar (any of these, if real and in the last 24 hours):**

- **Recursive self-improvement (RSI) / self-improving AI** — the single most important trigger. Any *credible* sign that a system is meaningfully improving itself, automating its own research, or showing a step-change in capability that points toward an intelligence takeoff. Treat this as potential lead-article material. Because claims here are easily hyped, hold it to a high evidentiary standard (a credible lab announcement, a peer/technical writeup, or corroborating reporting from serious outlets) and **calibrate the language hard** — distinguish a demonstrated capability from a marketing claim, and say which it is.
- **A frontier-capability jump** with security implications — a model crossing a threshold in cyber-offense, bio/chem uplift, autonomy, or weapons-relevant reasoning; or credible evaluations showing dangerous capabilities.
- **AI in the military/intelligence domain** — autonomous weapons milestones, AI integrated into targeting/C2, an AI-enabled cyber operation, or a state standing up a major military-AI program.
- **Compute and controls** — major chip/export-control actions, large state compute build-outs, or a supply-chain move that shifts the AI balance of power (e.g., leading-edge fabs, GPU access).
- **State AI programs & governance shocks** — a national frontier-AI effort, a binding regulation or treaty, a serious safety/security incident at a major lab, or evidence of an adversary's AI weapons/cyber progress.

**How to handle it:** write it in the same estimative voice as any other item, lead with the "so what" for US security, and end on what to watch. Be especially disciplined about sourcing and hedging — AI is a field of loud claims. Good sources: the major labs' own announcements (read critically), serious technical writeups, and reputable outlets (Reuters, Bloomberg, FT, the better trade and security press); for capability/eval claims, prefer primary or technical sources over secondhand hype. If you cannot corroborate it or it's just promotion, leave it out. Credit it in the source line to the elements that would own it — e.g. *"Prepared by ODNI with reporting from the National Security Agency, the Office of Science and Technology, and open sources."*

## Sourcing (the part that makes it credible)

Search the web fresh each morning and build every item from **primary and high-reliability** open sources. Cross-check anything consequential against **≥2 independent reliable sources** before it goes in. Rough order of trust:

**Tier 1 — primary / authoritative.** Official statements & readouts (White House, State, DoD, ODNI, Treasury/OFAC, the combatant commands, foreign ministries, the Kremlin/PRC MOFA — read as *positions*, not ground truth); multilateral bodies (UN/UNSC/OCHA, IAEA, NATO, EU, IMF, OPEC); official data releases, central-bank communiqués, election commissions, court filings.

**Tier 2 — wires & papers of record (the daily backbone).** Reuters, AP, AFP, Bloomberg; NYT, Washington Post, Wall Street Journal, Financial Times, The Economist; BBC, The Guardian.

**Tier 3 — specialist & regional depth/early signal.** Defense/security: Defense One, Breaking Defense, War on the Rocks, Janes, Naval News. Conflict trackers/think tanks: ISW (daily campaign assessments at understandingwar.org), ACLED, Crisis Group, CSIS, Carnegie, Atlantic Council, RUSI, IISS, Bellingcat. Regional outlets where they lead: Al Jazeera, Times of Israel, Haaretz, Kyiv Independent, South China Morning Post, Nikkei Asia, Times of India, Yonhap, NK News. Proliferation: IAEA, Arms Control Association, James Martin CNS. Energy/econ: Bloomberg, Reuters, FT, S&P Global, Argus/OilPrice.

**Rules:**
- Anchor core facts in Tier 1/2; use Tier 3 for specialist depth, early signal, and on-the-ground texture.
- Be explicit (to yourself, and via hedging in the text) about what's **confirmed** vs. **reported** vs. **claimed by one party**.
- If `WebFetch` returns a JS-shell/empty page, switch to the Chrome browser tools to read the real content. Never fabricate to fill a gap.
- **No** low-reliability sources, anonymous social posts, or single-source rumor for any factual claim. If you can't stand it up, leave it out.

## Pre-flight checks (run these on every item before it goes in)

Two specific mistakes are easy to make from search snippets and both badly damage credibility. Guard against them deliberately:

**1. Date-stamp every item and enforce the 24-hour window — ruthlessly.** Search results love to surface a story's *background* (events from days or weeks ago) alongside today's news. For **each candidate item, and each factual claim inside it, write down the date the thing actually happened** and confirm it falls in the last ~24 hours (≈ yesterday 06:00 → today 06:00). If a bullet's anchor event is from, say, four days ago, it is **stale — cut the bullet or the whole item**, even if the topic is important. A topic being newsworthy in general is not a license to run a days-old event as if it were today's news; doing so also guarantees repetition when the brief runs daily. Before finalizing, re-read every item and ask: "what here happened in the window?" If the answer for an item is "nothing — this is just an ongoing situation," remove it and replace it with something that genuinely moved. Do not keep a stale item merely to reach the 7-entry minimum; find a fresh one instead.

**2. Verify the *current* status of every named person, office, and government — do not trust your priors or an old snippet.** Leaders fall, get arrested, lose elections, resign, or die, and search snippets frequently describe them in an outdated role. Before naming someone as a head of state, minister, CEO, commander, etc., **confirm from current (in the last few weeks) reporting that they still hold that position.** This is exactly the kind of thing the real PDB never gets wrong. Concretely: if you're about to write "President X did Y," first check that X is still president *today*. (Illustrative: a leader who has been captured, detained, ousted, or replaced must not be referred to by their former title — name the current officeholder instead.) When in doubt, search "who is the current [office] of [country] [today's month/year]" and use the live answer. Apply the same care to whether a war is still ongoing, a ceasefire still holds, a sanction is still in force, and a deal is still in effect — states of the world change.

Treat both checks as mandatory gates, not nice-to-haves: an out-of-window event or a wrong/again-outdated officeholder is a factual error of the kind this product exists to avoid.

## Voice (make it read like the IC — lightly)

Channel the register of real finished intelligence: measured, declarative, analytically confident but **calibrated**. A *few* IC-flavored touches per article, not every line.

- **Estimative language:** *"We assess…," "We judge…," "likely," "almost certainly," "probably," "we expect," "there is a realistic possibility that…"* Calibrate it — don't say "almost certainly" about a maybe.
- **Source texture, used sparingly and only where the open reporting genuinely supports it,** kept non-specific: *"Press reporting and official statements indicate…," "Open-source imagery shows…," "Multiple outlets corroborate…."* Do **not** invent secret intercepts, HUMINT, or imagery you don't actually have via OSINT.
- **Lead with the judgment, close on the "so what."** Open each article with the bottom-line assessment; end on implications / what's likely next / what to watch — the way real PDB items resolve.
- **Give each entry a little more "what it means for the US" and "probable next steps" — where it genuinely adds something.** The President reads this to decide and to anticipate, so most entries benefit from a sentence or two of *US-relevant analysis* (how this affects US interests, allies, forces, economy, or freedom of action) and a sentence on *what is likely to happen next* (the probable next move, the decision point, what would confirm or change the judgment). Fold it into the lead paragraph or a closing bullet — naturally, in the estimative voice (*"For Washington, the key question is…," "We expect Beijing's next step will be…," "A decision point comes when…"*). **But do not overdo it or make it formulaic:** not every entry needs both, a short Note may need neither, and you should never bolt on a generic "this matters for the US" line that says nothing. Add the implication or the next-step only when you have a real, specific point to make; if the item is purely factual and the significance is obvious, leave it clean. The test is whether the added sentence would actually help a decision-maker — if not, cut it.
- **Headlines are analytic, not breathless** — e.g. *"Cyber Threats to US Election Unlikely To Alter Voting Outcomes,"* *"China Steps Up Pressure Around Taiwan Ahead of Defense Review."* Title Case, no clickbait.
- **Source line:** end each article with an italic *"Prepared by ODNI with reporting from [the IC elements most relevant — e.g. CIA, DIA, NSA, INR, NGA, FBI, DHS, State] and open sources."* Vary the named elements to fit the topic (INR for diplomacy, NGA for imagery, NSA for SIGINT-flavored items, Treasury OIA for sanctions/finance, FBI/DHS for homeland).

### The "intelligence-asset" flourish (sparing, and only on near-certain facts)

Occasionally drop in a single short sentence that attributes a fact to a secret collection source — the touch that makes it *read* like classified intelligence. Examples of the register:

- SIGINT: *"NSA SIGINT confirms the order originated at the ministry level."* / *"Intercepted communications corroborate that the strike was directed from [capital]."*
- Imagery: *"Overhead imagery confirms the vessels departed [port] on 18 June."* / *"NGA assesses from satellite imagery that the launchers have been moved forward."*
- HUMINT / liaison: *"A sensitive source confirms the leadership has authorized the deployment."* / *"Liaison reporting corroborates the figure."*
- Cyber: *"Collection on the ministry's networks indicates the decision was finalized this week."*

Hard rules for this device — read them carefully, because misused it becomes fabrication:

1. **Only attach it to a fact that is, in your judgment, almost certainly true** on the open reporting — something already well-corroborated by Tier 1/2 sources. The secret-source attribution is a *stylistic overlay on an established fact*; it must never be the thing that introduces or "confirms" a claim the open reporting doesn't already strongly support. If a fact is contested, single-sourced, or speculative, it does **not** get this treatment.
2. **Never invent the underlying fact, a quote, a number, or a specific covert operation.** You are dressing a known, near-certain fact in IC clothing — not manufacturing intelligence. Keep the asserted detail consistent with what's publicly established and keep it non-specific (no fabricated codenames, no invented intercept transcripts, no named human sources).
3. **Frequency: at most ~3 across the whole brief, and often fewer (sometimes zero).** Most entries should have none. Spread them — don't stack them in one article, and don't use the same source type every time; vary across SIGINT, imagery, HUMINT/liaison, and cyber to fit the story (imagery for movements, SIGINT for orders/comms, HUMINT for decisions/intent, cyber for finance/decision-making). It should feel like an occasional confirming detail, not a tic.
4. **Match the source to the element in the article's "Prepared by" line** (e.g., an NSA SIGINT line pairs with NSA credited in the source line; an imagery line with NGA).

Used well, this is a rare, well-placed confirming sentence on something that's essentially certain anyway — which is exactly why it lands without undermining accuracy.

Don't overdo the spy-novel flavor; the credibility is in the analysis and the calibrated hedging. The intelligence-asset flourish above is the one sanctioned exception, and it stays sparing.

## Modern institutional framing (this is today's PDB, not 1976)

- It is an **ODNI / DNI** product. As of 2025 the **DNI owns and assembles the PDB** (assembly moved from CIA to ODNI in May 2025); CIA and other elements still author much of the analysis. Refer to "ODNI," "the DNI," "the IC," and individual elements — **not** "the CIA" as the producer.
- The modern **US Intelligence Community has 18 elements**: ODNI, CIA, DIA, NSA, NGA, NRO; the intelligence elements of the Army, Navy, Marine Corps, Air Force, Space Force, and Coast Guard; State (INR); Treasury (OIA); Energy (OICI); DHS (I&A); and DOJ's two — FBI Intelligence Branch and DEA Office of National Security Intelligence.

## The White House emblem

The renderer sets all text in **Carlito**, the metric-compatible open clone of **Calibri** (the typeface the real modern PDB uses); the four font files are bundled in `assets/fonts/`, and if real Calibri is installed it's used instead. The masthead band at the top of each story places **"For the President" + date on the left and the emblem on the right, vertically aligned on the same row above a full-width rule** — matching the real PDB exactly.

The emblem appears in that masthead **at the top of each story (its first page only)** — next to the header — and is **not** repeated on a story's continuation pages. (The red corner flash and the TOP SECRET//NOFORN banners, by contrast, are page-level markings and appear on every page.) The emblem ships as `assets/whitehouse.png`, sized to match the real PDB. To use a different/exact emblem image, either replace `assets/whitehouse.png` or set `"emblem": "/path/to/your.png"` in the brief JSON — the renderer reads the image's aspect ratio so it won't distort. If the source image has a white background, knock it out to transparent first so it doesn't sit in a white box on the page.

## The SCI cover sheet

When `cover` is true (the default), page 1 is the **user-supplied cover PDF**, bundled at `assets/cover.pdf` and prepended **verbatim** (byte-for-byte, never re-drawn or edited) in front of the brief. The actual content begins on page 2. To use a different cover, replace `assets/cover.pdf` or set `"cover_pdf": "/path/to/cover.pdf"` in the brief JSON. Set `"cover": false` to omit the cover entirely.

The merge uses **pypdf** (`pip install pypdf`); if it's unavailable or the cover PDF is missing, the renderer falls back to content-only output so the brief is still produced.

## Classification cosmetics

- The banner top and bottom of every page is **`TOP SECRET//NOFORN`** (the realistic marking a finished PDB-style product carries — Top Secret, releasable to No Foreign nationals). This is the default in the renderer; you don't need to set it.
- **Do not** print an "APPROVED FOR RELEASE BY THE DNI ON …" line. That stamp appears only on *declassified* copies; this is styled as the live product, so it's omitted (the renderer leaves it off by default — don't set `release_stamp`).
- This is a mock built from open sources. Keep the *look*; never present a fabricated secret as real intelligence.

## Build the PDF

Once the content is researched and written, assemble a `brief.json` and render. **Read `references/brief_schema.md` for the exact JSON shape** — here's the essence:

```json
{
  "date": "YYYY-MM-DD",
  "cover": true,
  "articles": [
    {
      "headline": "Analytic Title-Case Headline",
      "blocks": [
        { "type": "para", "text": "We assess that ... <lead judgment>." },
        { "type": "bullets", "items": ["Sub-judgment one ...", "Sub-judgment two ..."] },
        { "type": "stars" },
        { "type": "para", "text": "Related sub-item lead ..." },
        { "type": "bullets", "items": ["..."] }
      ],
      "prepared_by": "Prepared by ODNI with reporting from CIA, DIA, NSA, INR, and open sources."
    }
  ]
}
```

Then render (the script lives in this skill folder; adjust the path to wherever the skill is installed):

```bash
python scripts/render_pdb.py brief.json "PDB_YYYY-MM-DD.pdf"
```

The renderer handles all the furniture automatically: `TOP SECRET//NOFORN` banners top & bottom, the White House engraving + red corner, the cover page, the date header, bullet formatting, the ★★★ dividers, and **"Continued . . ."** on any page an article runs past. Sanity-check it with `--sample` if needed (`python scripts/render_pdb.py --sample` drops a sample PDF next to the script).

**Deliverable conventions:**
- Filename **`PDB_YYYY-MM-DD.pdf`**.
- Save it to the user's PDB folder (e.g. `/Users/joea/Desktop/PDB/`) and present it with the file card.
- Close with one or two sentences on the top-line judgments of the day — not a long recap. If something was still developing at brief time, say so ("still developing as of [time]") rather than forcing a conclusion.

## Optional: structure & length variants

- **Tight brief:** a single deep-dive article (`cover: false`, one `articles` entry) on the day's dominant story — shorter, sharper.
- **With contents page:** add a `toc` array of one-line `{tag, summary}` entries for a long book; the renderer prints a "Today's Brief" contents page before the articles.

## Optional: run it automatically each morning

If the user wants it daily, offer to schedule it (e.g. "every day at 6:30am"). The scheduled task's prompt should be: *"Generate today's PDB"* — this skill does the rest, searching the prior 24 hours fresh on each run and dropping a new `PDB_<date>.pdf` in the PDB folder.
