# Exact-v5 CPU preparation evidence

This bundle supports the opt-in filesystem CT verified-read change, source commit `9e7b78798f58f909f2259352ada4a51823e3c4da` on Villa base `417e17689029434fa1572efe20a3e7a9bfc79be4`.

Three fixed AB/BA/AB comparisons on two real Scroll 1218 crops produced identical complete output trees (38 and 119 files). Summed baseline/candidate preparation times were 110.895/10.610, 108.370/10.609 and 108.898/10.610 seconds; paired ratios 10.45165, 10.21500 and 10.26381. These quantify this Linux CPU preparation component only. They do not measure GPU inference, sustained pipeline throughput, or new ink/text discovery.

Start with:

- [Exact-v5 raw measurements and linker evidence](scheduler/selected-read-integrity-v2-candidate/failclosed-v5-final-source-cpu-benchmark-v3/terminal-evidence/)
- [Independent source re-review](selected-read-cpu-final-v5-cold-review.md)
- [Production evidence: two complete chains](scheduler/selected-read-integrity-v2-candidate/v5-production-two-full-chains.json)
- [Compile/link provenance](cpu-preparation-provenance-20261024/compile-link-provenance.json)
- [35-case fixture report](cpu-preparation-provenance-20261024/v5-native/integrated-fixture-report.json)
- [Byte hashes and external source pins](publication-evidence-manifest-v2.json)

The changed source was rebuilt against pinned retained objects and passed the public API CTest. A clean full-repository build is not proved. The original build wrapper failed after CTest; its receipt is preserved alongside the successful read-only artifact postcheck. Reconstructed compile/link commands are labelled as reconstruction, not an execution transcript.

Historical v2 and earlier artifacts are retained for provenance and are not performance evidence for v5. The opt-in caller must enforce an immutable input tree and reject invalid/rejected read ledgers. The successful ledger verdict is `LEDGER_VALIDATED_NO_TRACE`, not complete per-read tracing. Production-chain evidence establishes integration and structural validation, not scientific interpretation.
