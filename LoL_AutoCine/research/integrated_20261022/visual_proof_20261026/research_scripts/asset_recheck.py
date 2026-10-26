from common import *
queue=load(R/'outputs/autocine_implementation_specs_20261026/ASSET_REVIEW_QUEUE.json');notes=load(W/'review_notes.json');ledger=load(O/'ASSET_RENDER_LEDGER.json');by={(x['kind'],x['id']):x for x in ledger['items']};rows=[]
for x in queue['items']:
 p=A/x['path'];h=sha(p)
 with Image.open(p) as im:
  im.load();mode=im.mode;size=im.size;a=np.asarray(im.convert('RGBA'));alpha=a[:,:,3];edge=np.concatenate([alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
 r={'kind':x['kind'],'id':x['id'],'priority':x['priority'],'source_sha256':h,'hash_matches_queue':h==x['source_sha256'],'size':size,'source_mode':mode,'alpha_min':int(alpha.min()),'alpha_max':int(alpha.max()),'partial_alpha_pixels':int(((alpha>0)&(alpha<255)).sum()),'opaque_edge_pixels':int((edge==255).sum()),'partial_edge_pixels':int(((edge>0)&(edge<255)).sum()),'alpha_zero_rgb_nonzero_pixels':int(((alpha==0)&(a[:,:,:3].max(2)>0)).sum()),'catalog_status_unchanged':x['catalog_status_unchanged'],'mechanical_status':'PASS' if h==x['source_sha256'] and alpha.min()==0 and alpha.max()>0 else 'FAIL','formal_approval_changed':False}
 if (x['kind'],x['id']) in by:
  b=by[(x['kind'],x['id'])];r.update({'sheet':b['sheet'],'AI_image_visual_status':'REVIEW','AI_image_observation':notes['observations'][str(b['sequence'])],'derivation_source_available':b['derivation_source_available'],'derivation_source_identical_hash':b['derivation_source_identical_hash'],'master_available':b['master_available']})
 else:r.update({'AI_image_visual_status':'NOT_RUN','reason':'P2 new image review not performed in this delivery; prior records retained separately'})
 rows.append(r)
assert len(rows)==687;assert all(x['hash_matches_queue'] for x in rows)
save('ASSET_687_RECHECK.json',{'items':rows,'new_decode_hash_checks':687,'new_AI_image_reviews':140,'new_P0_reviews':50,'new_P1_reviews':90,'new_P2_reviews':0,'formal_approval_changes':0,'visual_scope':notes['scope'],'limitations':['synthetic backgrounds, 2 stacked rows, 4 motion snapshots at elapsed .13 seconds per asset','not all native pixels inspected; targeted edge crops and scaled overview','FX only tested with baseline083; no full 652x35 compatibility','no complete temporal human review; no live LoL/HUD background','89 context thumbnail cannot certify original theme fidelity or repair incomplete originals'],'mechanical_criteria':'hash equals pinned queue; decode; dimensions >0; alpha zero and nonzero present. Edge touches are flags, not automatic failure. No visual approval implied.'})
print('assets 687 rechecked; AI review 140; mechanical pass',sum(x['mechanical_status']=='PASS' for x in rows))
