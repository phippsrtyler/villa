# Exact-v5 publication audit

Independent read-only review, 2026-10-24. No PR was published and no science was rerun.

The evidence now supports a narrowly scoped **draft CPU-preparation PR for review**. I found no new concrete code correctness blocker in the exact reviewed patch. This is not clean-build or merge approval, and it is not a GPU or whole-pipeline performance result. Three GPU performance tests are not a gate for this CPU-only change.

## Bound identities and checks

- Villa base: `417e17689029434fa1572efe20a3e7a9bfc79be4`. The retained cold-review records root's exact native HEAD and successful `git apply --check` against this base.
- Patch: `scheduler/selected-read-integrity-v2-candidate/failclosed-v3-repair-v1/selected-read-cpu-final-v5-review.patch`, SHA256 `3a0f02fb0cb74e4ed0486e3c94a3ca6fea9a4d30cdca0985ae08c3409a6270fb`, independently rehashed here.
- Qualified library: `e4287923b8468a157eba6895d82c17a2f00105eeda32a6c9ec6755673b52231d`. The final benchmark linker proof binds the loaded library; the 35-case retained build report has a separate successful acceptance receipt. The original wrapper failure remains preserved.
- Existing build artifacts are under `/mnt/oldpc/vesuvius_park/selected-read-upstream-failclosed-v5-cpu-qualification/`: `build-and-test.log`, `cmake-source/`, `receipt.json`, `launch.json`, `ldd.txt`, and `libutils.so`. The source rebuild script consumes `/mnt/oldpc/vesuvius_park/selected-read-integrity-v3-source/build-provenance.json` for source-snapshot hashes, original compile command and retained objects. These records should be exported together; this audit did not rerun a build.
- Final benchmark: central `selected-read-final-source-v5-cpu-preparation-v3`, digest `30eb0b1b7b3c7eae2f4da8b2334bf4f88edf202b71bc7599fc4e223c563e12cd`, validated success. Summary SHA256 `232f800b3967b299d20c9940fdca02030aaf85255a7c402315fc59885697554a`. All seven raw evidence hashes in `root-derived-component-metrics.json` were independently rechecked. The three two-crop paired ratios are 10.45165, 10.21500, and 10.26381; all 38/119-file output maps match. This is fixed-workload Linux CPU preparation, not sustained production throughput. Candidate ledger results are `LEDGER_VALIDATED_NO_TRACE`.
- Actual production: `scheduler/selected-read-integrity-v2-candidate/v5-production-two-full-chains.json`, SHA256 `94fc146928c469ca2cccc2101c9f4d589fdddf18aff81ac322c19c6288b2244c`, copied without transformation from the native handoff evidence. Two distinct 9216/9344 crops have all eight producer/input-validator/GPU/output-validator jobs successful, with exact dependency, receipt and inference identity bindings. This closes the production-caller gate; it does not establish ink, text, image quality or performance.
- Native constructor proof `v5-production-native-verification-v2.json` covers 48 contexts/2029 keys, 24 descriptor admissions and 12 real constructor previews. Its receipt stubs make it a construction proof, separate from the actual two-chain evidence.

## Before publication

1. Replace the contradictory historical readiness header in `CPU_PREPARATION_PR_REVIEW.md` with one current checkpoint and clearly label the remaining historical sections. It still says controller resume/downstream completion are pending. Do not use old-library 5.80x or v2 timing as evidence for v5.
2. Attach the exact patch, cold review, final benchmark protocol/raw receipts/linker proof, 35-case acceptance record, actual two-chain evidence, and a manifest of their hashes. Include the existing source snapshot/retained-object provenance and exact compile/link commands. The local qualification manifest alone says PREPARED and is not a terminal build report.
3. State the build limitation plainly: the changed C++ source was compiled and linked against pinned retained objects; public API CTest passed. A clean full-repository configure/build is unproved. The historical focused CMake fixture against an imported library does not establish full project linkage. Do not require or launch another scientific qualification solely to package existing provenance.

The frozen patch's documentation contains an older explicitly labelled final-source-v2 measurement. Preserve source identity for this review; the PR body must distinguish that historical figure from the exact-v5 results. If documentation source is changed before submission, generate a new patch hash and review that documentation-only diff rather than silently retaining the old identity.

## Draft PR text

Title: **Add opt-in manifest verification for filesystem CT chunk reads**

Repeated whole-volume hashing dominated preparation of small crops from an immutable restored CT dataset. This adds an opt-in filesystem Zarr2 G0 path that validates the exact compressed buffer returned to the decoder against a complete SHA256 manifest, including explicit absence records. With all opt-in variables absent the stock read path remains unchanged.

The guard rejects unsupported Store, shard and mmap paths. It bounds each guarded allocation to 32 MiB, records initialized/read/rejection evidence, and terminates on evidence infrastructure failure. Callers must keep the source tree immutable and reject any invalid or rejected ledger before accepting output; this is not universal I/O interception or race-free confinement against concurrent path replacement. Store-backed opens are rejected process-wide while opt-in is active.

Validation: exact base/apply check; focused retained-object rebuild and 35 public API cases; three AB/BA/AB CPU pairs on two fixed real crops with complete rendered-tree equality; and two fresh production crops passing independent input and output validation. The measured two-crop stock/candidate preparation ratios were 10.45x, 10.22x and 10.26x on this Linux host. These are CPU preparation component observations, not GPU, universal or whole-pipeline gains. A clean full-repository configure/build remains unverified; exact provenance and raw evidence are attached.
