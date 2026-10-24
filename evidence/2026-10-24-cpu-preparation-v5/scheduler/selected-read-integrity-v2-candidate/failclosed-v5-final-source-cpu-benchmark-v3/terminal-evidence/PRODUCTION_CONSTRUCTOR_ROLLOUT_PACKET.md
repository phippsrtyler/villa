# Exact v5 production constructor mapping (prospective)

The source-level caller and the paired candidate are the same bytes: `production_finite_optin_v2.py` and the staged `qualified_producer.py` both hash to `8ec9c25525a7f55cfdc3b179c2b0dec2ed16eb1603fe05c196ba2e43df4af2ea`. In the caller, `main()` reads `selected_read_verified` from the crop contract at line 32 and validates the closed six-key schema, audit source, library bytes, and loader path in lines 34–40. Absence of that field leaves the stock path. The accepted one-crop production-caller qualification is separate evidence; this paired benchmark did not modify the production catalog.

The concrete constructor used by the v5 paired runner is `build_candidate_contract(contract, c)` in `paired_preparation_runner_v5.py` (SHA-256 `b07e8b10356876fc525e09f8ed5032e48c61f392ee337c9e676ed2ddb8a7a966`). It copies a resolved crop contract and inserts exactly:

```python
contract['selected_read_verified'] = {
    'manifest': c['manifest'],
    'manifest_sha256': sha(c['manifest']),
    'library_file': c['candidate_library'],
    'library_sha256': sha(c['candidate_library']),
    'library_root': c['candidate_library_path'],
    'audit_source_sha256': sha(c['candidate_audit_source']),
}
```

To wire a future unaccepted producer descriptor, call this constructor only after its finite crop/work-key identity is resolved. Point `candidate_audit_source` to the exact sibling `audit_qualification_ledger.py` imported beside the candidate producer; the caller compares that sibling's bytes to `audit_source_sha256`. Keep the library-file SHA and loader root pinned, and keep the original selected manifest SHA and volume binding. Candidate output_root must be a fresh owned per-crop directory. The v5 producer puts its ledger at `<output_root>/selected-read-events.jsonl`; its selected-read environment points there. Baseline contracts remove `selected_read_verified` and every inherited `VC_VERIFIED_*` variable.

The older helper `qualify_production_optin.py` also constructs the same six-key object, but derives its audit source as `candidate_source.parent / 'audit_qualification_ledger.py'`. Use it only if the future staged producer's import layout is byte-identical to that rule; otherwise use the exact v5 `build_candidate_contract` input binding above. Do not merely reuse the one-crop receipt for new crop keys. Each target descriptor still needs its own contract hash, candidate source/library/import closure pins, stock comparison contract, fresh output, exact output-tree equality, candidate ledger acceptance, and zero-owned-process cleanup before activation. No production descriptor or catalog entry was changed by this packet.
