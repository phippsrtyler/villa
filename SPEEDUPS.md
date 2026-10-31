# Speedups

My speedups for the pipeline. The open ones are merged together on this branch, on top of main. Most new paths are opt-in; #2218, #2234 and #2400 are on by default with unchanged output. Each was checked against main: identical output, or for the spiral fit, results inside run-to-run spread. Each PR has the full proof and repro commands.

| Stage | Measured | How to use it | PR |
|---|---|---|---|
| Track scoring (`spiral-fitting/tracks.py`) | 5.31 → 2.59 s on an RTX 3080 (2.05x), 22.41 → 10.35 s on an MI50 (2.17x) | always on, output unchanged | [#2218](https://github.com/ScrollPrize/villa/pull/2218) (merged into main) |
| Spiral fit (`spiral-fitting`) | per step: 1.23x on an RTX 3080, 1.39x on an R9700, 1.45x on an MI50 (0.3082 → 0.2123 s/step) | `FIT_SPIRAL_SEP_UPSAMPLE=1 FIT_SPIRAL_GRAPH_RK4=1` | [#2212](https://github.com/ScrollPrize/villa/pull/2212) |
| Spiral fit constants (`spiral-fitting`) | 0.230 → 0.211 s/step on an MI50 (8%), 1.09x on an RTX 3080, outputs `torch.equal` | always on | [#2234](https://github.com/ScrollPrize/villa/pull/2234) |
| Remote ink reads, shared chunk fetches (`infer_full3d_tifxyz.py`) | 45 Paris 4 patches over HTTPS: 1.65x on an RTX 3080, 1.58x on an R9700, 1.60x on an MI50, 45/45 identical | always on for remote volumes | [#2400](https://github.com/ScrollPrize/villa/pull/2400) (draft) |
| Remote ink reads via vc_reader (`infer_full3d_tifxyz.py`) | 45 Paris 4 patches over HTTPS: 36.6 → 18.1 s on a shared server CPU (2.0x); 1.96x on an R9700 and 1.98x on an MI50 with batches copied to the GPU; 45/45 identical | `--reader vc_reader` | [#2226](https://github.com/ScrollPrize/villa/pull/2226) (draft) |
| Render (`vc_render_tifxyz`, GPU sampling) | 10 PHerc 0800 wraps on an R9700: 49–53 s stock vs 24–26 s (after the first-round kernel build), byte-identical at all 6 levels | `RENDER_GPU=1 scripts/render_gpu/render_band.sh` | [#2225](https://github.com/ScrollPrize/villa/pull/2225) (draft) |
| Surface track extraction (`extract_surface_tracks.py`) | about 3.5x on a 500-slice band with parallel slabs (measured before the GPU-owner change), same tracks | `--backend cpu --cc-device gpu --slab-workers 6 --kimimaro-parallel 1` | [#2221](https://github.com/ScrollPrize/villa/pull/2221) (draft) |

Related, not a code change: [#2213](https://github.com/ScrollPrize/villa/pull/2213) documents running 2–4 `infer.py` processes per GPU (depends on #2189), 1.2–1.4x on the same windings with byte-identical output.

Track scoring is already in main. It has no flag: it only skips work whose result was thrown away, and its counts were bit-identical under deterministic mode.

The #2212, #2400 and #2213 numbers, and the #2234 RTX 3080 number, were re-taken in late October with each card to itself, before/after runs interleaved, at least 3 rounds, median reported. The other numbers are as first measured in each PR. Together they replace the headlines withdrawn on October 24.

## CPU crop preparation: draft PR #2293 (not ready)

[#2293](https://github.com/ScrollPrize/villa/pull/2293) checks each CT chunk it reads against a SHA-256 manifest, instead of rehashing the whole volume for every crop. It is a draft and not ready for review: long jobs currently die after 65,536 ledger events.

On two real Scroll 1218 crops, preparing both took 108.4–110.9 s with whole-volume checks and 10.6 s with this change (10.2–10.5x over three interleaved pairs), with identical output files. That is the CPU crop-prep step only, not GPU inference or the whole pipeline. Human review is still pending. [Evidence and commands](https://github.com/phippsrtyler/villa/tree/f9a86ec7c58fd1c5a5e1705173a6aaec4dd864fe/evidence/2026-10-24-cpu-preparation-v5); an earlier version of the same idea is in [evidence/2026-10-24-preparation](evidence/2026-10-24-preparation/README.md).

## Production notes (October 24)

- Model-reuse correctness checks passed on the MI50, R9700 and RTX 3080 (three each).
- 108 Scroll 1218 inference outputs (window 8832) passed independent validation. That counts outputs, not new text found.
- Automatic next-window production was still being wired up, and no new text had been confirmed.
