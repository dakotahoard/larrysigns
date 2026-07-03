# LARRY Profile: `pse.v1` — Contact Sign (PSE)

**Status:** Exercise draft — written to stress-test LARRY's core/profile split, and because PSE is the home language of this project's author (and of many late-deafened adults and hearing family members). A PSE target is not a lesser goal than ASL: for a user like the author's father — deafened at 43, English-primary — an interpreter that signs in English word order with continuous mouthing is *more* legible than fluent ASL, not less. Verdict on the split at the end.

---

## 1. What PSE is, operationally

Pidgin Signed English / contact sign uses ASL's lexicon on English's spine: English word order, English mouthing throughout, sharply reduced use of grammatical space, few classifier predicates, and English function words either fingerspelled, signed, or dropped. It is a contact continuum, not a fixed grammar — this profile encodes the middle of that continuum and exposes a knob for where on it to sit.

## 2. Inheritance

`pse.v1` declares `inherits: asl.v1`. Unchanged: the full handshape inventory and aliasing (§10.1), anatomical locations (§10.2), fingerspelling rules (§10.6), the numeral grammar (§10.7), and the sign dictionaries (PSE draws on the same lexicon — namespace `core` resolves identically). The inheritance mechanism worked with zero core changes: a profile is a data file, and overriding a subset of it is just shadowing keys.

## 3. What `pse.v1` overrides

**Non-manual bundles (§10.4).** Same keyword set, attenuated realization — PSE signers question with English-like intonation-analogues rather than full ASL facial grammar:

| Keyword | asl.v1 | pse.v1 |
|---|---|---|
| `ynq` | brows(raise, .8), head thrust | brows(raise, .5); no hold on final sign |
| `whq` | brows(furrow, .8) | brows(furrow, .4) |
| `topic` | brows(raise, .7) + hold | **absent** — topicalization is not PSE syntax; lint error |
| `cond` | brows(raise, .7), forced boundary | realized as lexical IF + brows(raise, .3) |
| `neg` | headshake 2Hz | headshake, lower amplitude; NOT usually alone — expect lexical NOT |
| mouth morphemes | full §10.5 set | `mm`, `cha` only; others lint-warn (rare in contact sign) |

**Mouthing default.** PSE's defining feature: the mouth channel continuously mouths the English source. `pse.v1` sets `mouth: mouthing(auto)` as the profile default — every lexical token is accompanied by the mouthed English word it translates, unless overridden. This required a **new core hook** (see finding F1).

**Continuum knob.** `%register` (§4.1) is repurposed with profile-specific values: `%register english-strong | balanced | asl-lean`, controlling how aggressively the renderer drops function words and engages space. This overloading is legal but smells (finding F2).

**Discourse space.** `!est`/`ix`/`:dir` remain fully available — PSE signers do use loci, just less — but `pse.v1` lint *warns* (not errors) on classifier blocks and depth-2 role shift, which read as register breaks in strong-English PSE.

## 4. Sample

*"Are you coming to the party tomorrow?"* — same core syntax, different profile:

```lry
%lry 0.1
%lang pse.v1
%register english-strong

[ynq] { ix(2p) COME TO PARTY TOMORROW }   # English order; TO signed, not dropped
```

The asl.v1 rendering of the same sentence would be `[ynq] { TOMORROW PARTY ix(2p) COME ix(2p) }` — different token stream, identical notation machinery. That is the core/profile split doing its job.

## 5. Findings — where the split held and where it leaked

**Held.** Inventories, bundles, fingerspelling, numerals, dictionaries: all cleanly profile-shadowed. No syntax changes were needed for a typologically *different* signing system, which was the point of the exercise. Span keywords being profile-defined meant `[topic]` could simply cease to exist here.

**F1 (core change required): profiles need a `defaults` block.** asl.v1 never needed to set channel *defaults*, so the core had no mechanism for a profile to say "mouth channel = mouthing(auto) unless overridden." Proposed for v0.2: a `defaults { channel: value }` section in the profile format, sitting at priority rung 0.5 (above neutral, below everything authored). Without it, PSE's single most important property was inexpressible.

**F2 (design smell): `%register` is doing two jobs.** In the core it's a formality hint; pse.v1 overloads it as a continuum position. These are genuinely different axes (one can sign formal english-strong PSE and casual asl-lean PSE). Proposed for v0.2: profiles may declare their own pragmas (`%continuum english-strong`), namespaced to the profile.

**F3 (open question): lint severity is profile-relative.** `[topic]` is an error in pse.v1 but core lint machinery had no notion of per-profile severity until this exercise; the linter needs its span/feature tables loaded *from* the profile rather than hard-coded. (The reference linter currently hard-codes asl.v1 — known limitation, flagged in its docstring.)

**F4 (validation): nothing in PSE needed new *syntax*.** The strongest evidence for the design: a second profile at a very different point in typological space required zero grammar productions. BSL remains the harder test (two-handed fingerspelling will stress §10.6's assumptions) and should be the next profile exercise.
