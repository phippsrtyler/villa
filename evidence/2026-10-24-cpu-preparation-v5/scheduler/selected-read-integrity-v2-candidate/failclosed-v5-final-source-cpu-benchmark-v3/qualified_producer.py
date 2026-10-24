"""One distinct new-band render, using original crop semantics and exact original C++ renderer."""
import argparse,hashlib,json,math,os,pathlib,subprocess,time
import numpy as np,tifffile

def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def inside(p):
 p=str(p);need(p.startswith('/mnt/oldpc/vesuvius_park/'),'exact archive host path');return pathlib.Path('/archive')/p.removeprefix('/mnt/oldpc/vesuvius_park/')
def render_shape(grid,scale):
 need(len(scale)==2 and all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in scale),'finite positive original gridscale');return [27,max(1,math.floor(grid[0]/scale[1]+.5)),max(1,math.floor(grid[1]/scale[0]+.5))]
def emit(p,j):p.write_text(json.dumps(j,indent=2))
def crop_arrays(x,y,z,window):
 need(x.shape==y.shape==z.shape and x.ndim==2 and np.isfinite(x).all() and np.isfinite(y).all() and np.isfinite(z).all(),'finite matching XYZ grids')
 mask=(z>=window[0])&(z<window[1])&(x>0)
 if mask.sum()<100:return None
 rr=np.where(mask.any(1))[0];cc=np.where(mask.any(0))[0];sl=(slice(rr[0],rr[-1]+1),slice(cc[0],cc[-1]+1));cropped=[]
 for a in [x,y,z]:
  q=a.copy();q[~mask]=-1;cropped.append(q[sl])
 return cropped,mask[sl],np.stack([a[mask] for a in [x,y,z]],axis=1),int((x>0).sum())
