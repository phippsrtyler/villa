# Speedups

My speedups for the pipeline. The open ones are merged together on this branch, on top of main. The new paths are opt-in, so the defaults don't change, and each was checked against main for the same output. Each PR has the full proof and repro commands.

| Stage | Measured | How to use it | PR |
|---|---|---|---|
| Spiral fit (`spiral-fitting`) | 0.313 → 0.230 s/step on an MI50 (−27%) | `FIT_SPIRAL_SEP_UPSAMPLE=1 FIT_SPIRAL_GRAPH_RK4=1` | [#2212](https://github.com/ScrollPrize/villa/pull/2212) |
| Track scoring (`spiral-fitting/tracks.py`) | 5.31 → 2.59 s on an RTX 3080 (2.05x), 22.41 → 10.35 s on an MI50 (2.17x) | always on, output unchanged | [#2218](https://github.com/ScrollPrize/villa/pull/2218) (merged into main) |
| Surface track extraction (`extract_surface_tracks.py`) | 562.8 → 163.8 s and 565.9 → 156.3 s on a 500-slice band (3.4–3.6x), 0 of 192 keys differ | `--backend cpu --cc-device gpu --slab-workers 6 --kimimaro-parallel 1` | [#2221](https://github.com/ScrollPrize/villa/pull/2221) (draft) |
| Render (`vc_render_tifxyz`, GPU sampling) | in progress, waiting on a parity re-check | | pending |
| Flatten (`lasagna`) | in progress, timing not done yet | | pending |

Related, not a speedup: [#2213](https://github.com/ScrollPrize/villa/pull/2213) documents running several `infer.py` processes per GPU.

Track scoring is already in main. It has no flag: it only skips work whose result was thrown away, and its counts were bit-identical under deterministic mode.
