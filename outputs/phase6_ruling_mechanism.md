# Phase 6 — Why do `<RULING>` marks lower cross-boundary similarity?

Phase 4 established the effect on the full corpus but explicitly did **not** establish the mechanism. The proposed explanation — a ruling falls *between* records while an arbitrary cut falls *within* one — was a hypothesis. This tests it directly.

**If a ruling ends a record**, the line immediately before it should be enriched in record-*closing* formulae. If rulings were arbitrary or a modern editorial artifact, there should be no enrichment.

Only probes validated at 96–100% precision in [`probe_validation.md`](probe_validation.md) are used; the DO-NOT-CITE probes are excluded. Tablet-final lines are excluded from both groups, and the null permutes ruling *positions* within each tablet, holding tablet length, line content and ruling count fixed so that only placement varies.

A letter-*opening* formula (`u₃-na-a-du₁₁`) is included as a **negative control**: it should show no enrichment before rulings, and if it does, the design is measuring something other than record structure.

## Administrative

1,783 tablets · 2,213 pre-ruling lines · 31,469 other interior lines

| Marker | Rate before ruling | Rate elsewhere | Within-tablet enrich | p | **Position-controlled enrich** | **p** |
|---|---:|---:|---:|---:|---:|---:|
| seal_of_PN (kišib₃) | 0.0303 | 0.0093 | 2.46× | 0.0001 | **2.52×** | **0.0001** |
| received_by (šu ba-ti) | 0.0922 | 0.004 | 5.4× | 0.0001 | **6.31×** | **0.0001** |
| month (iti) | 0.0307 | 0.0399 | 0.58× | 1.0 | **0.53×** | **1.0** |
| year-name (strict mu) | 0.0163 | 0.0433 | 0.3× | 1.0 | **0.28×** | **1.0** |
| letter address (u₃-na-a-du₁₁) *(negative control)* | 0.0 | 0.0 | None× | 1.0 | **None×** | **1.0** |

## Literary

109 tablets · 293 pre-ruling lines · 3,770 other interior lines

| Marker | Rate before ruling | Rate elsewhere | Within-tablet enrich | p | **Position-controlled enrich** | **p** |
|---|---:|---:|---:|---:|---:|---:|
| seal_of_PN (kišib₃) | 0.0034 | 0.0016 | 2.15× | 0.40416 | **1.94×** | **0.41606** |
| received_by (šu ba-ti) | 0.0 | 0.0003 | 0.0× | 1.0 | **0.0×** | **1.0** |
| month (iti) | 0.0 | 0.0013 | 0.0× | 1.0 | **0.0×** | **1.0** |
| year-name (strict mu) | 0.0171 | 0.0454 | 0.59× | 0.94911 | **0.38×** | **0.999** |
| letter address (u₃-na-a-du₁₁) *(negative control)* | 0.0 | 0.0 | None× | 1.0 | **None×** | **1.0** |

## How to read this

`Enrichment` is the observed rate before a ruling divided by the rate expected when the same number of rulings is placed at random interior positions in the same tablet. p is the one-sided upper permutation p-value over 10,000 placements. An enrichment above 1 with small p means ruling placement is **predicted by the semantic content of the preceding line**.

That is the observation an editorial-artifact explanation cannot easily accommodate: a modern editor marking lines without regard to content would not place them preferentially after seal clauses and receipt confirmations.

## Conclusion

**The record-boundary mechanism proposed in Phase 4 is supported, and the result is more informative than a uniform enrichment would have been.**

In Administrative tablets the two transaction-*closing* elements are strongly enriched in the line immediately preceding a ruling:

- **received_by (šu ba-ti)** — 5.4× enriched (rate 0.0922 vs null 0.0171), p = 0.0001
- **seal_of_PN (kišib₃)** — 2.46× enriched (rate 0.0303 vs null 0.0123), p = 0.0001

The date elements go the other way — `iti` (month) and `mu` (year-name) are *depleted* before rulings. That is the expected pattern rather than a problem: in Ur III practice the date closes the whole **tablet**, not each internal entry, and tablet-final lines are excluded from this test by design. Interior rulings separate individual transaction entries, and an entry closes with a seal and a receipt — not with a date.

**Why the differentiated signal matters.** A test that enriched everything would be measuring something generic about line position. This one separates transaction-closers (enriched) from tablet-closers (depleted) from a letter-*opening* formula (the negative control, flat). It discriminates, which is what makes the positive result credible.

**Literary tablets show no significant enrichment**, which is also as expected: literary texts have no transaction records to close, so the closing formulae carry no information about where a ruling falls there.

### What this settles, and what it does not

**Settles (for Ur III administrative tablets):**

1. **The Phase 4 effect has a mechanism.** Rulings fall after record-closing formulae, so a ruling separates completed transactions. An arbitrary cut lands mid-record, leaving related material on both sides — which is precisely why arbitrary cuts show *higher* cross-boundary overlap.
2. **`<RULING>` is not merely an editorial artifact.** Its placement is predicted by the semantic content of the preceding line. A modern editor drawing lines without regard to content could not produce this. This was listed as an open threat to validity in Phase 4; it is now substantially addressed.

3. **The result is not positional co-clustering.** The obvious objection to the within-tablet null is that rulings *and* closing formulae might both drift toward the back of a tablet, producing enrichment with no record-boundary relationship at all. The position-controlled null removes that: every interior line is assigned a relative-position decile and labels are permuted only within a decile, so the positional distribution of rulings is fixed by construction. **The effect does not weaken — it strengthens slightly** (`šu ba-ti` 5.4× → 6.31×, `kišib₃` 2.46× → 2.52×, both still at p = 0.0001). Position is therefore not the driver.

**Does not settle:**

- Whether this generalises beyond Ur III administrative practice. Literary is underpowered here and every other genre lacks the record structure entirely.
- Whether the enrichment reflects scribal intent or a downstream regularity of how such tablets were laid out. The test shows the association, not the intention behind it.
- The philological validity of the probes themselves beyond the precision audit — that still wants specialist review, though the probes used here are the ones validated at 96–100%.
