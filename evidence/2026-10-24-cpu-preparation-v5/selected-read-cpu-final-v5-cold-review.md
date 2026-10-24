# Independent v5 CPU patch re-review — 2026-10-24

Reviewer: separate rtx_lineage_repair agent, followed by root base/apply verification.
Patch SHA256: 3a0f02fb0cb74e4ed0486e3c94a3ca6fea9a4d30cdca0985ae08c3409a6270fb.

No additional concrete source correctness blocker was found in this pass. The previous allocation-bound finding is fixed: configured and per-row chunk sizes are checked against a 32 MiB per-read cap before allocating. This is not an aggregate concurrent-memory limit.

The documented immutable-tree assumption remains necessary: symlink checks, file-size checks and opening the file are separate operations. Returned bytes are hash-verified; concurrent path mutation is not guaranteed to preserve source confinement. Production callers must honor that assumption.

The 35-case count matches the test source: 12 public read/bypass cases, five evidence failures, swallowed-read rejection, six partial opt-in masks, all-unset stock behavior, eight malformed/boundary manifests, and two stock Store overloads. Missing explicit tests include exact-cap acceptance, zero limit, duplicate JSON members, and concurrent symlink mutation. Do not claim exhaustive malformed-input coverage.

The reviewer lacked the requested base locally. Root subsequently checked the native checkout /mnt/scrolls/vesuvius/flatboi_build/src_pr: HEAD exactly417e17689029434fa1572efe20a3e7a9bfc79be4; standard git apply --check of the staged v5 patch returned0. No checkout edits were made.

Open readiness gates: actual production caller acceptance of a fresh correctly pinned ledger and exact outputs using the v5 library; controlled exact-v5 performance; clean full-repository build evidence versus the focused retained-object build. Original build wrapper failure remains preserved separately from the successful 35-case CTest and later artifact-verification receipt. This review does not establish PR readiness.
