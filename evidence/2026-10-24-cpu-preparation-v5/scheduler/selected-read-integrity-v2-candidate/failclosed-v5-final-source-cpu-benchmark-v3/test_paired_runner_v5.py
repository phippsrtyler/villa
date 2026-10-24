import hashlib,json,pathlib,tempfile,sys,unittest
from types import SimpleNamespace
from unittest import mock
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import paired_preparation_runner_v5 as runner
class CandidateContractTests(unittest.TestCase):
 def test_candidate_receives_closed_qualification_tuple(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=pathlib.Path(td)
   files={name:root/name for name in ('manifest','libutils.so','audit.py')}
   for name,path in files.items():path.write_bytes(name.encode())
   cfg={'manifest':str(files['manifest']),'candidate_library':str(files['libutils.so']),
        'candidate_library_path':'/candidate:/stock','candidate_audit_source':str(files['audit.py'])}
   original={'selected_work_key':'known','library_root':'/stock','selected_read_verified':None}
   out=runner.build_candidate_contract(original,cfg)
   self.assertEqual(out['selected_work_key'],'known')
   self.assertEqual(out['selected_read_verified'],{
    'manifest':str(files['manifest']),'manifest_sha256':hashlib.sha256(b'manifest').hexdigest(),
    'library_file':str(files['libutils.so']),'library_sha256':hashlib.sha256(b'libutils.so').hexdigest(),
    'library_root':'/candidate:/stock','audit_source_sha256':hashlib.sha256(b'audit.py').hexdigest()})
   self.assertIsNone(original['selected_read_verified'])
 def test_stock_contract_does_not_inherit_optin(self):
  c={'selected_work_key':'known','selected_read_verified':{'stale':True}}
  c.pop('selected_read_verified',None)
  self.assertNotIn('selected_read_verified',c)
 def test_candidate_audits_producer_owned_evidence_files(self):
  packet=json.loads((HERE/'benchmark-packet-v2.json').read_text())
  producer=(HERE/'qualified_producer.py').read_text()
  self.assertIn("VC_VERIFIED_CT_LEDGER=str(out/'selected-read-events.jsonl')",producer)
  self.assertIn("emit(out/'selected-read-integrity.json',selected_read_evidence)",producer)
  self.assertIn('from requested_crop_identity_v1 import validate as validate_requested_crop',producer)
  self.assertEqual(hashlib.sha256((HERE/'qualified_producer.py').read_bytes()).hexdigest(),
                   packet['source_correspondence']['qualified_candidate_producer_sha256'])
  identity=(HERE/'requested_crop_identity_v1.py').read_bytes()
  self.assertEqual(hashlib.sha256(identity).hexdigest(),
                   packet['source_correspondence']['qualified_crop_identity_module_sha256'])
 def test_execute_audits_actual_producer_output_root(self):
  with tempfile.TemporaryDirectory(dir=HERE) as td:
   root=pathlib.Path(td);pins={}
   def pinned(name,content):
    p=root/name;p.write_text(content);pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();return str(p)
   manifest=pinned('manifest.json','{}')
   baseline=pinned('stock.py','pass\n');candidate=pinned('candidate.py','pass\n')
   audit=pinned('audit.py','pass\n');library=pinned('libutils.so','native-fixture')
   guard=pinned('guard.py','pass\n')
   crops=[]
   for n,key in enumerate(('crop-a','crop-b')):
    contract=pinned(f'contract-{n}.json',json.dumps({'selected_work_key':key,'library_root':'/stock'}))
    crops.append({'work_key':key,'contract':contract})
   output=root/'pair'
   c={'output':str(output),'order':['baseline','candidate'],'crops':crops,
      'baseline_source':baseline,'candidate_source':candidate,'candidate_audit_source':audit,
      'candidate_library':library,'candidate_library_path':'/candidate:/stock','manifest':manifest,
      'bounded_guard':guard,'view':'/unused','pins':pins}
   observed=[]
   def fake_run(argv,env,stdout,stderr):
    log=pathlib.Path(argv[argv.index('--log')+1]);(pathlib.Path(str(log)+'.json')).write_text(json.dumps({'rc':0,'reason':None,'final_group_rss_bytes':0,'peak_group_rss_bytes':1}))
    cp=pathlib.Path(argv[argv.index('--contract')+1]);contract=json.loads(cp.read_text());science=pathlib.Path(contract['output_root']);render=science/'render.zarr';(render/'0').mkdir(parents=True)
    (render/'.zgroup').write_text('{}');(render/'0/.zarray').write_text('{"fixture":true}')
    (science/'render-receipt.json').write_text('{}')
    if argv[argv.index('--')+3].endswith('candidate.py'):
     (science/'selected-read-events.jsonl').write_text('fixture\n')
     (science/'selected-read-integrity.json').write_text(json.dumps({'status':'LEDGER_VALIDATED_NO_TRACE','events':1,'unique_chunks':1}))
    return SimpleNamespace(returncode=0)
   def fake_audit(manifest_path,expected_sha,ledger,view,env):
    ledger=pathlib.Path(ledger);observed.append(ledger)
    self.assertEqual(ledger.parent.name,'science')
    self.assertEqual(str(ledger),env['VC_VERIFIED_CT_LEDGER'])
    self.assertTrue(ledger.is_file())
    return {'status':'LEDGER_VALIDATED_NO_TRACE','events':1,'unique_chunks':1}
   with mock.patch.object(runner.subprocess,'run',side_effect=fake_run),mock.patch.object(runner,'ledger_only',side_effect=fake_audit):
    report=runner.execute(c)
   self.assertEqual(report['status'],'PAIRED_PREPARATION_EXACT')
   self.assertEqual(len(observed),2)
   self.assertEqual([p.relative_to(output).as_posix() for p in observed],
                    ['arms/candidate-0/science/selected-read-events.jsonl','arms/candidate-1/science/selected-read-events.jsonl'])
if __name__=='__main__': unittest.main(verbosity=2)
