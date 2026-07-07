# Changelog

## 0.1.2
Completes the phonetic layer's two-handed and compound machinery, prompted by drafting the first 100-entry core dictionary (`dictionary/core-draft.lry`): `hands: both free` fully specified with `dh{}`/`ndh{}` sub-blocks, default-hold for base hands, and a global direction frame (§7.1.1); sequential `seg{}` segments for lexicalized compounds with 1-beat compound-reduction timing (§7.1.2, §8.1); `compound(...)` ancestry annotation as non-normative metadata (§7.1.3); EBNF extended (§13); lexical rule 4 amended and rule 5 added — digit-initial handshape names `1-bent`/`5-lax`, plus line-oriented pragma lexing per rule 1, both found and fixed in the prototype parser (§13.1).

Also: `tools/dict_editor.html` — a browser GUI for dictionary entries (form-driven defs, spec-cited validation, sub-block/raw editing); `dictionary/` added to CI lint; `spec/larry-spec-latest.md` always mirrors the newest version (CI-enforced).

## 0.1.1
Fixes from the first stress test (prototype parser over every spec example plus adversarial inputs; semantic probe of streaming and composition rules): normative `%%retract` registry rollback; first-class buoys (`buoy` / `finger(n)` / `release`) with addressable landmarks; `num()` numeral tokens + profile numeral grammar; sustained role shift across chunks; `!est` defined as registry-write only, with zone-eviction rules; anticipation ramps clamp at chunk boundaries; `affect:` removed from the priority ladder; normative lexical rules (§13.1); compound references and `each()` distributive agreement; handshape aliasing stated (2=V, 6=W, 9=F); auto-declaration lint guards; chained-modifier semantics.

Also: reference semantic linter added (15 self-tests); `pse.v1` profile exercise (findings F1–F4); cold-authoring test passed (see `reports/`).

## 0.1
Initial draft: three-layer model, channels, beat timing, signing-space grid, streaming mode, lexical layer (tokens, inflections, spans, role shift, `par`), phonetic layer (`sign{}`/`cl{}`), renderer contract, `asl.v1` profile, worked examples, abridged EBNF.
