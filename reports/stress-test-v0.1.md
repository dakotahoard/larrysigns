# LARRY v0.1 — Stress-Test Report

**Method:** (1) Implemented a prototype tokenizer + recursive-descent parser directly from the §13 EBNF (`larry_parser_prototype.py`) and ran all 14 code examples from the spec plus 6 adversarial inputs through it. (2) Attempted to encode hard ASL phenomena the spec doesn't showcase. (3) Probed the streaming semantics and channel-composition rules for internal contradictions.

**Headline:** All 14 spec examples parse. The core design holds up. But the parser needed four disambiguation rules the EBNF doesn't state, two adversarial inputs exposed genuine grammar holes, and the streaming section has three semantic gaps that will bite a real pipeline. Nothing is fatal; most fixes are small.

---

## Severity 1 — Will break a real implementation

**1.1 `%%retract` doesn't say what happens to discourse state.** If a retracted chunk contained `!est(mother @ ...)`, is the registry rolled back? If yes, the renderer's already-signed pointing gestures dangle; if no, the re-translation may re-establish at a colliding zone. The spec defines the pragma and punts everything else. *Fix: retract must specify registry rollback semantics — suggest: registry rolls back with the chunks; a repair re-establishes on screen, which matches how human interpreters fix a wrong locus.*

**1.2 Buoys are half-specified.** §5.5 says a buoy's `ndh` "outlives the block" and shows `~hold(until: release)` … `buoy-release`, but `buoy-release` appears in no grammar production (adversarial parse: **FAIL**, as expected), has no beat cost, and there's no way to *address* the buoy — ASL's core use of a list buoy is pointing at its fingers ("the second one…"), and `ix()` can only target zone-bound entities, not `ndh.finger(2)`. *Fix: promote buoys to a first-class construct with establishment (`!est(x @ ndh.finger(n))` or a dedicated `buoy` item), reference, and release in the grammar. Already flagged in §14 roadmap, but it's a bigger hole than "syntax hardening" implies.*

