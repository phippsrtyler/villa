# Independent terminal audit: v5 CPU paired benchmark

The parent-submitted job `selected-read-final-source-v5-cpu-preparation-v3` (central digest `30eb0b1b7b3c7eae2f4da8b2334bf4f88edf202b71bc7599fc4e223c563e12cd`) finished `SUCCEEDED`, `validated=true`, return code 0. The central outer guard ran 361.356 s and recorded `final_group_rss_bytes=0`; the nested supervisor guard recorded `rc=0`, `inner_cleanup_verified=true`, and zero final RSS. All 12 producer arms recorded rc 0, no reason, and zero final process-group RSS.

The pinned summary is `ALL_THREE_PAIRED_REPETITIONS_EXACT`. The order was AB/BA/AB, with unchanged stock whole-CT verification as A and exact v5 verified-read producer as B. Each pair contains two work keys:

| Work key / output shape | Stock times (s) | v5 times (s) | Mean ratio |
|---|---:|---:|---:|
| `59a887eef7e8385596ae84f1a9296db306439ce1ed09ab78aaf331360e3de20b` / `[27,180,1060]` | 55.200, 54.185, 54.208 | 5.055, 5.049, 5.055 | 10.79× |
| `24655cb86a8d39faefcf4ecc51991cd41f75646c1a1b815e621bb99fb65ed195` / `[27,180,4640]` | 55.695, 54.185, 54.690 | 5.555, 5.560, 5.555 | 9.87× |

For every same-repeat, same-work-key pair, the baseline and candidate output hash maps matched exactly: 38 entries for the first output and 119 for the second. Each of the six candidate arms reported `LEDGER_VALIDATED_NO_TRACE`, with successful verified reads, unique chunks, and no rejected/unknown ledger records according to the pinned audit implementation. Event/unique-chunk counts by pair are in the preserved `r1-pair.json` through `r3-pair.json`. This is a ledger validation, not a trace-bound read proof.

The linker-resolution proof resolves the renderer's `libutils.so` to the pinned v5 library SHA-256 `e4287923b8468a157eba6895d82c17a2f00105eeda32a6c9ec6755673b52231d`. The source patch is `selected-read-cpu-final-v5.patch`, SHA-256 `3a0f02fb0cb74e4ed0486e3c94a3ca6fea9a4d30cdca0985ae08c3409a6270fb`. The experiment is CPU-only, Linux-host-specific, and limited to these two fixed crops, this renderer/library, two reserved CPU slots, and the protocol's 4 GiB per-arm RSS bound. It does not establish GPU, cross-card, all-workload, or image-quality outcomes.

The original machine files were copied without transformation from the job's output directory. Local evidence file hashes:

- `cpu-paired-summary.json`: `232f800b3967b299d20c9940fdca02030aaf85255a7c402315fc59885697554a`
- `central-receipt.json`: `759d9681d79ac87276cc70458bc53d6f91002bc5b1be29b57c49f1285c9ad76d`
- `linker-resolution.json`: `ef34cc3eea8babd262f440392d3a767223b7b45e86a15333b09ca08bd39c3a89`
- `r1-pair.json`: `5dcf73181d4ea4f6440fe4f349d198bb39e50f9f62971845d5f285a11fd0bc1c`
- `r2-pair.json`: `34033c359226412422b474e37bf9025d21b982caad8d4c18cfcea821ff524d9b`
- `r3-pair.json`: `960e8f612ce8d71f754e161e967a3ce2b20fd527874e9adcb8c46b0b9f619150`
- `sequence.json`: `81c24b858cd070a270b59d8a47e1d12e0bdb3269caa82afc255d88a62471f0b4`
- `CPU_ONLY_PROTOCOL_AMENDMENT_V2.md`: `582b3fd34d45fd605bcc03a123a21a6bc2a688d6e65af6fe55ce586c7918730c`
