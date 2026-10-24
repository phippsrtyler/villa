"""Independent finite-crop identity gate; bootstrap receipts cannot satisfy siblings."""
import hashlib
import json

def validate(producer_contract, catalog_bytes, render_receipt):
    def need(condition, message):
        if not condition:
            raise ValueError(message)
    requested = producer_contract.get('selected_work_key')
    need(isinstance(requested, str) and requested, 'explicit finite crop selection required')
    need(hashlib.sha256(catalog_bytes).hexdigest() == producer_contract.get('finite_catalog_sha256'),
         'exact pinned finite catalog bytes required')
    catalog = json.loads(catalog_bytes)
    entries = catalog['entries']
    keys = [entry['work_key'] for entry in entries]
    need(len(keys) == len(set(keys)), 'duplicate catalog identities')
    matches = [entry for entry in entries if entry['work_key'] == requested]
    need(len(matches) == 1, 'requested crop must exist exactly once')
    expected = matches[0]
    shape = expected['expected_shape']
    need(isinstance(shape, list) and len(shape) == 3 and
         all(type(n) is int and n > 0 for n in shape), 'valid exact crop shape')
    need(render_receipt.get('work_key') == requested, 'rendered crop differs from request')
    need(render_receipt.get('shape') == shape, 'rendered shape differs from requested crop')
    need(render_receipt.get('selected_source') == expected['source_path'],
         'rendered geometry source differs from requested crop')
    return {'status': 'REQUESTED_FINITE_CROP_IDENTITY_PASS',
            'work_key': requested, 'shape': shape,
            'catalog_sha256': producer_contract['finite_catalog_sha256']}
