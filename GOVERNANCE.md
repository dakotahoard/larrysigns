# Governance

## Principles

1. **Nothing about us without us.** LARRY is a notation for Deaf languages. Linguistic authority over the specification belongs with fluent Deaf signers and sign-language linguists, not with the project founder or with AI tooling.
2. **Transparency.** AI assistance in drafting is disclosed in the spec and README, and applies to future contributions too: PRs containing AI-drafted content must say so.
3. **The spec is falsifiable.** Changes come with executable examples; claims come with tests or citations.
4. **English is not a prerequisite.** For many Deaf signers, ASL is a first language and written English a second. This project exists because English-first channels fail Deaf users; its governance must not repeat that failure. Contributions, reviews, and binding sign-offs are equally valid delivered in ASL as signed video. The burden of translation between video and written text falls on the project (founder/maintainers), never on the Deaf contributor.

## Roles

- **Founder/maintainer (Dakota):** project direction, tooling, releases.
- **Linguistic maintainers (open seats — Deaf signers / ASL linguists):** binding review on any change to grammatical content — non-manual bundles, span semantics, beat ratios, profile inventories, worked examples. Until at least two linguistic maintainers have joined, all linguistic content is explicitly marked *unreviewed hypothesis* and v0.2 does not ship.
- **Contributors:** anyone, via issues and PRs.

## Spec change process (RFC-lite)

1. Open an issue describing the problem (not the solution) with a motivating utterance LARRY currently can't express or expresses wrongly.
2. Discussion → a PR that changes the spec **and** adds at least one example that parses and lints, plus a changelog entry.
3. Grammar/syntax changes require the parser and linter updated in the same PR; CI must stay green.
4. Linguistic-content changes additionally require sign-off from a linguistic maintainer. Sign-off may be a signed video statement linked from the PR — it carries identical weight to written approval.
5. RFC discussion may happen in ASL video calls; a maintainer posts a written summary afterward for the record, reviewed by the participants.
6. Versioning: patch = clarifications; minor = additive syntax; major = breaking. Renderers declare the version they conform to.
