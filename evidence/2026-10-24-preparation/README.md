# CPU preparation observation — October 24, 2026

This evidence extract reports nine fixed pairs, each summing two CPU crop-preparation runs on the same Linux host. The candidate uses selected-read verification. Baseline and candidate rendered output trees matched in the native audit. Device names in job IDs identify downstream cohorts, not GPU measurements.

The accompanying JSON retains every pair, per-report hashes, descriptor identities and successful central receipt metadata. The median of baseline/candidate ratios is 5.802832252601815. These timings are component observations: warm OS cache, observed background controller CPU, and 12.7328689 seconds of cross-host transfer overlap in the RTX-labelled first pair. They do not establish isolated-host, GPU or whole-pipeline performance.

The aggregate hash identifies the source audit used for this extract, not the JSON file itself. Receipt metadata records execution and declared validation; it is not an independent reproduction of the underlying output trees. This extract is not a complete portable reproduction bundle. Exact upstream build provenance, CMake integration testing and final cold review remain outstanding for an upstream implementation PR. CPU-only changes do not require three-GPU performance qualification.

Recompute the descriptive median with Python's standard library:

```python
import json, statistics
from pathlib import Path
report = json.loads(Path('preparation-nine-pairs.json').read_text())
ratios = [b['baseline'] / b['candidate'] for b in report['blocks']]
assert len(ratios) == 9
assert all(b['central_receipt']['validated'] and b['central_receipt']['returncode'] == 0 for b in report['blocks'])
assert abs(statistics.median(ratios) - report['median_paired_ratio']) < 1e-12
print(statistics.median(ratios))
```

This checks the published arithmetic and receipt fields, not execution correctness or reproducibility.
