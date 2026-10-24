# CPU-only selected-read paired protocol amendment v2

This version supersedes only the prospective CPU-preparation amendment v1. The historical `PAIRED_PROTOCOL_V1.md` remains unchanged. This amendment covers Linux CPU preparation only; it makes no GPU, cross-card, or inference claim.

## Fixed experiment

Use the v5 fail-closed source and exact `libutils.so` SHA-256 `e4287923b8468a157eba6895d82c17a2f00105eeda32a6c9ec6755673b52231d`. The source patch is `selected-read-cpu-final-v5.patch` (SHA-256 `3a0f02fb0cb74e4ed0486e3c94a3ca6fea9a4d30cdca0985ae08c3409a6270fb`). The preserved v5 build/CTest record reports all 35 cases passing; its successful postcheck verifies the saved build log, library, reports, and pins without rebuilding or rerunning tests. Separately, production-caller qualification v2 completed one fixed crop with `PRODUCTION_OPTIN_INTEGRATION_EXACT`, exact equality of the 55-entry output tree, and a clean ledger (43 events, 43 unique chunks). These are correctness/provenance gates, not timing results.

Use the frozen representative manifest SHA-256 `56dd6c8cd71f17858fe8c7e8a7da9e7469ee23453096c4d47c4560268746d974` and the two representatives, in this order in every arm: `[27,180,1060]` (`broad1218-first`) and `[27,180,4640]` (`geometry-selected-largest`). Perform three pairs in order AB, BA, AB, where A is unchanged stock whole-CT verification and B is v5 verified-read. Do not substitute crops, inputs, precision, or build between arms.

For B, set the complete verified-read opt-in tuple and point the loader path at the pinned v5 candidate library directory. For A, remove every inherited `VC_VERIFIED_*` variable. Before any timed arm, run the dedicated linker-resolution preflight with the exact renderer binary and candidate environment. It must prove that the ELF loader resolves `libutils.so` to the canonical pinned v5 path and that the resolved file hash matches the pin. Record that proof outside arm timing. The candidate arm uses that same `VC_VERIFIED_LIBRARY_PATH` and `LD_LIBRARY_PATH` ordering. Missing, alternate, or unparseable resolution aborts the packet.

## Controls and acceptance

Reserve the Linux preparation host exclusively for the three-pair sequence, two CPU slots, 4 GiB owned-process-group RSS limit per arm, at least 8 GiB host RAM, 40 GiB free on archive, and 50 GiB free on scrolls; reserve 0.3 GiB per pair output. Keep outputs, temporary files, logs, and receipts on approved data mounts. Use natural OS cache state; do not flush caches or write to the root filesystem. AB/BA alternation balances warming. Record queue wait and unrelated-host activity separately from measured arm wall time; invalidate the sequence if unrelated project I/O overlaps materially.

Every arm must pass the existing bounded process-group guard and finish with zero owned group RSS and no cleanup error. Require a non-empty render tree, candidate ledger `INITIALIZED`, at least one `VERIFIED` event and zero `REJECTED` events, and byte-for-byte tree equality between A and B for each crop. Preserve any failure and stop; no automatic retry. Report individual arm times, pair order, full guard receipts, linker-resolution proof, source pins, and exact-output comparison. Keep source-pin checks, linker preflight, setup, and comparisons outside the arm timer and report their costs separately. Results apply only to these fixed representatives on this Linux host.

## Launch gate

This protocol is not launch authorization. Before submission, stage and pin the exact contracts, producer scripts, guard, renderer, manifest/view, v5 patch, postcheck evidence, production-caller qualification evidence, and candidate library; verify all three output roots are absent; verify dependencies, host/disk reservations, native descriptor preflight, and central queue schema. Preserve the historical protocol and every prior failed or completed receipt. Do not infer broad workload performance from the one-crop correctness qualification.
