# Democratic Caucus 2027: a four-way sort

This folder sorts every Democrat who will sit in the 120th Congress from 3 January 2027 into four analytical groups. That is 320 members: 264 in the House (including 4 non-voting delegates) and 56 in the Senate (including 2 caucusing independents). The sort uses a published, repeatable test. Research cut-off: 11 November 2026, eight days after the midterms.

Open `report.html` in a browser for the interactive report. It has the split, the findings, an ideology map, and a filterable roster with the evidence and sources for every member.

## The four groups

| # | Group | Test |
|---|---|---|
| 1 | Ideological left | Left-Ideology Index (LI) ≥ 6 |
| 2 | Inexperienced & base-dependent | Not 1 or 4, and Experience & Policy Depth (EPD) ≤ 3. Small-donor share and activist backing adjust confidence. |
| 3 | Credentialed but disengaged | Not 1 or 4, EPD ≥ 4, and Engagement & Openness (EO) ≤ 2 |
| 4 | Clinton-style centrist | Centrism Index (CI) ≥ 5 and LI ≤ 3 |

Members who are credentialed and engaged but below both ideological thresholds are placed by nearest fit and flagged. The full definitions and decision sequence are in `rubric.md`; the final residual rule is in `scripts/score.py`.

## Result (all 320)

| Group | Total | Meet the test outright | Nearest fit |
|---|---|---|---|
| Ideological left | 116 (36%) | 68 | 48 |
| Inexperienced & base-dependent | 15 (5%) | 15 | 0 |
| Credentialed but disengaged | 86 (27%) | 6 | 80 |
| Clinton-style centrist | 103 (32%) | 42 | 61 |

- 186 of 320 members sit below both ideological thresholds. Read the "nearest fit" placements as tendencies, not verdicts.
- Newcomers who flipped Republican seats lean centrist (25 of 49). Newcomers in Democratic-held or new seats lean left (17 of 46).
- Left score minus centrist score correlates with DW-NOMINATE at r = 0.60 (House) and 0.64 (Senate) for sitting members.

## Evidence

- **Roster:** Wikipedia's 2026 House results and new-members pages, the unitedstates/congress-legislators list, and 270toWin's uncalled-race tracker.
- **Sitting members (225 plus the PR Resident Commissioner):**
  - Co-sponsorships from GovInfo bill-status files: Medicare for All, the Ultra-Millionaire Tax Act, Abolish/Melt ICE, the DC Admission Act, Block the Bombs, the Green New Deal, the 99.5% Act, and the Judiciary Act (2021, 2023).
  - Roll calls from Voteview: Laken Riley, the trans sports bill, the 2025 stopgaps, and the July 2026 amendment ending military aid to Israel.
  - Membership of the Progressive Caucus, New Democrats, Blue Dogs and Problem Solvers.
- **Everyone:** public statements, campaign platforms, endorsements, debate and media records, and FEC small-donor shares (bulk candidate summaries to 14 Oct 2026).
- **Research process:** parallel research passes collected cited evidence per member (`data/research/`). Scores are then computed centrally from the marker values (`scripts/score.py`), so every member goes through the same arithmetic.

## Limits

- Group 2 and 3 placements rest on proxies. Experience and policy depth are measured, not intelligence. Debate and press access are measured, and these also reflect campaign strategy.
- A shared web-search allowance ran out early, so debate and media records are often unverified. Unverified evidence scores neutral rather than as avoidance, which means group 3's core is probably under-counted.
- Newcomers have no voting record yet.
- Eight races were still uncalled at cut-off and are flagged `provisional` in `members.csv`.
- Individual entries can be wrong. Every scored position carries its source URL in `data/members.json`.
- The categories are analytical groupings defined by the brief. They are not characterisations of anyone's ability or motives.

## Files

- `report.html`: the interactive report (self-contained).
- `data/members.csv`: one row per member with group, fit, confidence, scores, small-donor share, DW-NOMINATE, caucuses, endorsements and rationale.
- `data/members.json`: full per-member evidence (markers with notes and sources, profile, debates and media, money).
- `data/research/`: raw research output per batch.
- `data/inputs/`: roster, bulk incumbent data, co-sponsor and caucus lists, analyst corrections, and page narrative.
- `rubric.md`, `agent_brief*.md`: the test and the research instructions.
- `scripts/`: the pipeline. `full_roster.py`, `incumbent_bulk.py`, `score.py`, `build.py` and `export.py` take the working directory as their first argument.
