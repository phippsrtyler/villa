from __future__ import annotations
import hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
P=HERE/'benchmark-packet-v2.json'
D=json.loads(P.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert D['schema']=='selected-read-final-source-v5-cpu-paired-benchmark-v2'
assert 'NOT_SUBMITTED' in D['status']
assert D['source_correspondence']['candidate_library_sha256']=='e4287923b8468a157eba6895d82c17a2f00105eeda32a6c9ec6755673b52231d'
assert D['source_correspondence']['candidate_patch_sha256']=='3a0f02fb0cb74e4ed0486e3c94a3ca6fea9a4d30cdca0985ae08c3409a6270fb'
assert D['design']['arm_orders']==['baseline,candidate','candidate,baseline','baseline,candidate']
assert D['design']['fixed_crops']==[{'label':'broad1218-first','coordinates':[27,180,1060]},{'label':'geometry-selected-largest','coordinates':[27,180,4640]}]
for f,h in [('run_pinned_paired_benchmark.py','sha256'),('library_resolution_preflight.py','sha256'),('CPU_ONLY_PROTOCOL_AMENDMENT_V2.md','sha256'),('paired_preparation_runner_v5.py','paired_runner_sha256')]:
 row={'run_pinned_paired_benchmark.py':D['runner']['sha256'],'library_resolution_preflight.py':D['runner']['library_resolution_preflight_sha256'],'CPU_ONLY_PROTOCOL_AMENDMENT_V2.md':D['runner']['cpu_protocol_amendment_sha256'],'paired_preparation_runner_v5.py':D['runner']['paired_runner_sha256']}[f]
 assert sha(HERE/f)==row,(f,sha(HERE/f),row)
assert sha(HERE/'qualified_producer.py')==D['source_correspondence']['qualified_candidate_producer_sha256']
assert sha(HERE/'requested_crop_identity_v1.py')==D['source_correspondence']['qualified_crop_identity_module_sha256']
assert D['source_correspondence']['production_caller_qualification_sha256']=='7a055258e57115efb2182077cb384110f73f243fa2a85c090f3533992f334f87'
assert len(D['design']['dependencies'])==6
out={'status':'PASS_LOCAL_V5_PACKET_STRUCTURE_AND_LOCAL_PINS; NATIVE_LINKER_PREFLIGHT_AND_SOURCE_PINS_PENDING','packet_sha256':sha(P),'descriptor_template_sha256':sha(HERE/'selected-read-final-source-v5-cpu-preparation-v1.json'),'launch_authorized':False,'submitted':False,'native_preflight':'not run from this Windows workspace; exact renderer/lib linker check remains a launch gate'}
(HERE/'local-validation-v2.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