def main():
 if not __debug__:raise RuntimeError('assertions required')
 started_all=time.monotonic()
 p=argparse.ArgumentParser();p.add_argument('--contract',required=True);p.add_argument('--sha256',required=True);a=p.parse_args();need(sha(a.contract)==a.sha256,'contract pin');c=json.loads(pathlib.Path(a.contract).read_text());out=pathlib.Path(c['output_root']);need(out.resolve().is_relative_to(pathlib.Path('/archive')),'archive only');out.mkdir(exist_ok=False)
 need(sha(c['fit_receipt'])==c['fit_receipt_sha256'],'exact successful newfit');fit=json.loads(pathlib.Path(c['fit_receipt']).read_text());need(fit['status']=='PASS_STOCK_FIT_ARTIFACTS','successful fit artifacts');need(sha(c['ct_validation'])==c['ct_validation_sha256'],'exact CT validation proof');ct=json.loads(pathlib.Path(c['ct_validation']).read_text());need(ct['status']=='PASS_EXPLICIT_SPARSE_GEOMETRY_CT_RESTORE_ALL_PRESENT_BYTES' and ct['contract_sha256']==c['ct_producer_contract_sha256'] and ct['footprint_sha256']==c['footprint_sha256'] and ct['sparse_fill_value']==0,'exact successful sparse-zero CT producer');ctroot=pathlib.Path(c['ct_validation']).parent;need(sha(ctroot/'manifest.json')==ct['manifest_sha256'] and sha(ctroot/'receipts.jsonl')==ct['receipts_sha256'] and sha(ctroot/'source-absent-key-ledger.json')==ct['absent_ledger_sha256'],'complete CT receipts');need(sha(ctroot/'complete-selected-prefix-listing.json')==ct['complete_listing_sha256'],'complete source listing proof');manifest=json.loads((ctroot/'manifest.json').read_text());need(all(r['key'] not in set(manifest['missing_required_keys']) for r in manifest['objects']),'present absent partition')
 receipts=[json.loads(line) for line in (ctroot/'receipts.jsonl').read_text().splitlines()];need(len(receipts)==c['expected_present_count'] and len({r['key'] for r in receipts})==c['expected_present_count'] and {r['key'] for r in receipts}=={r['key'] for r in manifest['objects']} and len(manifest['missing_required_keys'])==c['expected_absent_count'],'complete exact restored sparse partition');data_root=inside(ct['data_root']);volume_root=inside(ct['volume_root']);need(set(c['ct_metadata_pins'])=={'.zattrs','.zgroup','0/.zarray'},'all metadata pins');
 for rel,h in c['ct_metadata_pins'].items():need(sha(volume_root/rel)==h and manifest['metadata'][manifest['source_prefix']+rel]['sha256']==h,'actual restored metadata and source manifest pin')
 selected_read=c.get('selected_read_verified')
 need(selected_read is None or type(selected_read) is dict,'explicit selected-read contract schema')
 if selected_read is not None:
  need(set(selected_read)=={'manifest','manifest_sha256','library_root','library_file','library_sha256','audit_source_sha256'},'closed selected-read contract')
  need(sha(pathlib.Path(__file__).parent/'audit_qualification_ledger.py')==selected_read['audit_source_sha256'],'pinned ledger audit source')
  need(sha(selected_read['library_file'])==selected_read['library_sha256'],'qualified selected-read library bytes')
  need(selected_read['library_root']==str(pathlib.Path(selected_read['library_file']).parent)+':'+c['library_root'],'closed selected-read loader search path')
  need(not (out/'selected-read-events.jsonl').exists(),'fresh owned selected-read ledger')
  os.environ.update(VC_VERIFIED_CT_MANIFEST=selected_read['manifest'],VC_VERIFIED_CT_MANIFEST_SHA256=selected_read['manifest_sha256'],VC_VERIFIED_CT_LEDGER=str(out/'selected-read-events.jsonl'))
 if selected_read is None:
  for r in receipts:
   q=data_root/r['key'];need(q.is_file() and q.stat().st_size==r['bytes'] and sha(q)==r['sha256'],'all restored CT bytepins')
  for k in manifest['missing_required_keys']:need(not (data_root/k).exists(),'source-absent chunks remain absent')
 else:
  # Explicit contract opt-in; immutable complete partition remains checked.
  need(os.environ.get('VC_VERIFIED_CT_MANIFEST') and os.environ.get('VC_VERIFIED_CT_MANIFEST_SHA256') and os.environ.get('VC_VERIFIED_CT_LEDGER'),'selected-read environment mandatory')
  need(sha(os.environ['VC_VERIFIED_CT_MANIFEST'])==os.environ['VC_VERIFIED_CT_MANIFEST_SHA256'],'selected-read manifest pin')
  guarded=json.loads(pathlib.Path(os.environ['VC_VERIFIED_CT_MANIFEST']).read_text())
  need(pathlib.Path(guarded['volume_root']).resolve()==volume_root.resolve(),'selected-read volume binding')
  expected={r['key'].removeprefix(manifest['source_prefix']+'0/'):(False,r['bytes'],r['sha256']) for r in receipts}
  expected.update({k.removeprefix(manifest['source_prefix']+'0/'):(True,0,'') for k in manifest['missing_required_keys']})
  need({r['key']:(r['absent'],r['bytes'],r['sha256']) for r in guarded['objects']}==expected,'complete selected manifest records')
 need(sha(c['ct_view_qualification'])==c['ct_view_qualification_sha256'],'exact independent retained metadata-view proof bytes');viewproof=json.loads(pathlib.Path(c['ct_view_qualification']).read_text());need(viewproof['status']=='PASS_EXACT_SOURCE_METADATA_VIEW_ACTUAL_G0_READER' and viewproof['contract_sha256']==c['ct_view_producer_contract_sha256'],'successful exact source metadata view reader qualification');view=pathlib.Path(viewproof['view_root']);need(view.resolve().is_relative_to(pathlib.Path('/archive')) and (view/'0').is_symlink() and (view/'0').resolve()==(volume_root/'0').resolve(),'exact sole view G0target');need([p for p in view.rglob('*') if p.is_symlink()]==[view/'0'],'no other view symlinks');need(viewproof['advertised_levels']==list(map(str,range(6))),'exact advertised levels');
 for rel,r in viewproof['metadata'].items():need(sha(view/rel)==r['sha256'],'exact source all-level metadata bytes')
 for rel,h in c['ct_metadata_pins'].items():need(sha(view/rel)==h,'view original metadata unmodified')
 need(sha(c['library_receipt'])==c['library_receipt_sha256'] and sha(c['binary'])==c['binary_sha256'],'exact qualified renderer');lib=json.loads(pathlib.Path(c['library_receipt']).read_text());need(all(sha(pathlib.Path(c['library_root'])/r['name'])==r['sha256'] for r in lib['libraries']),'full closure pins');catalog=[];seen=set();selected=None;need([r['path'] for r in c['unique_meshes']]==sorted(r['path'] for r in c['unique_meshes']),'frozen deterministic source order')
 for row in c['unique_meshes']:
  identity=tuple(row['coordinates'][k+'.tif'] for k in 'xyz');need(identity not in seen,'no duplicated XYZ triples');seen.add(identity);src=pathlib.Path(row['path']);need(all(sha(src/(k+'.tif'))==row['coordinates'][k+'.tif'] for k in 'xyz') and sha(src/'meta.json')==row['meta_sha256'],'exact geometry coordinate/meta pins');arrays=[tifffile.imread(src/(k+'.tif')).astype(np.float32) for k in 'xyz'];result=crop_arrays(*arrays,c['window'])
  if result is None:continue
  cropped,mask,points,source_valid=result;meta=json.loads((src/'meta.json').read_text());scale=meta['scale'];need(len(scale)==2 and all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in scale),'finite positive original gridscale');shape=render_shape(cropped[0].shape,scale);height,width=shape[1:];recipe={'geometry_sha256':list(identity),'geometry_meta_sha256':row['meta_sha256'],'window':c['window'],'render_options':c['render_options'],'ct_metadata_pins':c['ct_metadata_pins'],'renderer_sha256':c['binary_sha256']};workkey=hashlib.sha256(json.dumps(recipe,sort_keys=True,separators=(',',':')).encode()).hexdigest();entry={'work_key':workkey,'source_path':str(src),'aliases':row['aliases'],'crop_grid_shape':list(mask.shape),'valid_crop_points':int(mask.sum()),'expected_shape':[27,height,width],'resource_eligible':height*width<=c['max_pixels'],'geometry_sha256':list(identity)};catalog.append(entry)
  if selected is None and entry['resource_eligible'] and entry['work_key']==c['selected_work_key']:
   mesh=out/'mesh';mesh.mkdir()
   for k,v in zip('xyz',cropped):tifffile.imwrite(mesh/(k+'.tif'),v)
   meta['bbox']=[points.min(0).tolist(),points.max(0).tolist()];meta['area_cm2']=round(meta.get('area_cm2',0)*mask.sum()/max(source_valid,1),3);meta['uuid']=src.name;emit(mesh/'meta.json',meta);selected=entry
 need(sha(c['finite_catalog'])==c['finite_catalog_sha256'],'exact approved finite120 catalog bytes');finite=json.loads(pathlib.Path(c['finite_catalog']).read_text());need(catalog==finite['entries'],'all120 recomputed crop identities/shapes match actual first qualified catalog');need(len(seen)==c['expected_unique_geometry_count'] and selected is not None,'exact selected key among120unique eligible surfaces');emit(out/'unique-crop-catalog.json',{'window':c['window'],'unique_geometry_count':len(seen),'eligible_crop_count':len(catalog),'selection':'Exact frozen finite-catalog work_key; no CT-driven or image-driven selection.','entries':catalog,'selected_work_key':selected['work_key']})
 need(c['render_options']=={'group':0,'scale':1,'depth':27,'slice_step':1,'geometry_interpolation':'linear','voxel_sampling':'trilinear','cache_gb':1,'threads':2,'window':c['window'],'source_voxel_size_um':c['source_voxel_size_um'],'source_undefined_chunks':'explicit_source_zero_fill_only','renderer_options_no_affine_or_rotation':True},'frozen scientific options exactly match actual invocation');env={k:v for k,v in os.environ.items() if selected_read is not None or not k.startswith('VC_VERIFIED_')};env.update(LD_LIBRARY_PATH=selected_read['library_root'] if selected_read is not None else c['library_root'],OMP_NUM_THREADS='2');render=out/'render.zarr';argv=[c['binary'],'-s',str(out/'mesh'),'-v',str(view),'-g','0','--scale','1','-n','27','--slice-step','1','--surface-interpolation','linear','--zarr-output',str(render),'--cache-gb','1']
 started=time.monotonic()
 with (out/'renderer.log').open('wb') as log:r=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT)
 render_seconds=time.monotonic()-started
 selected_read_evidence=None
 if selected_read is not None:
  from audit_qualification_ledger import ledger_only
  selected_read_evidence=ledger_only(selected_read['manifest'],selected_read['manifest_sha256'],out/'selected-read-events.jsonl',str(view),env)
  emit(out/'selected-read-integrity.json',selected_read_evidence)
 need(r.returncode==0,'actual new-band renderer failed');meta=json.loads((render/'0/.zarray').read_text());need(meta['shape']==selected['expected_shape'] and meta['dtype']=='|u1' and meta['zarr_format']==2,'exact actual output shape/dtype/Zarr2');tree={q.relative_to(render).as_posix():sha(q) for q in render.rglob('*') if q.is_file()};need(sum(q.stat().st_size for q in out.rglob('*') if q.is_file())<=c['max_output_bytes'],'bounded owned output')
 receipt={'status':'RENDERED_AWAITING_INDEPENDENT_VALIDATION','source_root':str(render).replace('/archive/','/mnt/oldpc/vesuvius_park/'),'container_source_root':str(render),'work_key':selected['work_key'],'shape':meta['shape'],'dtype':'uint8','zarr_format':2,'full_tree_pins':tree,'source_pins':{'fit_receipt_sha256':c['fit_receipt_sha256'],'ct_validation_sha256':sha(c['ct_validation']),'ct_metadata_view_qualification_sha256':sha(c['ct_view_qualification']),'ct_manifest_sha256':ct['manifest_sha256'],'absent_ct_source_ledger_sha256':ct['absent_ledger_sha256'],'renderer_sha256':c['binary_sha256'],'geometry_sha256':selected['geometry_sha256'],'library_receipt_sha256':c['library_receipt_sha256']},'render_options':c['render_options'],'window':c['window'],'aliases':selected['aliases'],'selected_source':selected['source_path'],'argv':argv,'contract_sha256':a.sha256,'renderer_wall_seconds':render_seconds,'preparation_and_render_wall_seconds':time.monotonic()-started_all,'finite_catalog_sha256':c['finite_catalog_sha256'],'scope':'New fitted-geometry coverage candidate, original27-depth recipe. Source-absent CT chunks are metadata-defined zero, not observed material support. No sheet/ink quality claim.'};from requested_crop_identity_v1 import validate as validate_requested_crop;validate_requested_crop(c,pathlib.Path(c['finite_catalog']).read_bytes(),receipt);emit(out/'render-receipt.json',receipt)
if __name__=='__main__':main()
