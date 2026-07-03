# LARRY — Linguistic Articulation Representation for Real-time sYnthesis

*A modern notation for sign language production*

**Version 0.1.1 — Draft Specification** (incorporates first stress-test fixes; see §16 Changelog)
**Status:** Working draft for discussion
**File extension:** `.lry` · **MIME type (proposed):** `text/x-larry`
**Language profile in this document:** ASL (`asl.v1`), on a language-neutral core

> **Provenance and transparency.** This specification is being developed with AI assistance (Anthropic's Claude), directed and edited by the project's author, Dakota — a hearing CODA whose father is a late-deafened adult (deafened at 43, English-primary). Dakota grew up signing at home, but the home language was PSE (contact sign) rather than strict ASL. That background motivates and informs this project; it does not make either the author or the AI an authority on ASL grammar. Every linguistic claim in this document should be treated as a hypothesis pending review by fluent Deaf signers and ASL linguists (§14). The language is named for Dakota's father, Larry.

---

## 1. Motivation

HamNoSys (1985) and its XML encoding SiGML solved the problem of *describing signs phonetically* for avatar animation, but they predate three things that change the design space entirely: large language models that can author structured text, motion-capture corpora of fluent signers, and modern animation engines with layered rigs. HamNoSys fails as an interchange format today for concrete reasons:

- **Write-only for humans.** Dense special-symbol strings that require expert training to read and cannot be typed on a keyboard.
- **Poses, not motion.** It specifies articulator configurations and abstract movements, leaving motion *quality* (velocity profiles, coarticulation, tension) undefined — which is why HamNoSys-driven avatars look robotic.
- **No discourse layer.** Sign languages use space grammatically: entities are established at spatial loci and referenced later by pointing and verb directionality. HamNoSys describes one sign at a time and has no memory.
- **Non-manuals bolted on.** Facial grammar (brows, mouth, head) carries syntactic load in ASL — question marking, negation, adverbials — but HamNoSys treats it as an afterthought.
- **Not LLM-friendly.** An LLM can learn any syntax, but symbol-dense notations with no redundancy are maximally hostile to generation and to human review of the output.

LARRY is designed to be the *interface between a language model and a motion model*: authored or emitted by humans and LLMs, audited by Deaf linguists, and rendered by animation systems that learn motion quality from real signer data.

### 1.1 Design goals

1. **Human-readable and typeable.** Plain ASCII, meaningful keywords, comment support. A fluent signer with an hour of training should be able to read an `.lry` file aloud (in sign).
2. **Three layers, cleanly separated.** Discourse (who/where in space), lexical (which signs, with what grammatical inflection), phonetic (articulator-level detail). Most content lives at the lexical layer; the phonetic layer is an escape hatch, not a requirement.
3. **Simultaneity as a first-class citizen.** Parallel channels (each hand, face sub-channels, head, torso, gaze) with an explicit alignment model — a score, not a string.
4. **Motion-model friendly.** LARRY specifies *intent and constraints*; a learned renderer supplies motion quality. The spec defines a renderer contract stating exactly what is normative and what is renderer discretion.
5. **Stateful spatial grammar.** A referent registry makes loci, indexing, and verb agreement resolvable and checkable.
6. **ASL-first, extensible.** A language-neutral core grammar plus per-language *profiles* that define inventories (handshapes, mouth morphemes, non-manual bundles). This document ships the `asl.v1` profile.
7. **Checkable.** A file either parses or it doesn't; references either resolve or they don't. Tooling can lint a LARRY file the way a compiler lints code.
8. **Streamable.** A live interpreting pipeline emits LARRY clause-by-clause as speech arrives. Every construct closes within a bounded chunk, discourse state carries forward across chunks, and nothing requires unbounded lookahead (§4.4).

### 1.2 Non-goals

- LARRY is not a transcription system for linguistic fieldwork (SignWriting and ELAN tiers serve that better).
- LARRY does not specify rendering (rig topology, blend curves, mesh). It specifies the *signal* a renderer must realize.
- v0.1 does not attempt full International Sign or tactile signing coverage (see Roadmap).
- LARRY is not a step toward replacing human interpreters. The discernment, advocacy, and art of a good interpreter rest on semantic and social understanding this project does not expect machines to attain; the notation targets contexts where the alternative to a machine is no access at all.
- The notation is direction-neutral by design: recognition systems (vision → LARRY) are as much its intended consumers as production systems (LARRY → animation), though this document is written from the production side.

---

## 2. Conceptual Model

### 2.1 Three layers

| Layer | Answers | Typical author |
|---|---|---|
| **Discourse** | What entities exist, where they live in signing space, whose perspective is active | LLM translator |
| **Lexical** | Which signs, in what order, with what inflections and grammatical non-manual spans | LLM translator |
| **Phonetic** | Exact articulator specification for novel signs, classifier constructions, and overrides | Human expert / dictionary / specialist model |

A production system authors mostly at the discourse + lexical layers. The renderer resolves lexical tokens against a **sign dictionary** (mocap clips or phonetic definitions). The phonetic layer exists so that *anything a body can sign is expressible*, but 95% of authored content never touches it.

### 2.2 Channels

The signing body is modeled as parallel channels. At the lexical layer channels are implicit (a sign token drives all of them); they become explicit in `par` blocks and phonetic definitions.

| Channel | Sub-channels | Carries |
|---|---|---|
| `dh` | — | Dominant hand/arm |
| `ndh` | — | Non-dominant hand/arm |
| `face` | `brows`, `eyes`, `cheeks`, `nose`, `mouth` | Grammatical + affective facial signal |
| `gaze` | — | Eye gaze target |
| `head` | — | Nods, shakes, tilts, thrusts |
| `torso` | — | Leans, shifts (role shift) |
| `affect` | — | Global emotional coloring (renderer hint) |

Channel values compose by **priority layering** (§8.4): span-level non-manual bundles < token-level modifiers < explicit `par` channel statements.

### 2.3 Timing

LARRY time is measured in **beats** (`b`), not milliseconds. One lexical sign token = 1 beat by default. The document header sets tempo (`%tempo 1.6sps` = signs per second); the renderer maps beats to seconds and is free to vary actual sign durations naturalistically (a fingerspelled word is not 1 beat per letter — see §8). Beats make files tempo-independent and let prosodic structure (pauses, holds, stress) be stated relationally.

### 2.4 Signing space

Signing space is addressed two ways:

- **Named zones** on a 3×3×3 grid: `{contra|center|ipsi}-{low|mid|high}-{near|mid|far}`, e.g. `ipsi-mid-near`. `neutral` = `center-mid-near` (the default signing box).
- **Anatomical locations** from the active profile (e.g. `chin`, `temple`, `chest-center`, `ndh-palm`) for body-anchored signs.

Continuous coordinates `locus(x, y, z)` (meters, signer-local, x+ = ipsilateral, y+ = up, z+ = away from body) are available for phonetic precision. **Entities are bound to zones** in the referent registry and referenced by name thereafter — authors say `ix(mother)`, never `point at (0.3, 1.1, 0.4)`.

---

## 3. Syntax at a Glance

A complete, valid LARRY document:

```lry
%lry 0.1
%lang asl.v1
%tempo 1.6sps

# "My mother gave me a book yesterday."
@entities {
  mother          # discourse referents; loci bound at establishment
  book
}

YESTERDAY |
[topic] { poss(1p) MOTHER !est(mother @ ipsi-mid-near) } |
BOOK !est(book @ center-mid-near) |
GIVE :dir(mother -> 1p)
```

Reading guide: `%` lines are header pragmas. `#` starts a comment. `@entities` declares discourse referents. UPPERCASE tokens are lexical sign IDs. `[topic]{...}` wraps a span in the ASL topic-marking non-manual bundle (brows up, slight hold). `!est(...)` establishes a referent at a spatial zone. `:dir(a -> b)` inflects a directional verb from locus to locus. `|` is a minor prosodic boundary.

---

## 4. Document Structure

### 4.1 Header pragmas

```lry
%lry 0.1                  # required, first line: spec version
%lang asl.v1              # required: language profile
%tempo 1.6sps             # optional, default 1.5sps
%signer handed(right)     # optional: right|left, default right
%dict core, medical.v2    # optional: dictionary namespaces, in priority order
%register formal          # optional hint: formal|neutral|casual, default neutral
```

### 4.2 Entities and establishment

Entities need no pre-declaration: **`!est` declares and binds in one step, mid-utterance.** The first establishment *is* the declaration, and it can carry a semantic class:

```lry
[topic] { poss(1p) MOTHER !est(mother @ ipsi-mid-near) } |
CAR !est(car : vehicle @ contra-mid-near) ...
```

This is how a streaming translator introduces referents as they arrive in the source speech — exactly as a human interpreter sets up space on the fly.

The optional `@entities` block is a batch-document convenience for pre-binding loci and classes (useful for authored/edited content, where planning the spatial layout ahead improves clarity):

```lry
@entities {
  mother                      # locus assigned at first !est
  store  @ contra-mid-far     # locus may be pre-bound
  car : vehicle               # optional semantic class, aids classifier selection
}
```

Reserved referents (never declared): `1p` (signer), `2p` (addressee), `3p-any` (generic third person). Compound references are allowed wherever a reference is: `ix(1p+2p)` ("we-two"), `:dir(1p -> mother+sister)` (dual agreement; max three atoms). Entity names are lowercase identifiers. Re-establishing an entity (`!est` again) rebinds its locus — this is normal ASL discourse behavior. Referencing (`ix`, `poss`, `:dir`) an entity that has never been established remains an error, whether or not it was declared.

**`!est` is a registry write, nothing more.** It does not displace the sign it is attached to (displacement is `:loc(zone)`) and does not add a pointing gesture (that is a following `ix()`). The typical live pattern is sign-then-index: `fs"DENVER" !est(denver @ ipsi-mid-far) ix(denver)`.

**Zone collisions.** Establishing at a zone held by a live entity is legal and evicts the previous binding *only if* that entity has never been referenced since its establishment; evicting a referenced entity's locus is a lint error — rebind it explicitly instead. This makes streaming lint decidable with zero lookahead.

### 4.3 Body

The body is a sequence of **utterance items**: sign tokens, spans, prosodic boundaries, `par` blocks, role-shift blocks, and inline definitions. Whitespace and line breaks are insignificant except inside strings.

### 4.4 Streaming mode

LARRY is designed to be emitted incrementally by a live translation pipeline. A stream is one header followed by an unbounded sequence of **chunks**, where a chunk is any well-formed sequence of body items — typically one clause.

- **State persists across chunks.** The referent registry, buoy holds, role-shift depth, and tempo are stream-scoped, not chunk-scoped. Mid-utterance `!est` (§4.2) is the normal way entities enter a live discourse.
- **Chunks are the unit of validity and render.** A renderer may begin rendering a chunk the moment it closes and must never require the rest of the stream. Consequently `[span]`, `par`, and `rs` blocks must close within their chunk — LARRY deliberately has no sentence-spanning open constructs. In practice the translating LLM chunks at clause boundaries, which is where translation quality wants to segment anyway (matching the 2–5s lag of human interpreters).
- **Bounded lookahead.** Non-manual `anticipate` ramps (§8.3) need at most 0.25b of lookahead, always satisfied within the closed chunk. Anticipation is *regressive* (it reaches backward): when a span opens a chunk, the ramp clamps at the chunk boundary and is absorbed into the boundary pause — it never reaches into already-rendered material. Nothing in the language requires unbounded buffering.
- **Sustained role shift.** Quoted dialogue spans sentences. When consecutive chunks close and re-open `rs` with the same referent, the renderer MUST sustain the shift — no torso return between them; the chunk-final `}` is a validity boundary, not a performance instruction. An `rs` with a different referent is a full transition.
- **Late corrections.** Live ASR revises itself. `%%retract(n)` discards the last *n* chunks, and discourse state rolls back with them: `!est` bindings, buoy raises, and role-shift entries made in retracted chunks are undone, so re-translation replays against a consistent registry. If the chunks were already signed, the renderer performs a visible repair the way human interpreters do (brief hold, corrective `[neg]` headshake, re-sign, re-establishing any loci the correction needs) — never pretending the error didn't happen. Repair *style* is renderer discretion; registry rollback is normative.

---

## 5. The Lexical Layer

### 5.1 Sign tokens

```lry
HELLO                      # dictionary sign, citation form
WEEK :num(3)               # number incorporation → "three weeks"
LOOK-AT :asp(iter)         # iterative aspect → "look at repeatedly"
GIVE :dir(1p -> mother)    # directional verb agreement
SIT~fast                   # timing modifier
!WANT                      # prosodic stress (bigger, tenser)
```

A token is an UPPERCASE identifier (letters, digits, hyphens) resolved against the active dictionaries. Unknown tokens are a **lint error**; conforming renderers must fall back to fingerspelling and flag the event (§9.4).

**Inflection modifiers** (`:key(args)`, profile-defined, chainable):

| Modifier | Meaning | Example |
|---|---|---|
| `:dir(a -> b)` | Verb agreement path between loci/referents | `GIVE:dir(mother -> 1p)` |
| `:loc(zone)` | Displace sign to a locus (spatial inflection) | `HOUSE:loc(contra-mid-far)` |
| `:asp(x)` | Aspect: `iter`, `cont`, `habit`, `delayed`, `intense` | `WAIT:asp(cont)` |
| `:num(n)` | Numeral incorporation (1–9, sign-dependent) | `MONTH:num(2)` |
| `:dir(a -> each(x, y))` | Distributive/exhaustive agreement — verb sweeps each locus in order | `GIVE:dir(1p -> each(mother, sister))` |
| `:recip` | Reciprocal (both hands mirror the agreement path) | `LOOK-AT:recip` |
| `:size(s)` | Scalar size/intensity 0.25–4.0 | `BIG:size(2.0)` |

**Timing/prosody suffixes** (`~x`, core, chainable): `~fast`, `~slow`, `~hold(1.5b)`, `~tense`, `~lax`. Prefix `!` = stress. Chained modifiers and suffixes apply left to right; repeating the same key within one chain is a lint error.

### 5.2 Pointing, possessives, fingerspelling, numerals

```lry
ix(mother)          # index (point) at a bound referent
ix(2p)              # "you"
ix(1p+2p)           # dual: "we-two" (compound reference)
poss(1p)            # possessive handshape toward locus → "my"
hon(mother)         # honorific/open-hand reference (polite deixis)
fs"KAFKA"           # fingerspelling, letter-by-letter
fs"KAFKA"~lexical   # lexicalized fingerspelling (smoothed, fused)
num(1987)           # numeral system: profile realization (compound year)
num(4.50, unit: dollar)
num(25, unit: percent)
```

`ix`/`poss`/`hon` on an unbound entity is a lint error — establish first. Fingerspelling content is uppercase A–Z, digits, and `&`/`-`; the renderer applies profile fingerspelling rules (§10.6).

`num(value)` invokes the profile's **numeral grammar** (§10.7) — ASL numbers are morphology (decade forms, compound years, incorporating money/age forms), not digit-by-digit fingerspelling. `unit:` selects the incorporating realization. Lexical `:num(n)` incorporation (§5.1) remains the form for 1–9 on incorporating signs.

### 5.3 Non-manual spans

Spans wrap a sequence and layer a **non-manual bundle** (defined in the profile, §10.4) over its duration:

```lry
[ynq] { ix(2p) DEAF ix(2p) }          # yes/no question: brows up, head forward
[whq] { STORE WHERE }                  # wh-question: brows furrowed
[neg] { ix(1p) LIKE COFFEE }           # headshake spans the clause
[topic] { BOOK } ix(1p) READ FINISH    # topic marks only BOOK
[cond] { RAIN } [neg]{ GO PICNIC }     # "If it rains, (we) won't go..."
[mm] { DRIVE }                         # adverbial mouth morpheme: "drive along casually"
```

Spans nest; inner bundles win conflicts channel-by-channel (§8.4). Span keywords are profile-defined; `asl.v1` ships the grammatical bundles `ynq whq rhq neg topic cond` (§10.4) plus every mouth morpheme in §10.5 as an adverbial span keyword.

### 5.4 Role shift (constructed action/dialogue)

```lry
rs(daughter) {
  affect: annoyed
  [neg] { ix(1p) WANT GO SCHOOL }      # 1p inside rs = the daughter
}
```

`rs(entity)` shifts torso/gaze toward the entity's locus and re-maps `1p` to that entity for the block's duration. Nesting is allowed to depth 2 (deeper is legal ASL but rare; lint warns). `affect:` inside any block sets the affect channel for that scope. In streaming mode, back-to-back `rs` blocks with the same referent across a chunk boundary render as one sustained shift (§4.4).

### 5.5 Explicit parallelism: `par` blocks

When channels must be independently specified — classifier predicates, buoys, simultaneous constructions — use `par`:

```lry
# "The car wound its way up the hill."
par 3b {
  ndh: cl{ hs:open-B orient: palm(down) loc: contra-mid-near } ~hold   # hill (buoy)
  dh:  cl{ hs:3 orient: palm(contra)
           loc: contra-low-near
           mv: path(spiral, to: ipsi-high-far) speed(0.7) }
  face.mouth: morpheme(mm)
  gaze: follow(dh)
}
```

Rules: the block declares its duration (`3b`; default = longest child). Each statement is `channel: content`. Unlisted channels return to neutral/carryover. A channel statement may be a lexical token, a `cl{}`/`sign{}` phonetic block, a morpheme, a target (`gaze:`), or `~hold` to freeze the channel's current state. Offsets stagger children: `dh +0.5b: ...`.

**Buoys** are not expressed through `par` holds — they are first-class constructs (§5.7).

### 5.6 Prosodic boundaries

| Mark | Meaning | Default effect |
|---|---|---|
| (space) | Sign transition | Renderer coarticulates |
| `\|` | Minor boundary (phrase) | ~0.5b relaxation, non-manuals may reset |
| `\|\|` | Major boundary (sentence) | ~1b pause, hands may rest, non-manuals reset |
| `~hold(nb)` | Freeze final posture | Sign's end posture held n beats |

### 5.7 Buoys

A buoy raises the non-dominant hand as a persistent discourse landmark. It is **stream-scoped state**: it survives chunk and sentence boundaries until released.

```lry
buoy plans : LIST-3 {                # raise: NDH forms LIST-3 and holds
  !est(coffee @ finger(1))           # bind entities to buoy landmarks
  !est(tea    @ finger(2))
  !est(juice  @ finger(3))
}
ix(tea) GOOD | ix(coffee) [neg]{ WANT } ||
release(plans)                       # NDH returns to rest
```

Entities bound to `finger(n)` are referenced with ordinary `ix`/`:dir`, resolved to the physical fingertip of the live buoy — "the second one" is a point at the NDH index finger, exactly as signed. Rules: the buoy sign must be NDH-compatible (lint); a live buoy owns the `ndh` channel, so `par` statements addressing `ndh` are lint errors while one is up; raising costs 1b, `release` 0.5b; an unreleased buoy at stream end is auto-released with a lint warning; v0.1.1 allows one live buoy at a time. Fragment and pointer buoys are dictionary signs used the same way.

---

## 6. The Discourse Layer in Practice

The registry plus three operators carry ASL's spatial grammar:

```lry
!est(entity @ zone)     # bind entity to a zone (attach to any sign token)
ix(entity)              # point at its locus
:dir(a -> b)            # move a verb through agreement space
```

Worked mini-discourse — *"My brother lives in Denver. I visit him every month."*:

```lry
@entities { brother, denver : place }

[topic] { poss(1p) BROTHER !est(brother @ ipsi-mid-mid) } |
LIVE fs"DENVER" !est(denver @ ipsi-mid-far) ix(denver) ||
EVERY-MONTH ix(1p) VISIT :dir(1p -> brother)
```

The lint pass verifies: every `ix`/`dir`/`poss` target is established before use; zone eviction rules (§4.2) are respected; role-shift referents are bound. Because `!est` auto-declares, the linter additionally warns on entities established but never referenced and on near-duplicate entity names (edit distance 1) within a stream — the typo hazards auto-declaration introduces. This is the layer gloss fundamentally cannot express, and it is deliberately *checkable*.

---

## 7. The Phonetic Layer

The phonetic layer defines signs from articulatory primitives. It appears in three places: `def` statements (building dictionaries), inline `sign{}` blocks (novel one-off signs), and `cl{}` classifier blocks (productive constructions).

### 7.1 `sign{}` blocks and `def`

```lry
def HELLO sign {
  hands: dh
  hs: open-B
  orient: palm(fwd) fingers(up)
  loc: temple-ipsi contact(light)
  mv: straight(dir: ipsi+fwd) size(small) end(release)
}

def BOOK sign {
  hands: both sym(mirror)
  hs: open-B
  orient: palm(contact)            # palms facing each other, touching
  loc: center-mid-near
  mv: pivot(axis: pinky-edge, open: 120deg) end(hold)
}
```

Fields (all optional except `hs`, `loc`):

| Field | Content |
|---|---|
| `hands:` | `dh` (default), `ndh`, `both sym(mirror\|alt\|parallel)`, or `both free` (then `dh{}`/`ndh{}` sub-blocks) |
| `hs:` | Handshape from profile inventory (§10.1). Transitions: `5 > flat-O` (closing). Per-segment: `hs: 5 > flat-O @ mv.end` |
| `orient:` | `palm(dir)` + `fingers(dir)`. Directions: `up down fwd back ipsi contra` and combinations `ipsi+fwd`; `palm(contact)` for hand-to-hand |
| `loc:` | Anatomical location or zone; `contact(light\|firm\|brush\|none)`; path `chin -> chest` |
| `mv:` | One or more movement primitives (§7.2) with parameters |
| `nm:` | Sign-intrinsic non-manuals, e.g. `nm: mouth(morpheme: pah)` |

The **symmetry and dominance conditions** (Battison) are enforced as lint warnings: in `sym()` signs both hands share handshape; in two-handed asymmetric signs the NDH must use an unmarked handshape (`B, A, S, C, O, 1, 5`).

### 7.2 Movement primitives

Path movements: `straight(dir)`, `arc(dir, plane: v|h|mid)`, `circle(plane, cw|ccw)`, `zigzag(dir)`, `spiral(dir)`, `path(shape, to: zone)` (free path to target).
Local movements: `wiggle(fingers)`, `flick`, `open`, `close`, `twist(deg)`, `nod(wrist)`, `tap(n)`, `rub`, `shake`.
Parameters on any movement: `size(small|med|large|x.x)`, `speed(x.x)`, `repeat(n)`, `alt` (hands alternate), `end(hold|release|contact)`, `tension(lax|neutral|tense)`.

Path and local movements compose simultaneously (`mv: straight(fwd) + wiggle(fingers)` — e.g. SNOW). This inventory is deliberately small: it must cover *lexical* signs; free-form classifier motion uses `path()` with waypoints: `path(free, via: [center-mid-near, ipsi-mid-mid], to: ipsi-high-far)`.

### 7.3 Classifier blocks `cl{}`

Same fields as `sign{}` but the handshape is a **classifier morpheme** and semantics matter to the lint pass: if the entity's registry entry has a class (`car : vehicle`), tooling can check the classifier fits (`hs:3` = vehicle in `asl.v1`). `cl{}` blocks almost always live inside `par` and use free paths — this is the productive core of ASL that no fixed dictionary can hold, and the main reason the phonetic layer exists.

### 7.4 Non-manual primitives

Used in `nm:`, `par` face/head/torso channels, and profile bundle definitions:

```
brows(raise|furrow, 0..1)      eyes(wide|squint|closed|blink)
cheeks(puff|suck)              nose(wrinkle)
mouth(morpheme: id) | mouth(mouthing: "word") | mouth(viseme-track)
gaze(target|follow(ch)|addressee|averted)
head(nod|shake|tilt(dir)|thrust|pullback, amp, repeat)
torso(lean(dir)|shift(toward: locus), amp)
```

`mouth(mouthing:)` (silent articulation of a spoken word — common in ASL for proper nouns/emphasis) is distinct from `mouth(morpheme:)` (native adverbial morphemes). Conflating these is a classic avatar mistake; LARRY makes them different constructs. On the `face.mouth` channel, `morpheme(x)` is accepted shorthand for `mouth(morpheme: x)`.

---

## 8. Timing and Composition Semantics

### 8.1 Beat allocation

Default: 1 sign token = 1b; `ix`/`poss` = 0.5b; fingerspelling = 0.4b/letter (`~lexical` compresses to ~1.5b total); `num()` = 0.5b per numeral morpheme (profile-defined); buoy raise = 1b, `release` = 0.5b; `|` = +0.5b; `||` = +1b. Suffixes scale: `~fast` ×0.7, `~slow` ×1.5, `~hold(nb)` appends. These are *normative ratios*; absolute duration comes from `%tempo` and renderer prosody (§9.2).

### 8.2 Alignment in `par`

All children start at block start unless offset (`dh +0.5b:`). A child shorter than the block holds its final state; `~hold` makes that explicit. Block duration = declared or longest child.

### 8.3 Span timing

A non-manual bundle spans exactly its `{...}` contents including internal boundaries, with profile-defined onset/offset ramps (default 0.2b ramp-in, 0.15b ramp-out). ASL regressive spreading (e.g., negation headshake beginning slightly before the verb) is expressed by the bundle's `anticipate: 0.25b` property in the profile, not by the author. In streaming mode, anticipation clamps at chunk boundaries: if a span opens a chunk, the ramp is absorbed into the preceding boundary pause rather than reaching into rendered material.

### 8.4 Channel conflict resolution

When multiple sources drive one channel, priority (low→high):

1. Neutral/carryover state
2. Sign-intrinsic `nm:` from dictionary/phonetic definition
3. Span bundles (outer < inner)
4. Token modifiers (`:asp`, `~tense` — these may imply non-manuals, e.g. `asp(intense)` adds a tense mouth)
5. Explicit `par` channel statements

`affect:` is deliberately *not* on the ladder: it is a fill layer that colors only channels no rung currently owns, and therefore can never override grammatical signal (the brows of `[whq]`, the headshake of `[neg]`). Conflicts at the same rung are lint errors.

---

## 9. Renderer Contract

A conforming renderer:

**9.1 Must** realize every normative element: sign identity, order, span extents, agreement paths, established loci (±10cm), handshape/orientation/location/contact in phonetic blocks, channel priority (§8.4), and beat ratios (±20%).

**9.2 May** vary: velocity profiles, transitional (epenthetic) movement between signs, exact hold micro-timing, blinks at boundaries, weight shift, and all motion texture. Renderers are *encouraged* to learn these from fluent-signer mocap rather than interpolate naively — this is where signing stops looking robotic.

**9.3 Must coarticulate:** the transition between consecutive signs is renderer-synthesized (minimum-jerk or learned); the end posture of sign *n* must not simply snap to sign *n+1*. `end(hold)` suppresses anticipatory transition.

**9.4 Must fail loudly:** unknown lexical token → render as fingerspelling *and* emit a machine-readable warning event (never silently skip). Unresolvable reference → refuse to render the utterance (a wrong pronoun is worse than an error message, in an accessibility context).

**9.5 Pipeline note.** The reference architecture is: LLM emits LARRY → lint/resolve pass → per-channel target curves → learned motion model (trained on pose-extracted signer video, conditioned on LARRY features) → retarget to rig (e.g., MetaHuman control rig in Unreal). LARRY is the boundary where correctness is checked; naturalness lives downstream.

---

## 10. The `asl.v1` Profile

A profile supplies: handshape inventory, anatomical locations, non-manual bundles, mouth morphemes, span keywords, fingerspelling rules, and classifier classes. Excerpted here; the full profile is a separate machine-readable file.

### 10.1 Handshape inventory (52 shapes)

Fingerspelling bases: `A B C D E F G H I K L M N O P Q R S T U V W X Y Z` (as handshapes: `A…Z`).
Numerals: `1 2 3 4 5 6 7 8 9`.
Derived/marked: `open-A, open-B, bent-B, flat-B, open-8, bent-V, bent-3, claw-5, claw-3, flat-O, baby-O, small-C, flat-C, G-angle, horns, ILY, R-crossed, S-tense, 1-bent, 5-lax`.

Three numeral names are aliases of letter shapes — `2 = V`, `6 = W`, `9 = F` — giving 52 *distinct* shapes from the 55 names above. Dictionaries and renderers must key on the canonical letter form; the numeral spellings are accepted as input and normalized.

### 10.2 Anatomical locations

`head-top, forehead, temple-ipsi, brow, eye, nose, ear-ipsi, cheek, chin, mouth, neck, shoulder-ipsi, shoulder-contra, chest-center, chest-ipsi, chest-contra, abdomen, upper-arm-ndh, elbow-ndh, forearm-ndh, wrist-back-ndh, ndh-palm, ndh-back, hip-ipsi` — plus all 27 grid zones (§2.4).

### 10.3 Classifier classes

`vehicle: 3` · `person-upright: 1` · `person-by-legs: bent-V` · `flat-surface: open-B` · `cylindrical: C` · `small-round: F` · `mass/crowd: claw-5` · `thin-wire: I` — extendable per dictionary.

### 10.4 Non-manual bundles (span keywords)

| Keyword | Bundle (summary) | Anticipate |
|---|---|---|
| `ynq` | brows(raise, .8), head(thrust fwd, .4), eyes(wide, .3), hold last sign | 0.2b |
| `whq` | brows(furrow, .8), head(tilt fwd, .3), gaze(addressee) | 0.2b |
| `rhq` | brows(raise, .6), head(tilt side, .4) | 0.2b |
| `neg` | head(shake, amp .5, ~2Hz), brows(furrow, .3) | 0.25b |
| `topic` | brows(raise, .7), head(pullback, .3), +0.3b hold at close | 0.1b |
| `cond` | brows(raise, .7), head(tilt, .3); forces `\|` at close | 0.2b |

### 10.5 Mouth morphemes (usable as spans `[mm]{...}` or `mouth(morpheme: mm)`)

`mm` (with ease, regularly) · `cha` (large, tall) · `oo` (small, thin) · `th` (careless, sloppy) · `pah` (finally, success — punctual) · `pow` (impact) · `cs` (very recent) · `puff` (large quantity/mass) · `ps` (smooth, thin) · `intense` (clenched — very much so).

### 10.6 Fingerspelling rules

Ipsi-high-near placement, palm forward; letter transitions renderer-coarticulated; double letters = small lateral slide; `~lexical` items may be dictionary-overridden (e.g. `fs"BANK"~lexical` → the fused loan sign).

### 10.7 Numeral grammar (`num()`)

Realizes `num(value, unit:)` per ASL numeral morphology: cardinals 1–15 lexical; 16–19, decades, and hundreds as compound forms; years as paired compounds (`num(1987)` → 19+87); `unit: dollar | cent | percent | age | oclock` triggers the incorporating form (e.g., money counts with the palm-in twist, `age` from the chin). Ordinals 1st–9th are twist forms (`num(2, unit: ordinal)`). Any value the profile cannot realize natively falls back to digit fingerspelling **with a machine-readable warning** (§9.4) — silent degradation of numbers is forbidden; misheard numbers are the classic interpreting failure.

---

## 11. Worked Examples

### 11.1 Yes/no question — *"Are you deaf?"*

```lry
%lry 0.1
%lang asl.v1

[ynq] { ix(2p) DEAF ix(2p) }
```

Three tokens, one span. The renderer holds the final `ix(2p)` slightly (bundle property), brows stay raised throughout — a system driving raw gloss has no way to say any of this.

### 11.2 Conditional with negation — *"If it rains tomorrow, I'm not going."*

```lry
[cond] { TOMORROW RAIN } | [neg] { ix(1p) GO }
```

Note how the two grammatical facial signals never overlap; each span owns its clause. `neg`'s headshake anticipates onto `ix(1p)` by 0.25b per profile.

### 11.3 Spatial discourse + agreement — *"My mother gave me a book yesterday. I gave it to my sister."*

```lry
@entities { mother, sister, book }

YESTERDAY |
[topic] { poss(1p) MOTHER !est(mother @ ipsi-mid-near) } |
BOOK !est(book @ center-mid-near) GIVE :dir(mother -> 1p) ||
poss(1p) SISTER !est(sister @ contra-mid-near) |
GIVE :dir(1p -> sister)
```

`GIVE` never appears in citation form — both instances are spatially inflected, and the lint pass can verify the giving chain is referentially coherent.

### 11.4 Classifier predicate — *"The car wound slowly up the hill."*

```lry
@entities { car : vehicle, hill : flat-surface }

[topic] { HILL } [topic] { CAR } ||
par 3b {
  ndh: cl{ hs: open-B orient: palm(down) fingers(contra)
           loc: contra-mid-near } ~hold
  dh:  cl{ hs: 3 orient: palm(contra) fingers(fwd)
           loc: contra-low-near
           mv: path(spiral, to: ipsi-high-mid) speed(0.6) }
  face.mouth: morpheme(mm)
  gaze: follow(dh)
}
```

### 11.5 Role shift — *"My daughter said, 'I don't want to go to school!'"*

```lry
@entities { daughter }

[topic] { poss(1p) DAUGHTER !est(daughter @ ipsi-mid-near) } |
SAY ||
rs(daughter) {
  affect: exasperated
  [neg] { ix(1p) WANT !GO SCHOOL }
}
```

---

## 12. Comparison

| | Gloss | HamNoSys | SiGML | SignWriting | **LARRY** |
|---|---|---|---|---|---|
| Human-readable/typeable | ✓ / ✓ | ✗ / ✗ | ✗ / partial | ✓ / ✗ | ✓ / ✓ |
| Machine-parseable | ✗ (conventions vary) | ✓ | ✓ | partial | ✓ (EBNF) |
| Non-manual grammar | ad hoc overlines | bolted on | partial | ✓ | first-class spans + channels |
| Discourse space / agreement | ✗ | ✗ | ✗ | ✗ | referent registry, checkable |
| Motion semantics | ✗ | poses | poses | poses | intent + renderer contract |
| Classifier constructions | ✗ | phonetic only | phonetic only | ✓ (2D) | `cl{}` + semantic classes |
| Lexical/phonetic layering | lexical only | phonetic only | phonetic only | phonetic only | both, with dictionary fallback |
| LLM-authorable / lintable | poorly / ✗ | ✗ / ✗ | ✗ / partial | ✗ / ✗ | ✓ / ✓ |

---

## 13. Grammar (EBNF, abridged)

```ebnf
document    = header, [entities], { item } ;
              (* streaming: chunk boundaries are semantic, not syntactic — §4.4 *)
header      = "%lry", version, "%lang", profile, { pragma } ;
entities    = "@entities", "{", { entity }, "}" ;
entity      = ident, [":", class], ["@", zone] ;

item        = token | span | parblock | roleshift | buoy | release
            | boundary | definition | retract ;
token       = signref, { inflection }, { suffix } ;
signref     = ["!"], ( SIGNID | index | possessive | honorific
                     | fingerspell | numeral ) ;
index       = "ix", "(", ref, ")" ;
possessive  = "poss", "(", ref, ")" ;
honorific   = "hon", "(", ref, ")" ;
fingerspell = "fs", STRING, ["~lexical"] ;
numeral     = "num", "(", NUMBER, [",", "unit", ":", ident], ")" ;
inflection  = ":", key, [ "(", args, ")" ]
            | "!est", "(", ident, [":", class], "@", ( zone | fingerloc ), ")" ;
suffix      = "~", key, [ "(", args, ")" ] ;

buoy        = "buoy", ident, ":", SIGNID, "{", { buoybind }, "}" ;
buoybind    = "!est", "(", ident, "@", fingerloc, ")" ;
fingerloc   = "finger", "(", DIGIT, ")" ;
release     = "release", "(", ident, ")" ;
retract     = "%%retract", "(", INT, ")" ;

span        = "[", spankey, "]", "{", { item }, "}" ;
roleshift   = "rs", "(", ref, ")", "{", [affect], { item }, "}" ;
parblock    = "par", [duration], "{", { chanstmt }, "}" ;
chanstmt    = channel, [offset], ":", chanvalue, { suffix } ;
chanvalue   = token | clblock | signblock | nmprim | "follow", "(", channel, ")" ;

definition  = "def", SIGNID, signblock ;
signblock   = "sign", "{", { field }, "}" ;
clblock     = "cl", "{", { field }, "}" ;
field       = fieldkey, ":", fieldvalue ;

boundary    = "|" | "||" ;
ref         = refatom, { "+", refatom } ;      (* compound refs, max 3 atoms *)
refatom     = ident | "1p" | "2p" | "3p-any" ;
```

(Full grammar with lexical rules for `args`, `zone`, `duration`, directions, and field values ships as `lry-0.1.ebnf` alongside a reference parser. The `each(...)` distributive form appears inside `:dir` args, which are opaque at this level.)

### 13.1 Lexical rules (normative)

These resolve ambiguities a grammar alone cannot — each was discovered by implementing a parser, and each will silently fork implementations if left unstated:

1. **Pragmas are line-oriented.** `%` and `%%` pragmas terminate at end of line — the one exception to §4.3's "line breaks are insignificant."
2. **Digit-initial reserved lexemes.** `1p`, `2p`, `3p-any` must be matched before the number rule; a standard tokenizer otherwise lexes `1p` as `1` + `p`.
3. **The `!` rule.** `!` immediately followed by `est` and `(` is establishment; any other `!` is stress. Two tokens of lookahead suffice; `est` is not a legal sign ID (sign IDs are uppercase), so the grammar stays deterministic.
4. **Closed fieldkey set.** Phonetic-block fieldkeys are frozen per spec version (`hands hs orient loc mv nm`); a field's value list ends at the next `fieldkey :` or at `}`. Profiles may extend inventories and bundles but may **not** add fieldkeys — that would make field boundaries unparseable for older tools.

---

## 14. Roadmap and Open Issues

**v0.2 candidates:** JSON canonical AST as an interchange target (DSL compiles down; engines consume JSON); recognition-side conformance (what a vision system must and may emit when decoding signing into LARRY); multiple simultaneous buoys; ordinal/fractional coverage in the numeral grammar; profile mechanism for BSL/LSF to validate the core/profile split; a conformance test suite (LARRY files + reference pose renders).

**Known open problems:** (1) Motion-quality parameters — how much velocity/tension vocabulary belongs in the notation vs. the learned renderer is unresolved; v0.1 deliberately keeps it minimal. (2) Depicting signs beyond classifiers (full constructed action) currently bottoms out in `par` + free paths, which is expressive but verbose. (3) The affect channel is a hint, not a model — affective prosody in signing deserves better than one keyword. (4) Regional/generational lexical variation is punted to dictionary namespaces.

**Process note:** as stated up front, this spec is AI-drafted under the direction of a hearing PSE signer — it has not yet had Deaf collaborators, which is a defect, not a feature. Before v0.2, the notation needs review by fluent Deaf signers and ASL linguists — in particular the non-manual bundle definitions (§10.4), beat ratios (§8.1), and whether the span keywords carve ASL grammar at its joints. A notation for an accessibility technology inherits that technology's obligation: *nothing about us without us.*

---

## 15. References and Prior Art

Stokoe notation (1960) — first phonological analysis of ASL (handshape/location/movement). · Battison (1978) — symmetry & dominance conditions (§7.1 lint rules). · HamNoSys (Prillwitz et al., 1989) and SiGML/JASigning — the system LARRY replaces; its phonetic completeness remains the benchmark. · SignWriting (Sutton) — proof that 2D iconic notation can be fluently *read*. · ELAN annotation tiers — the parallel-channel timeline model. · Brentari's Prosodic Model — theoretical grounding for the movement/hold and simultaneity treatment. · Ham2Pose (2023) — evidence that notation→pose can be learned, which the renderer contract assumes. · Liddell (2003), *Grammar, Gesture, and Meaning in ASL* — spatial grammar, buoys, and depicting signs underlying §5.7, §6, and §7.3.

---

## 16. Changelog

**0.1.1** — Fixes from the first stress test (a prototype parser run over every spec example plus adversarial inputs, and a semantic probe of streaming and composition rules): `%%retract` now specifies normative registry rollback; buoys promoted to first-class constructs (`buoy` / `finger(n)` / `release`, §5.7) with addressable landmarks; `num()` numeral tokens added with profile numeral grammar (§10.7); sustained role shift defined across chunk boundaries; `!est` defined as registry-write only, with zone-eviction rules; anticipation ramps clamp at chunk boundaries; `affect:` removed from the priority ladder (§8.4); normative lexical rules added (§13.1); compound references (`1p+2p`) and `each()` distributive agreement; handshape aliasing stated (2=V, 6=W, 9=F); lint guards for auto-declaration typo hazards; chained-modifier semantics defined.

**0.1** — Initial draft.
