# Villa pipeline optimization status

Updated October 24, 2026. This hub tracks separate changes; it does not establish an end-to-end pipeline speedup. The historical timing headlines previously shown here are withdrawn from current recommendations pending source and concurrency reconciliation. Historical measurements are not being silently replaced with different workloads.

## Existing pull requests

| Change | Link | Current GitHub status | Evidence status |
|---|---|---|---|
| Separable upsampling and graph replay | [#2212](https://github.com/ScrollPrize/villa/pull/2212) | Open, non-draft | Existing implementation; no newly qualified performance claim in this update |
| Track satisfaction scoring | [#2218](https://github.com/ScrollPrize/villa/pull/2218) | Merged | Existing merged change; historical timing not requalified here |
| GPU connected components and parallel slabs | [#2221](https://github.com/ScrollPrize/villa/pull/2221) | Open, non-draft | Earlier 3.4â€“3.6Ã— comparison also changed CPU parallelism; not an isolated GPU gain |
| GPU layer sampling | [#2225](https://github.com/ScrollPrize/villa/pull/2225) | Draft | No new qualified full-stage speedup claimed |
| Native full-3D vc_reader loading | [#2226](https://github.com/ScrollPrize/villa/pull/2226) | Draft | Separate from rendered-stack Reader 3; old 2.4Ã— headline is not current qualified evidence |
| Multiple inference processes | [#2213](https://github.com/ScrollPrize/villa/pull/2213) | Open, non-draft | Documentation; existing normalization implementation is not new work here |
| Fitter constant caching | [#2234](https://github.com/ScrollPrize/villa/pull/2234) | Draft | No newly qualified timing claim in this update |

## New preparation experiment â€” not yet an upstream PR

The following older candidate is distinct from exact-v5 above and is retained for provenance. Nine paired Linux CPU preparation tests for two crops each produced exact matching output trees. Baseline sums were 59.376â€“64.259 seconds; selected-read candidate sums were 10.603â€“11.107 seconds. Median paired ratio: 5.802832Ã—. [Evidence, per-pair values and limitations](evidence/2026-10-24-preparation/README.md).

Scope: warm OS cache, with observed background controller CPU; one repetition overlapped 12.733 seconds of cross-host transfer. Hardware labels on these preparation jobs identify downstream qualification cohorts, not native GPU timing. This is a scoped component observation, not a clean isolated-host or end-to-end speedup. Do not add or multiply it with other ratios. CPU-only PR readiness requires reproducible CPU correctness and performance evidence, independent cold review, and verified production integration; three-GPU verification does not apply to this CPU-only preparation change.

## Correctness and production progress

Nine model-reuse correctness blocks completed across MI50, R9700 and RTX3080 (three per variety). Performance qualification remains incomplete, including shared-desktop RTX attribution.

108 Scroll 1218 window-8832 inference outputs have successful independent central validation receipts. This is a bounded production-output count, not a claim of 108 new text discoveries or total project production.

Automatic next-window production is being integrated. Sustained four-GPU utilization and two hours of runnable backlog per GPU have not been demonstrated. New-text discovery has not been confirmed.
