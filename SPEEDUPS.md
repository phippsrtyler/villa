# Villa pipeline optimization status

Updated October 24, 2026. This hub tracks separate changes; it does not establish an end-to-end pipeline speedup. The historical timing headlines previously shown here are withdrawn from current recommendations pending source and concurrency reconciliation. Historical measurements are not being silently replaced with different workloads.

## Existing pull requests

| Change | Link | Current GitHub status | Evidence status |
|---|---|---|---|
| Separable upsampling and graph replay | [#2212](https://github.com/ScrollPrize/villa/pull/2212) | Open, non-draft | Existing implementation; no newly qualified performance claim in this update |
| Track satisfaction scoring | [#2218](https://github.com/ScrollPrize/villa/pull/2218) | Merged | Existing merged change; historical timing not requalified here |
| GPU connected components and parallel slabs | [#2221](https://github.com/ScrollPrize/villa/pull/2221) | Open, non-draft | Earlier 3.4–3.6× comparison also changed CPU parallelism; not an isolated GPU gain |
| GPU layer sampling | [#2225](https://github.com/ScrollPrize/villa/pull/2225) | Draft | No new qualified full-stage speedup claimed |
| Native full-3D vc_reader loading | [#2226](https://github.com/ScrollPrize/villa/pull/2226) | Draft | Separate from rendered-stack Reader 3; old 2.4× headline is not current qualified evidence |
| Multiple inference processes | [#2213](https://github.com/ScrollPrize/villa/pull/2213) | Open, non-draft | Documentation; existing normalization implementation is not new work here |
| Fitter constant caching | [#2234](https://github.com/ScrollPrize/villa/pull/2234) | Draft | No newly qualified timing claim in this update |

## CPU preparation - draft PR #2293

[Opt-in filesystem CT chunk verification (#2293)](https://github.com/ScrollPrize/villa/pull/2293) is now a draft PR. Three exact-v5 AB/BA/AB comparisons on two fixed real Scroll 1218 crops produced identical complete output trees. Combined baseline/candidate times were 110.895/10.610, 108.370/10.609 and 108.898/10.610 seconds: paired ratios **10.45x, 10.22x and 10.26x**. These measure the tested Linux CPU preparation component only, not GPU inference or sustained pipeline throughput.

[Immutable exact-v5 evidence, commands and limitations](https://github.com/phippsrtyler/villa/tree/f9a86ec7c58fd1c5a5e1705173a6aaec4dd864fe/evidence/2026-10-24-cpu-preparation-v5) includes independent source re-review, 35 public API fixture cases, full output comparisons, and two production chains through independent input/output validation. The changed source was rebuilt against pinned retained objects; a clean full-repository build remains unverified. Human review remains pending, and the PR is not presented as merge-ready.

## Historical preparation experiment - earlier candidate

The older candidate below is distinct from exact-v5 and retained for provenance. Nine paired Linux CPU preparation tests for two crops each produced exact matching output trees. Baseline sums were 59.376–64.259 seconds; selected-read candidate sums were 10.603–11.107 seconds. Median paired ratio: 5.802832×. [Evidence, per-pair values and limitations](evidence/2026-10-24-preparation/README.md).

Scope: warm OS cache, with observed background controller CPU; one repetition overlapped 12.733 seconds of cross-host transfer. Hardware labels on these preparation jobs identify downstream qualification cohorts, not native GPU timing. This is a scoped component observation, not a clean isolated-host or end-to-end speedup. Do not add or multiply it with other ratios. CPU-only PR readiness requires reproducible CPU correctness and performance evidence, independent cold review, and verified production integration; three-GPU verification does not apply to this CPU-only preparation change.

## Correctness and production progress

Nine model-reuse correctness blocks completed across MI50, R9700 and RTX3080 (three per variety). Performance qualification remains incomplete, including shared-desktop RTX attribution.

108 Scroll 1218 window-8832 inference outputs have successful independent central validation receipts. This is a bounded production-output count, not a claim of 108 new text discoveries or total project production.

Automatic next-window production is being integrated. Sustained four-GPU utilization and two hours of runnable backlog per GPU have not been demonstrated. New-text discovery has not been confirmed.
