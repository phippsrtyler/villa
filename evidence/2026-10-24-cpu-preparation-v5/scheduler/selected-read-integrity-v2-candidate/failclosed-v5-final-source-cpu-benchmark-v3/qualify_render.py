"""Isolated qualification body. No production entry point or integrity gate is replaced."""
import argparse,collections,hashlib,json,os,pathlib,re,subprocess,time
from audit_qualification_ledger import audit

def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def tree(p):return {str(x.relative_to(p)):sha(x) for x in pathlib.Path(p).rglob('*') if x.is_file()}
def main():
 a=argparse.ArgumentParser();a.add_argument('--config',required=True);a=a.parse_args();c=json.loads(pathlib.Path(a.config).read_text());o=pathlib.Path(c['output']);o.mkdir(exist_ok=True)
 assert not (o/'render.zarr').exists() and not (o/'events.jsonl').exists()
 for p,h in c['pins'].items():assert sha(p)==h, 'input pin '+p
 volume=pathlib.Path(c['volume']);view=pathlib.Path(c['view']);assert (view/'0').resolve(strict=True)==(volume/'0').resolve(strict=True)
 manifest=pathlib.Path(c['manifest']);mh=sha(manifest);env=dict(os.environ,VC_VERIFIED_CT_MANIFEST=str(manifest),VC_VERIFIED_CT_MANIFEST_SHA256=mh,VC_VERIFIED_CT_LEDGER=str(o/'events.jsonl'),LD_LIBRARY_PATH=c['library_path'],OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',HIP_VISIBLE_DEVICES='',CUDA_VISIBLE_DEVICES='')
 tools='/archive/selected-read-trace-tools-v1'
 argv=[tools+'/ld-linux-x86-64.so.2','--library-path',tools,tools+'/strace','-ff','-yy','-s','4096','-o',str(o/'trace'),'-e','trace=%file,read,pread64,mmap',c['binary'],'-s',c['mesh'],'-v',str(view),'-g','0','--scale','1','-n','27','--slice-step','1','--surface-interpolation','linear','--zarr-output',str(o/'render.zarr'),'--cache-gb','1']
 started=time.monotonic()
 with (o/'renderer.log').open('wb') as log:r=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
 # Audit all syscall paths: successful chunk opens must correspond one-for-one to
 # verified owned buffers. All CT mmap/pread and non-G0 chunk reads are forbidden.
 from trace_qualification import reconcile
 traces=list(o.glob('trace.*'));assert traces
 mains=[f for f in traces if 'execve("'+c['binary']+'"' in f.read_text()]
 assert len(mains)==1 and mains[0].read_text().rstrip().endswith('+++ exited with 0 +++'),'exact renderer exit trace'
 present,absence,loaded,ctcalls=reconcile(traces,volume,c['pins'],json.loads(manifest.read_text()),c['metadata_absent'],view)
 assert r.returncode==0,'renderer failed'
 assert str(pathlib.Path(c['guarded_library']).resolve()) in loaded and ctcalls>0,'guard library mapping/CT trace missing'
 traced=present+list(absence.elements())
 evidence=audit(manifest,mh,o/'events.jsonl',view,env,traced)
 actual=tree(o/'render.zarr');expected=tree(pathlib.Path(c['reference']))
 assert actual and actual==expected,'render output tree mismatch'
 report={'status':'QUALIFICATION_EXACT_REFERENCE_AND_READ_COVERAGE_PASS','wall_seconds':time.monotonic()-started,'renderer_rc':r.returncode,'ledger':evidence,'output_files':len(actual),'output_hashes':actual,'manifest_sha256':mh,'canonical_view_zero':str((view/'0').resolve()),'applied_env':{k:env[k] for k in env if k.startswith('VC_VERIFIED_')},'scope':'Single retained crop qualification; no performance/promotion claim; production unchanged.'}
 (o/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()

