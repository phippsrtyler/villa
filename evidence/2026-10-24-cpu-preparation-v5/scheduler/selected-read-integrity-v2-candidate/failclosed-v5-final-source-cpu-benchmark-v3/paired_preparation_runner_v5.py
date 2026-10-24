"""Fixed CPU preparation pair under one central reservation; no queue claims."""
import argparse,json,math,os,pathlib,subprocess,sys,time
from qualify_render import sha,tree
from audit_qualification_ledger import ledger_only

def candidate_evidence_paths(science_root):
 science_root=pathlib.Path(science_root)
 return science_root/'selected-read-events.jsonl',science_root/'selected-read-integrity.json'

def build_candidate_contract(contract, c):
    contract = dict(contract)
    contract['selected_read_verified'] = {
        'manifest': c['manifest'],
        'manifest_sha256': sha(c['manifest']),
        'library_file': c['candidate_library'],
        'library_sha256': sha(c['candidate_library']),
        'library_root': c['candidate_library_path'],
        'audit_source_sha256': sha(c['candidate_audit_source']),
    }
    return contract

def preflight(c):
 root=pathlib.Path(c['output'])
 assert root.is_absolute()
 assert not (root/'pair.json').exists() and not (root/'arms').exists(),'fresh owned packet root'
 assert c['order'] in (['baseline','candidate'],['candidate','baseline'])
 assert len(c['crops'])==2 and len({r['work_key'] for r in c['crops']})==2
 required={c[k] for k in ('baseline_source','candidate_source','candidate_audit_source','manifest','bounded_guard','candidate_library')}
 required.update(r['contract'] for r in c['crops'])
 assert required.issubset(c['pins']),'complete execution source/contract/library pin closure'
 assert all(sha(p)==h for p,h in c['pins'].items()),'frozen common source pins'
 for crop in c['crops']:
  contract=json.loads(pathlib.Path(crop['contract']).read_text())
  assert contract['selected_work_key']==crop['work_key'],'contract identity'
 return root

def execute(c):
 root=preflight(c);root.mkdir(exist_ok=True)
 arms=root/'arms';arms.mkdir();results=[];began=time.monotonic()
 for mode in c['order']:
  for index,crop in enumerate(c['crops']):
   out=arms/(mode+'-'+str(index));out.mkdir()
   contract=json.loads(pathlib.Path(crop['contract']).read_text());science_root=out/'science';contract['output_root']=str(science_root)
   if mode=='candidate':
    contract=build_candidate_contract(contract,c)
   else:
    contract.pop('selected_read_verified',None)
   cp=out/'contract.json';cp.write_text(json.dumps(contract,indent=2)+'\n')
   temp=out/'tmp';temp.mkdir()
   env=dict(os.environ,TMPDIR=str(temp),TMP=str(temp),TEMP=str(temp),PYTHONOPTIMIZE='0',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',HIP_VISIBLE_DEVICES='',CUDA_VISIBLE_DEVICES='')
   if mode=='candidate':
    # Match the pinned production producer: it owns this exact ledger path and
    # emits selected-read-integrity.json next to it.
    ledger_path,_=candidate_evidence_paths(science_root)
    env.update(VC_VERIFIED_CT_MANIFEST=c['manifest'],VC_VERIFIED_CT_MANIFEST_SHA256=sha(c['manifest']),VC_VERIFIED_CT_LEDGER=str(ledger_path),VC_VERIFIED_LIBRARY_PATH=c['candidate_library_path'])
   else:
    for k in list(env):
     if k.startswith('VC_VERIFIED_'):env.pop(k)
   guard=out/'guard.json'
   argv=[sys.executable,'-B',c['bounded_guard'],'--seconds','180','--gib','4','--shutdown-grace-s','2','--log',str(guard),'--',sys.executable,'-B',c[mode+'_source'],'--contract',str(cp),'--sha256',sha(cp)]
   started=time.monotonic()
   # The already bounded guard owns its child and deadline. Never impose a
   # subprocess.run timeout that kills only that guard and strands its child.
   # The enclosing centrally supervised pair provides the total-run deadline.
   with (out/'process.log').open('wb') as log:r=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT)
   wall=time.monotonic()-started
   assert math.isfinite(wall) and wall>0,'positive finite measured process wall'
   assert r.returncode==0,'arm process failure; no next arm'
   g=json.loads(pathlib.Path(str(guard)+'.json').read_text())
   assert all(k in g for k in ('rc','reason','final_group_rss_bytes','peak_group_rss_bytes')),'guard schema'
   assert g['rc']==0 and g['reason'] is None and g['final_group_rss_bytes']==0 and g.get('cleanup_error') is None,'unclean arm; no advance'
   peak=g['peak_group_rss_bytes'];assert type(peak) in (int,float) and math.isfinite(peak) and 0<peak<=4*2**30,'sampled arm bound'
   actual=tree(out/'science/render.zarr');assert actual,'empty render'
   evidence=None
   if mode=='candidate':
    # No syscall reconciliation is claimed for timed runs. Exact library read
    # boundary was independently traced; evidence failures are fatal exit86.
    ledger,integrity_path=candidate_evidence_paths(science_root)
    evidence=ledger_only(c['manifest'],sha(c['manifest']),ledger,c['view'],env)
    integrity=json.loads(integrity_path.read_text())
    assert integrity==evidence,'producer integrity receipt and independently checked ledger disagree'
   receipt=json.loads((out/'science/render-receipt.json').read_text())
   results.append({'mode':mode,'work_key':crop['work_key'],'wall_seconds':wall,'guard':g,'output':str(out/'science/render.zarr'),'output_hashes':actual,'producer_receipt':receipt,'ledger':evidence,'execution_source_sha256':sha(c[mode+'_source']),'execution_library_sha256':sha(c['candidate_library']) if mode=='candidate' else None})
 for crop in c['crops']:
  pair=[r for r in results if r['work_key']==crop['work_key']]
  assert len(pair)==2 and pair[0]['output_hashes']==pair[1]['output_hashes'],'exact baseline/candidate rendered bytes'
 report={'status':'PAIRED_PREPARATION_EXACT','results':results,'whole_pair_seconds':time.monotonic()-began,'scope':'Linux CPU preparation for declared downstream hardware; warm OS cache, no trace overhead; not native GPU throughput or universal read coverage.'}
 (root/'pair.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--preflight',action='store_true');a=p.parse_args();c=json.loads(pathlib.Path(a.config).read_text());preflight(c) if a.preflight else execute(c)
