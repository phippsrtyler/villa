# v5 production rollout mapping (prospective; no catalog mutation)

## Qualified inputs

- Library: `/mnt/oldpc/vesuvius_park/selected-read-upstream-failclosed-v5-cpu-qualification/libutils.so`, SHA-256 `e4287923b8468a157eba6895d82c17a2f00105eeda32a6c9ec6755673b52231d`.
- Source patch: `/mnt/oldpc/vesuvius_park/selected-read-upstream-failclosed-v5-source/selected-read-cpu-final-v5.patch`, SHA-256 `3a0f02fb0cb74e4ed0486e3c94a3ca6fea9a4d30cdca0985ae08c3409a6270fb`.
- Production-caller qualification: `/mnt/oldpc/vesuvius_park/selected-read-v5-optin-integration-qualification-v2/science/integration.json`, SHA-256 `7a055258e57115efb2182077cb384110f73f243fa2a85c090f3533992f334f87`.

## Application path

The source-level opt-in boundary is `selected_read_verified` in `scheduler/selected-read-integrity-v1/production_finite_optin_v2.py`. It accepts a closed contract containing the manifest path and SHA, library file and SHA, loader search root, and ledger-audit source SHA. The producer binds the manifest to the validated volume and complete present/absent partition, sets `VC_VERIFIED_CT_MANIFEST`, `VC_VERIFIED_CT_MANIFEST_SHA256`, and `VC_VERIFIED_CT_LEDGER` only for explicit opt-in, and launches the renderer with the selected loader path. The generated producer used by the v2 integration is `/archive/selected-read-v5-optin-integration-qualification-v2-source/producer.py`.

Future unaccepted descriptors should map to that exact reviewed caller/config contract and v5 library pin. Verify the generated `producer.py` hash against its qualification receipt (or prove byte identity to the source-level opt-in implementation) before reuse. Do not assume the older `selected_finite_producer.py` is the same caller. For baseline arms, remove every inherited `VC_VERIFIED_*` variable. Preserve stock behavior unless a descriptor explicitly opts in.

## Scope of the current caller proof

The v2 integration qualification establishes one crop end to end: the producer wrote a 55-entry result tree identical to its pinned reference, while the ledger recorded 43 events for 43 unique chunks, with no rejected reads, and the guards reported clean process cleanup. This supports the tested caller wiring and one representative data path. It does not establish performance and does not cover absent/partial metadata, missing chunks, malformed manifests, empty selections, multiple crops, or every future descriptor shape. Before mapping a descriptor that exercises one of those branches, require its corresponding existing fixture or a bounded targeted qualification against the exact v5 library. Do not replay accepted production work merely to add coverage.

## Rollout gates

1. Complete the exact-v5 AB/BA/AB CPU packet in `benchmark-packet-v2.json`; require linker resolution to the pinned v5 library, exact output equality, ledger checks, and owned-process cleanup.
2. Match each future descriptor's input manifest/view, crop contract, candidate producer hash, opt-in environment, and expected output contract to the v5 caller pins before candidate selection.
3. Keep candidate activation opt-in until the target descriptor passes those gates. Record its new receipt separately; do not edit accepted catalog entries or retroactively apply the v2 one-crop receipt to other workloads.