**1.3 No numeral system.** `:num(1–9)` incorporation is all LARRY has. "In 1987," "$4.50," "twenty-five percent," phone numbers — a live interpreter of news, meetings, or medical instructions is drowning in numbers, and ASL numerals are their own morphology (compounds, decade forms, money/age incorporation), not fingerspelling. Adversarial `num(1987)` parse: **FAIL** (correctly — there's nothing to parse it into). *Fix: add a `num(...)` token type whose realization rules live in the profile, parallel to `fs"..."`.*

**1.4 Multi-sentence role shift contradicts streaming.** Quoted dialogue routinely spans many sentences, but §4.4 requires `rs` blocks to close within a chunk. Re-opening `rs(daughter)` each chunk is expressible but semantically wrong: the renderer would visibly re-engage the shift (torso return + re-shift) at every chunk boundary, which reads as the quote ending and restarting. *Fix: define that consecutive chunks re-opening `rs` with the same referent MUST render as a sustained shift (continuation), or add `rs-cont`.*

## Severity 2 — Spec is ambiguous; implementations will diverge

**2.1 The EBNF underdetermines the parser.** Four rules had to be invented to make the spec's own examples parse; all four belong in the spec's lexical rules:

- `!` is both stress prefix and the start of `!est(` — resolvable only by two-token lookahead (`!` + `est` + `(`), and `MOTHER !EST` vs a hypothetical sign `EST` is only safe because `est` is lowercase. Should be stated, or the syntax changed (e.g. `+est(...)`).
- `1p`, `2p`, `3p-any` are digit-initial identifiers that collide with the number rule (`1p` lexes as `1` + `p` under any standard tokenizer).
- Phonetic-block field boundaries are undecidable without a closed fieldkey set: in `loc: temple-ipsi contact(light) mv: ...`, nothing but the known set {hands, hs, orient, loc, mv, nm} says `contact(light)` belongs to `loc` while `mv` starts a new field. Profiles that add fieldkeys will break parsers. Should be: newline/comma-terminated fields, or fieldkeys frozen per spec version.
- Header pragmas have no terminator; `%dict core, medical.v2` followed by other content is ambiguous. "Whitespace is insignificant" (§4.3) is contradicted in practice — pragmas are line-oriented. Say so.

**2.2 `!est` zone vs. sign placement.** §6 has `fs"DENVER" !est(denver @ ipsi-mid-far)` — but fingerspelling is produced at its own fixed location (§10.6, ipsi-high-near). Which wins? Real ASL typically signs the name *then* points/gazes to assign the locus. The spec never says whether `!est` displaces the sign, adds a post-hoc index, or merely writes the registry silently. All three produce visibly different signing. *Fix: define `!est` as registry-write only, with an explicit note that displacement requires `:loc()` and overt indexing requires a following `ix()`.*

**2.3 Non-manual `anticipate` at chunk starts.** §8.3's regressive spreading reaches *backwards* onto material before the span; if the span opens a chunk, that material is in the previous, possibly already-rendered chunk. §4.4's "lookahead satisfied within the chunk" claim is about the wrong direction. *Fix: one sentence — ramps clamp at chunk boundaries and are absorbed into the boundary pause.*

**2.4 Priority rule 6 is self-contradicting as written.** §8.4 lists `affect:` as highest priority (6) then immediately says it "never overrides grammatical brows." So it's not priority 6 — it's a floor-filler that applies only to unowned channels. The prose is understandable; the numbering will mislead an implementer. *Fix: pull affect out of the numbered ladder.*

**2.5 Auto-declaration removed a safety check.** Making `!est` declare-on-first-use (needed for streaming) means a *typo'd second establishment* (`!est(mothre @ ...)`) silently creates a new entity instead of erroring. The original `@entities` declaration requirement caught this. *Fix: lint warnings for (a) entities established but never referenced, (b) near-duplicate entity names in one stream.*

**2.6 Zone collisions under streaming.** The lint rule "two entities never share a live zone" assumes planning, but a streaming translator allocates loci greedily with 27 zones and no lookahead. Who resolves collisions — the LLM, the linter, or the renderer? *Fix: define rebinding-on-collision as legal with a defined eviction rule (oldest unreferenced locus is reassignable), so streaming lint is decidable.*

## Severity 3 — Gaps and nits

**3.1 Missing pronoun morphology.** No dual/plural incorporation (`WE-TWO`, sweeping plural `ix`), fine as lexical items but agreement (`:dir(1p+2p -> x)`) can't express "give to you-two." Add plural/dual ref syntax or declare it dictionary territory.

**3.2 Missing aspect values.** No distributive/exhaustive (`GIVE` to each of several established loci — a signature ASL inflection that sweeps agreement across loci). `:asp(dist)` over a locus list would be natural and shows off the registry.

**3.3 Chained aspect is unparsed but undefined.** `WAIT:asp(cont):asp(intense)` parses (grammar allows modifier chains) but composition semantics are unstated. Either define stacking order or lint-error duplicates.

**3.4 Handshape count is right for the wrong reason.** §10.1 claims 52 shapes but lists 26 + 9 + 20 = 55 names. It's 52 only if `2=V`, `6=W`, `9=F` are deduplicated — true in ASL, never stated. State the aliasing (it matters: a dictionary keyed by handshape needs canonical names).

**3.5 `%%retract` and `buoy-release` are absent from §13.** Whatever their final form, the grammar must include them.

**3.6 `hon()` was missing from the EBNF until this pass** (fixed earlier); double-check future constructs land in §13 — three of the four grammar holes found were "prose introduced syntax the EBNF never learned."

## What held up well

The three-layer split survived every encoding attempt — nothing forced phonetic detail into lexical-layer content. The referent registry handled comparatives (contrastive left/right space), timeline placement, alternating dialogue shifts, and the give-chain example with no extensions. `par` + `cl{}` expressed simultaneous constructions including gaze-only reference (verbose, but expressible — consistent with §14's known issue #2). Beat math is coherent at real tempos (fs"DENVER" ≈ 1.5 s at 1.6 sps, matching observed fingerspelling rates). And the chunk model's clause-boundary segmentation matches where the translating LLM needs to commit anyway; nothing in the language requires unbounded buffering, exactly as claimed — the failures found (1.4, 2.3) are at chunk *edges*, not in the model itself.

## Recommended order of attack for v0.1.1

Numerals (1.3) and buoy addressing (1.2) are expressiveness holes an MVP interpreter hits in the first minute of real input. Retract semantics (1.1) and rs continuation (1.4) matter as soon as the pipeline is live. Everything in Severity 2 is a paragraph each. Severity 3 can ride to v0.2 — except 3.4, which is one sentence.
