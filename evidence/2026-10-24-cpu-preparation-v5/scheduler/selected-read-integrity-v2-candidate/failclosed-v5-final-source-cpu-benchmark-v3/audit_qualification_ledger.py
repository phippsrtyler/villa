"""Qualification-only acceptance checks; trace extraction remains a separate required proof."""
import hashlib
import json
from collections import Counter
from pathlib import Path


def _validated_counts(manifest_path, expected_sha, ledger_path, view_root, env):
    manifest_path = Path(manifest_path).resolve(strict=True)
    raw = manifest_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected_sha, 'manifest digest'
    manifest = json.loads(raw)
    assert manifest['schema'] == 'verified-ct-read-manifest-v1'
    volume = Path(manifest['volume_root']).resolve(strict=True)
    assert (Path(view_root) / '0').resolve(strict=True) == (volume / '0').resolve(strict=True), 'CT view volume mismatch'
    assert Path(env['VC_VERIFIED_CT_MANIFEST']).resolve(strict=True) == manifest_path
    assert env['VC_VERIFIED_CT_MANIFEST_SHA256'] == expected_sha
    assert Path(env['VC_VERIFIED_CT_LEDGER']).resolve() == Path(ledger_path).resolve()
    ledger = Path(ledger_path)
    assert ledger.stat().st_size <= 32 * 1024 * 1024, 'ledger bound'
    rows = [json.loads(line) for line in ledger.read_text().splitlines()]
    assert rows and rows[0] == {'status': 'INITIALIZED', 'key': expected_sha, 'bytes': 0}, 'initialization missing'
    assert sum(r['status'] == 'INITIALIZED' for r in rows) == 1
    expected = {r['key']: r for r in manifest['objects']}
    assert len(expected) == len(manifest['objects'])
    counts = Counter()
    for row in rows[1:]:
        assert row['status'] in ('VERIFIED_PRESENT', 'EXPLICIT_ABSENT'), 'rejection or unknown ledger event'
        item = expected[row['key']]
        absent = row['status'] == 'EXPLICIT_ABSENT'
        assert item['absent'] is absent
        assert type(row['bytes']) is int and row['bytes'] == (0 if absent else item['bytes'])
        counts[row['key']] += 1
    assert counts and any(r['status'] == 'VERIFIED_PRESENT' for r in rows), 'no successful CT read coverage'
    return counts


def ledger_only(manifest_path, expected_sha, ledger_path, view_root, env):
    counts = _validated_counts(manifest_path, expected_sha, ledger_path, view_root, env)
    return {'status': 'LEDGER_VALIDATED_NO_TRACE', 'events': sum(counts.values()), 'unique_chunks': len(counts)}


def audit(manifest_path, expected_sha, ledger_path, view_root, env, traced_chunk_keys):
    counts = _validated_counts(manifest_path, expected_sha, ledger_path, view_root, env)
    traced = Counter(traced_chunk_keys)
    assert traced and counts == traced, 'trace/ledger mismatch or unguarded CT reads'
    return {'status': 'LEDGER_AND_TRACE_BOUND', 'events': sum(counts.values()), 'unique_chunks': len(counts)}
