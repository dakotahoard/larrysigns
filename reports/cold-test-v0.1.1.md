# LARRY v0.1.1 — Cold-Authoring Test Report

**Setup:** A fresh LLM session (no prior exposure to LARRY, no conversation context) was given only `larry-spec-v0.1.1.md` and five English utterances of graded difficulty, instructed to author a single live-interpreting stream in ASL grammar. Its output (`cold_test_output.lry`) was then validated mechanically with the reference parser and semantic linter.

**Result: PASS.** The 60-line stream parses cleanly and produces **zero lint findings** — no unestablished references, no zone conflicts, correct buoy lifecycle (raise → bind → reference → release), valid span keywords, no modifier violations. This was the production job description — LLM emits LARRY, machine checks it — and it worked on the first attempt.

## What the cold author got right

It independently reproduced the intended idioms: streaming mode with no `@entities` block and mid-utterance `!est`; chunk-per-clause segmentation; time-first and topic-comment ordering; sign-then-index referent introduction (`WOMAN fs"MARIA" !est(maria @ ...) ix(maria)`); locus-to-locus verb agreement (`GIVE :dir(brother -> sister)`, `LOOK-AT :dir(maria -> 1p)`); the money numeral (`num(20, unit: dollar)`); role shift with affect for quoted speech; dual pronoun `ix(1p+2p)` for "we"; and — the hardest test — a fully correct LIST-3 buoy with fingertip bindings, where "the second one" is expressed as `ix(tea)` resolving to a physical finger point. It also invented reasonable solutions where the spec is silent (superlative as stress + MOST).

## What the test revealed (the author's own gap report, confirmed)

1. **No lexeme↔entity association.** `COFFEE ix(coffee)` works by human inference; nothing formally ties the sign COFFEE to the entity `coffee`, so a linter can't verify the pairing. *v0.2 candidate: optional `!est(coffee = COFFEE @ ...)` lexeme binding.*
2. **Quote attribution is positional.** `SAY ||` followed by `rs(maria)` associates speaker and quote only by adjacency; multi-speaker dialogue will strain it.
3. **`[cond]` "forces `|`" is ambiguous** — must the author still write it, and does writing it double-count the pause? (Worked example writes it; spec should say the explicit `|` is absorbed, not additive.)
4. **No person-introduction idiom.** The spec demonstrates introducing places, not people; the author composed `WOMAN fs"NAME"`, which is plausible ASL but unguided.
5. **Unknown-token risk is invisible without a dictionary.** MOST, CHOICE, etc. are trusted to exist in `core`; the fallback (§9.4) handles it at render time, but authors can't check. *A published core dictionary list is now the biggest missing artifact.*
6. **Chunk boundaries are comments.** Nothing normative marks them in the file format — fine for live pipes (the transport frames chunks), awkward for stored streams. *v0.2: optional `%%chunk` marker.*

## Caveats

One trial, one model, sentences within the spec's demonstrated range — this is a smoke test, not an evaluation. Mechanical validity ≠ good ASL: the output's grammar choices mirror the spec's worked examples, which encode the author's and the AI's hypotheses about ASL (see spec provenance note). Whether `[pah]{ ix(1p) !FINISH }` is how a Deaf signer would render "I already finished!" is exactly the kind of question that needs fluent Deaf review. What the test *does* establish: the notation is learnable from its spec alone, and the check pipeline catches the error classes it was designed to catch.

## Artifacts

`cold_test_output.lry` (the stream) · `larry_parser_prototype.py` (syntax) · `larry_lint.py` (semantics, 15/15 self-tests) · validation: `python3 larry_lint.py cold_test_output.lry` → exit 0, no findings.
