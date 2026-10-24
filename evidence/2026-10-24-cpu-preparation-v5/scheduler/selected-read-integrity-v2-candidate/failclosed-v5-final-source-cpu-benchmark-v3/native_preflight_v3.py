"""Read-only runtime/import/contract/linker preflight; never starts a renderer."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, pathlib, sys

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def load(name, path):
    spec=importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None: raise RuntimeError(f"cannot import {path}")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--descriptor',required=True)
    ap.add_argument('--sequence',required=True)
    ap.add_argument('--helper-root',required=True)
    ap.add_argument('--proof-dir',required=True)
    ap.add_argument('--library-sha256',required=True)
    ap.add_argument('--renderer-sha256',required=True)
    a=ap.parse_args()
    desc=json.loads(pathlib.Path(a.descriptor).read_text())
    assert desc['launch_authorized'] is False
    helper=pathlib.Path(a.helper_root).resolve(strict=True)
    if str(helper) not in sys.path: sys.path.insert(0,str(helper))
    runner=load('paired_runner_v5_preflight',helper/'paired_preparation_runner_v5.py')
    resolver=load('library_resolution_preflight_v3',helper/'library_resolution_preflight.py')
    seq=json.loads(pathlib.Path(a.sequence).read_text())
    configs=[json.loads(pathlib.Path(p).read_text()) for p in seq['configs']]
    assert len(configs)==3
    for cfg in configs: runner.preflight(cfg)
    cfg=configs[0]
    producer=pathlib.Path(cfg['candidate_source']).resolve(strict=True)
    stock=pathlib.Path(cfg['baseline_source']).resolve(strict=True)
    sys.path.insert(0,str(producer.parent))
    # The runner module imports its own same-named audit helper. A production
    # producer is a fresh child interpreter with the producer directory first
    # on sys.path, so evict that preflight-only cached module before simulating
    # the child's import resolution.
    sys.modules.pop('audit_qualification_ledger',None)
    sys.modules.pop('requested_crop_identity_v1',None)
    crop_identity=__import__('requested_crop_identity_v1')
    audit=__import__('audit_qualification_ledger')
    prod=load('qualified_v5_producer_preflight',producer)
    stock_mod=load('qualified_stock_producer_preflight',stock)
    c=json.loads(pathlib.Path(cfg['crops'][0]['contract']).read_text())
    candidate_contract=runner.build_candidate_contract(c,cfg)
    selected=candidate_contract['selected_read_verified']
    assert set(selected)=={'manifest','manifest_sha256','library_root','library_file','library_sha256','audit_source_sha256'}
    assert selected['library_root']==cfg['candidate_library_path']
    assert selected['library_file']==cfg['candidate_library']
    assert sha(selected['library_file'])==a.library_sha256
    producer_host='/mnt/oldpc/vesuvius_park'+str(producer).removeprefix('/archive')
    assert sha(producer)==desc['source_hashes'][producer_host]
    assert crop_identity.__file__==str(producer.parent/'requested_crop_identity_v1.py')
    assert audit.__file__==str(producer.parent/'audit_qualification_ledger.py')
    renderer_contract=json.loads(pathlib.Path(cfg['crops'][0]['contract']).read_text())
    proof_dir=pathlib.Path(a.proof_dir).resolve();proof_dir.mkdir(parents=True,exist_ok=True)
    proof=proof_dir/'linker-resolution.json'
    assert not proof.exists()
    linker=resolver.verify(renderer_contract['binary'],cfg['candidate_library'],a.library_sha256,
                           cfg['candidate_library_path'],str(proof),a.renderer_sha256)
    outputs=[pathlib.Path(x['path']) for x in desc['outputs']]
    assert all(not p.exists() for p in outputs)
    assert all(not pathlib.Path(x['output']).exists() for x in configs)
    result={'status':'PASS_NATIVE_READ_ONLY_PREFLIGHT','launch_authorized':False,'benchmark_started':False,
      'descriptor_id':desc['id'],'descriptor_sha256':sha(a.descriptor),'helper_root':str(helper),
      'candidate_producer':str(producer),'candidate_producer_sha256':sha(producer),
      'stock_producer':str(stock),'stock_producer_sha256':sha(stock),
      'requested_crop_identity':crop_identity.__file__,'requested_crop_identity_sha256':sha(crop_identity.__file__),
      'audit_module':audit.__file__,'audit_module_sha256':sha(audit.__file__),
      'configs_preflighted':len(configs),'contract_count':sum(len(x['crops']) for x in configs),
      'candidate_contract_keys':sorted(selected),'candidate_library_sha256':sha(cfg['candidate_library']),
      'linker_resolution':linker,'linker_proof':str(proof)}
    out=proof_dir/'native-preflight.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
