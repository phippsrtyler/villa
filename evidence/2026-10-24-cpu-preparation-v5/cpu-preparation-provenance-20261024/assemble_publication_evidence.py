"""Read-only evidence hashing and pinned-script-derived command reconstruction."""
import hashlib, json, pathlib, shlex

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(__file__).resolve().parent
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()
def write(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8')

src = ROOT/'scheduler/selected-read-integrity-v2-candidate/failclosed-v3-repair-v1/failclosed-v5-qualification-v1/build_and_test_failclosed_v5.py'
provpath = OUT/'selected-read-integrity-v3-source__build-provenance.json'
prov = json.loads(provpath.read_text())
r='/mnt/oldpc/vesuvius_park'
s=r+'/selected-read-integrity-v3-source'
c=r+'/selected-read-upstream-failclosed-v5-source'
o=r+'/selected-read-upstream-failclosed-v5-cpu-qualification'
libs=r+'/production-renderer-library-restore-v5/science/lib'
original=shlex.split(prov['original_compile_command']['command'])
flags=[x.replace('-flto=auto','-flto=2').replace('/work/flatboi_build/src_pr/volume-cartographer/utils/include',s+'/source-snapshot/include').replace('/work/flatboi_build/','/mnt/scrolls/vesuvius/flatboi_build/') for x in original[1:original.index('-o')]]
commands=[['/usr/bin/g++','-I'+s+'/compile-include','-I'+s,*flags,'-c',c+'/volume-cartographer/utils/src/zarr.cpp','-o',o+'/zarr-candidate.o'], ['/usr/bin/g++','-shared','-flto=2','-Wl,--gc-sections','-Wl,--as-needed','-Wl,-soname,libutils.so',o+'/zarr-candidate.o',*prov['retained_objects'],'-L'+libs,'-Wl,-rpath,'+libs,*['-Wl,-l:'+x for x in ['libQt6Core.so.6','libcurl.so.4','libz.so.1','libzstd.so.1','liblz4.so.1','libcrypto.so.3']],'-o',o+'/libutils.so'], ['cmake','-S',o+'/cmake-source','-B',o+'/build','-DCMAKE_BUILD_TYPE=Release'],['cmake','--build',o+'/build','--target','test_verified_ct_read','-j2'],['ctest','--test-dir',o+'/build','-R','verified_ct_read','--output-on-failure']]
write('compile-link-provenance.json', {'schema':'publication-build-provenance-v1','base_commit':'417e17689029434fa1572efe20a3e7a9bfc79be4','library_sha256':'e4287923b8468a157eba6895d82c17a2f00105eeda32a6c9ec6755673b52231d','command_evidence_scope':'Commands reconstructed mechanically from pinned build script and retained provenance; not a newly executed build or complete command execution transcript.','build_script':{'path':str(src.relative_to(ROOT)),'sha256':sha(src)},'original_provenance_sha256':sha(provpath),'original_compile_command':prov['original_compile_command'],'commands':commands,'environment':{'TMPDIR':o,'LD_LIBRARY_PATH':o+':'+libs},'retained_objects':{p:prov['source_snapshot_pins'][p] for p in prov['retained_objects']},'limitations':['Retained project objects were linked; full clean repository build was not demonstrated.','Focused CMake public API fixture imports the resulting libutils; it is not the full repository build.','Original wrapper exited 1 after successful CTest due report-processing bug; preserved postcheck validates existing outputs only.']})
paths=list(OUT.rglob('*'))
paths=[p for p in paths if p.is_file() and p.name not in {'publication-evidence-manifest.json','assemble_publication_evidence.py'}]
paths += [src,ROOT/'CPU_PREPARATION_V5_FINAL_PUBLICATION_AUDIT.md',ROOT/'scheduler/selected-read-integrity-v2-candidate/failclosed-v3-repair-v1/selected-read-cpu-final-v5-review.patch',ROOT/'scheduler/selected-read-integrity-v2-candidate/v5-production-two-full-chains.json',ROOT/'scheduler/selected-read-integrity-v2-candidate/v5-production-native-verification-v2.json']
paths += list((ROOT/'scheduler/selected-read-integrity-v2-candidate/failclosed-v5-final-source-cpu-benchmark-v3/terminal-evidence').glob('*'))
entries=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(paths)) if p.is_file()]
post=json.loads((OUT/'v5-postcheck/verification.json').read_text())
assert sha(OUT/'v5-native/build-and-test.log')==post['input_sha256']['build_log']
assert sha(OUT/'v5-native/integrated-fixture-report.json')==post['input_sha256']['fixture_report']
assert json.loads((OUT/'v5-native/receipt.json').read_text())['returncode']==1
write('publication-evidence-manifest.json',{'schema':'cpu-preparation-publication-evidence-v1','scope':'CPU preparation only; no GPU, sustained production, ink readability, or universal full-pipeline speed claim. Historical evidence remains unchanged.','original_build_wrapper':'FAILED rc1, retained explicitly','preserved_ctest':'35 cases passed; later read-only postcheck succeeded, no rebuild','clean_full_build_proved':False,'entries':entries})
print(json.dumps({'files':len(entries),'manifest_sha256':sha(OUT/'publication-evidence-manifest.json'),'compile_link_sha256':sha(OUT/'compile-link-provenance.json')}))
