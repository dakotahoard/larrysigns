# LARRY

**Linguistic Articulation Representation for Real-time sYnthesis** — a modern, human-readable, streaming-friendly notation for sign language production. LARRY is the interface between a translating language model and an animation system: authored or emitted by humans and LLMs, checkable by machines, and meant to be audited by Deaf linguists.

Named for Larry, the project author's father. · **https://larrysigns.org**

> **Provenance and transparency.** This project is being developed with AI assistance (Anthropic's Claude), directed and edited by Dakota — a hearing CODA whose father is a late-deafened adult. The home language was PSE (contact sign), not strict ASL. That background motivates the project; it does not make anyone involved an authority on ASL grammar. **Every linguistic claim in this repository is a hypothesis awaiting review by fluent Deaf signers and ASL linguists.** Deaf collaborators are wanted at maintainer level, with authority over linguistic content — see [GOVERNANCE.md](GOVERNANCE.md).

## Why

HamNoSys/SiGML solved phonetic sign description in the 1980s–2000s but are write-only for humans, describe poses rather than motion, have no discourse layer (ASL's spatial grammar), and predate LLMs. Raw gloss loses the grammar entirely. LARRY is a three-layer notation — discourse (spatial referents), lexical (signs + inflections + non-manual spans), phonetic (articulator escape hatch) — with beat-based timing, a streaming chunk model for live interpretation, and a renderer contract separating what is normative from what a learned motion model supplies. See the [spec](spec/larry-spec-v0.1.1.md) §1 for the full argument and §12 for comparisons.

```lry
%lry 0.1
%lang asl.v1

# "My mother gave me a book yesterday."
YESTERDAY |
[topic] { poss(1p) MOTHER !est(mother @ ipsi-mid-near) } |
BOOK !est(book @ center-mid-near) GIVE :dir(mother -> 1p)
```

## Quick start

```sh
python3 tools/larry_parser_prototype.py     # parser self-test (spec examples + adversarial)
python3 tools/larry_lint.py                 # semantic linter self-test
python3 tools/larry_lint.py examples/live-stream-demo.lry   # lint a file
```

No dependencies beyond Python 3.9+.

## Repository layout

`spec/` — the language specification (normative). · `profiles/` — language profiles (`asl.v1` is embedded in the spec §10; `pse.v1` is the first external profile). · `tools/` — prototype parser and reference semantic linter. · `examples/` — valid `.lry` streams; CI lints every one. · `reports/` — adversarial stress-test and cold-authoring test reports; read these to see how the spec has been exercised and where its known weaknesses are.

## Status

v0.1.1 draft. Machine-validated (all spec examples parse; the linter enforces the discourse registry, buoy lifecycle, and streaming rules; a fresh LLM authored valid LARRY from the spec alone — see `reports/`). **Not yet reviewed by Deaf signers — the project's gating milestone for v0.2.** Roadmap: spec §14.

## What this project is — and is not

**LARRY is a notation project.** The bet behind it: the biggest missing piece between the signing community and modern language technology is not another model — it is a robust, shared representation that humans and machines can both read, write, check, and argue about, built for quick encoding and decoding. The notation is deliberately symmetric: production systems (text/speech → LARRY → animation) and recognition systems (vision → LARRY → text) are both intended consumers. We will likely build reference implementations of both directions, but they are downstream of the notation, not the core of it.

**What LARRY is not: an attempt to replace human interpreters.** The discernment, skill, advocacy, and art of a good terp — reading the room, catching the misunderstanding as it forms, interjecting when the doctor needs to slow down, carrying accountability in legal settings — rest on semantic and social understanding we are not confident machines will ever have, and pursuing it is not this project's goal. The target is the vast space where the alternative to a machine is not a human interpreter but *nothing*: no terp available, no captions, a whiteboard and a pen.

**Is it a mechanical terp, though?** Someday, for some narrow jobs — station announcements, kiosks, the 2am ER wait before the human interpreter arrives. Let's be clear about the bar we're chasing first: **sign better than a VRI cart on three bars of hospital Wi-Fi.** The bar is on the floor. We expect to trip over it several times anyway.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). **ASL is a first-class working language of this project** — issues, reviews, and maintainer sign-offs are welcome as signed video, and the translation burden is ours, not yours. Most valuable right now: linguistic review from fluent Deaf signers and ASL linguists; a rendered proof-of-concept (parser output → skeleton animation); a published core sign dictionary; a BSL profile to stress the core/profile split.

## License

Code (`tools/`) under [MIT](LICENSE). Specification, profiles, and documentation under [CC BY-SA 4.0](LICENSE-SPEC.md). (Verify license choices with counsel before relying on them.)
