# Contributing

Thanks for your interest — this project needs collaborators, especially fluent Deaf signers and ASL/BSL linguists (see GOVERNANCE.md for the linguistic-maintainer role; these seats come with real authority, not advisory status).

## Ways to contribute

- **Linguistic review** (most needed): open issues against the spec's grammatical claims — §10.4 non-manual bundles, §8.1 beat ratios, worked examples, the PSE profile. "A native signer would not do X, they'd do Y, here's video" is the most valuable issue this repo can receive.
- **Spec changes:** follow the RFC-lite process in GOVERNANCE.md. Every spec PR needs: the spec edit, an executable example, a changelog entry, and green CI.
- **Tooling:** the parser is a prototype (see its DISAMBIG comments); a proper implementation, editor tooling (syntax highlighting, LSP), and a renderer proof-of-concept are all open.
- **Examples:** real utterances that stress the notation. Failing examples are as welcome as passing ones — file them as issues with what you expected.

## Language access

You do not need fluent written English to contribute here — ASL is a first-class working language of this project:

- **Issues and reviews as signed video.** Open an issue with a link to a signed video (any host, unlisted is fine). A maintainer will add a written transcription to the issue, credited to you, and you can correct it. The video, not the transcription, is the authoritative version of your feedback.
- **Sign-off in ASL.** Linguistic-maintainer approvals may be signed video statements (see GOVERNANCE.md) with the same force as written approval.
- **Discussion in ASL.** RFC discussions can be held as video calls in ASL, with written summaries posted afterward.
- **Plain-language docs.** Key documents (README, this file, governance) should stay in plain, direct English; jargon-dense prose is a bug — file issues against it. Signed-video summaries of the spec are a wanted contribution.
- The translation burden is the project's, never the contributor's.

## Mechanics

- Run `python3 tools/larry_parser_prototype.py && python3 tools/larry_lint.py` before pushing; CI runs the same plus lints every file in `examples/`.
- Python: stdlib only for the reference tools.
- Disclose AI assistance in PR descriptions.
- Be kind. Discussions about a language community's language, led in part by outsiders, demand extra care and humility from everyone — most of all from the maintainers.
