# Selected-read fixed paired pipeline protocol v1 (prospective)

Scientific gate: fixed first broad1218 crop [27,180,1060] and geometry-selected
largest area within frozen RTX-qualified30 [27,180,4640], same original
renderer binary and original crop/options. Exact representative manifest SHA
56dd6c8cd71f17858fe8c7e8a7da9e7469ee23453096c4d47c4560268746d974.
The larger crop was selected without reading timings. Baseline performs current whole CT
byte verification. Candidate changes only that byte-verification strategy to the
isolated read_raw library, bound manifest and metadata. Both preserve all other
preparation and output validation. Explicit opt-in; no live producer replacement.

Three hardware varieties: MI50/gfx906, R9700/gfx1201, RTX/Windows. Preparation is
performed on the same Linux host for ALL three; RTX has no qualified native
renderer. Report Linux preparation once per paired block, plus actual native
stock inference and transfer/validation wall separately for that variety.
Never label Linux prep timings as Windows CPU-native measurements.

Fixed three repetitions per variety, order AB / BA / AB, immutable before launch.
Each preparation block holds one central exclusive-host reservation for both
arms (CPU-only 2 slots, inner4GiB/host5GiB,8GiB RAM floor,40GiB archive floor,
50GiB scrolls floor, archive outputs .3GiB). No production process is interrupted.
Single process per arm, fresh owned paths; full guard and cleanup required before
next arm. Record order, process wall, CT verification wall, rendering wall,
shared source/checkpoint identity, output tree SHA, and complete guard wall.

Trace overhead is excluded from the timed arm: fresh safety-library traced v4
render establishes the boundary on the first input; larger and explicit-absent
actual-render fixtures must pass before timing release. Timed candidate
must still retain INITIALIZED+successful read ledger and zero REJECTED events,
exact canonical view/G0 binding, manifest/environment proof, and exact rendered
output tree. Follow with independent CPU output verification. No unqualified
trace-free promotion: this timing scope measures a candidate whose actual
read boundary was separately traced, not universal I/O interception. The new
library exits86 without core if opt-in initialization or ledger recording fails,
including event exhaustion. REJECTED read evidence always fails the wrapper.

Each variety's native inference uses the same frozen stock checkpoint/options,
forward27,batch1,workers0,no compile and unchanged reservation/caps. Require
independent exact TIFF bytes/SHA across baseline/candidate and retained arm
reference where same-runtime retained output exists. Preserve cross-runtime
MI50-vs-R9700 differences; never use cross-GPU equality as a gate.

Windows shared desktop: retain original strict ownership monitor and actual
attribution. Unknown/foreign ownership means performance invalid while correct
outputs can still pass correctness. Do not relabel existing N/A benchmark data.
Thus all three completion is insufficient for a speed claim if Windows remains
performance ineligible.

Statistics: all nine declared pairs must complete, report individual observations
and paired ratios, not selected best times. Include pipeline transfer/validation
and source-pin preflight overhead explicitly; central queue waiting reported
separately. Warm-state means OS caches may be warm; no cache flush/root writes.
No fixed speed/PR claim or production promotion until all required gates pass.
