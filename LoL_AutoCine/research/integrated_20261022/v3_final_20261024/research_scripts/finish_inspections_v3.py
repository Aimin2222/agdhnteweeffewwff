from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib, itertools
import numpy as np
R=Path(__file__).resolve().parents[2];W=R/'work/autocine_integrated_research_20261022';O=R/'outputs/autocine_final_research_v3_20261024'
def load(p):return json.loads(p.read_text('utf-8-sig'))
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',15)
q=load(R/'outputs/autocine_integrated_research_v2_20261022/ASSET_FULL_QA_V2.json')['items']
orig=load(O/'ORIGINAL_89_PROTECTION_MAPPING_V3.json');inv=load(W/'source_ledger_cache_v3/original_alpha/review_v1/upstream_evidence/source_inventory.json')
originals={x['number']:x for x in orig['files']};sources={f"{x['index']:03}":x for x in inv['sources']}
base=Path('${READONLY_ORIGINAL_REPOSITORY}')
edges=[x for x in q if x['flags']];pages=[]
for start in range(0,len(edges),8):
    rows=edges[start:start+8];sheet=Image.new('RGB',(1600,1600),'#e6eaf0');d=ImageDraw.Draw(sheet)
    for i,a in enumerate(rows):
        num=a['number'];comp=next(x for x in sources[num]['components'] if x['id']==a['id'].split('/',1)[1]);y=i*200
        d.text((10,y+2),a['id']+'  SOURCE CROP | EXTRACTED CANDIDATE',font=font,fill='#172638')
        with Image.open(base/originals[num]['path']) as im:crop=im.crop(comp['crop_box']).convert('RGBA')
        with Image.open(W/'asset_samples'/a['path']) as im:candidate=im.convert('RGBA')
        for j,img in enumerate([crop,candidate]):
            img.thumbnail((780,170),Image.Resampling.LANCZOS);tile=Image.new('RGBA',(780,170),'#202936');tile.alpha_composite(img,((780-img.width)//2,(170-img.height)//2));sheet.paste(tile.convert('RGB'),(10+j*800,y+25))
    name=f'SOURCE_EDGE_COMPARE_{start//8+1:02}.jpg';sheet.save(O/name,quality=91);pages.append({'file':name,'ids':[x['id'] for x in rows],'viewed':False})
(O/'SOURCE_EDGE_COMPARE_LOG_V3.json').write_text(json.dumps({'scope':'scaled source crop vs scaled extracted full candidate; native edge patches separate; not native fidelity approval','pages':pages},indent=2),'utf-8')
badges=sorted((W/'legacy_asset_cache_v3/LoL_AutoCine/assets/kill_badges').glob('*.png'))
for start in range(0,len(badges),20):
    sheet=Image.new('RGB',(1600,1250),'#e6eaf0');d=ImageDraw.Draw(sheet)
    for i,p in enumerate(badges[start:start+20]):
        x=i%4*400;y=i//4*250;d.text((x+4,y+2),p.stem,font=font,fill='#172638')
        with Image.open(p) as im:im=im.convert('RGBA');im.thumbnail((390,105),Image.Resampling.LANCZOS)
        for j,col in enumerate(['#f6f7f8','#202936']):
            tile=Image.new('RGBA',(390,105),col);tile.alpha_composite(im,((390-im.width)//2,(105-im.height)//2));sheet.paste(tile.convert('RGB'),(x+4,y+30+j*108))
    sheet.save(O/f'LEGACY_BADGES_{start//20+1:02}.jpg',quality=91)
# alpha dHash is an intentionally weak shape-similarity triage only, not duplicate proof.
pairs=[]
for a,b in itertools.combinations([x for x in q if x['kind']=='frame'],2):
    h=(int(a['alpha_dhash'],16)^int(b['alpha_dhash'],16)).bit_count()
    if h<=5:pairs.append({'a':a['id'],'b':b['id'],'alpha_dhash_hamming':h,'same_number':a['number']==b['number'],'same_theme':a['theme']==b['theme'],'decision':'human review; retain both; no merge/delete/approval'})
pairs.sort(key=lambda x:(x['alpha_dhash_hamming'],x['same_number'],x['a'],x['b']))
(O/'SIMILARITY_TRIAGE_V3.json').write_text(json.dumps({'method':'64-bit alpha silhouette dHash only; ignores color; high false-positive risk for shared layouts','threshold':5,'pairs':pairs,'exact_sha256_duplicates':0,'automatic_decisions':False},indent=2),'utf-8')
# Proposed warning engine, artificial arrays only: not product QA implementation.
cases=[]
def trial(name,frames,meta,expected):
    arr=np.asarray(frames,dtype=np.float32);luma=arr.mean(axis=(1,2,3));delta=np.abs(np.diff(arr,axis=0)).mean(axis=(1,2,3));warnings=[]
    if sum(luma<5)>=30 and not meta.get('intentional_black'):warnings.append('BLACK_OR_CAPTURE_EMPTY')
    if len(delta)>=59 and np.max(delta)<.1 and meta.get('expected_motion'):warnings.append('POSSIBLE_FREEZE')
    if meta.get('audio_expected') and not meta.get('audio_stream'):warnings.append('MISSING_AUDIO_STREAM')
    if meta.get('audio_expected') and meta.get('audio_stream') and meta.get('rms',1)<.0001:warnings.append('POSSIBLE_SILENCE')
    if meta.get('expected_frames') is not None and meta['decoded_frames']<meta['expected_frames']:warnings.append('FRAME_COUNT_MISMATCH')
    if meta.get('event_offset_ms',0)>50:warnings.append('EVENT_SYNC_REVIEW')
    if meta.get('safe_area_breach') and not meta.get('entrance_interval'):warnings.append('OVERLAY_CLIP_REVIEW')
    cases.append({'id':name,'context':meta,'warnings':warnings,'expected':expected,'fixture_expectation_met':warnings==expected,'scope':'proposed isolated array/metadata rules; no LoL validation'})
black=np.zeros((60,32,48,3),np.uint8);gray=np.full_like(black,90);red=gray.copy();red[:,:,:,0]=200
move=np.stack([np.full((32,48,3),40+i,np.uint8) for i in range(60)])
trial('Q01_black_capture',black,{},['BLACK_OR_CAPTURE_EMPTY'])
trial('Q02_intentional_black',black,{'intentional_black':True},[])
trial('Q03_gray_death',gray,{'death_event':True},[])
trial('Q04_low_hp_red',red,{'low_hp':True},[])
trial('Q05_teleport_bright',np.full_like(black,245),{'teleport':True},[])
trial('Q06_freeze_expected_motion',gray,{'expected_motion':True},['POSSIBLE_FREEZE'])
trial('Q07_intentional_still',gray,{},[])
trial('Q08_audio_missing',move,{'audio_expected':True,'audio_stream':False},['MISSING_AUDIO_STREAM'])
trial('Q09_audio_optional',move,{'audio_expected':False,'audio_stream':False},[])
trial('Q10_audio_silence',move,{'audio_expected':True,'audio_stream':True,'rms':0},['POSSIBLE_SILENCE'])
trial('Q11_dropped_count',move,{'expected_frames':120,'decoded_frames':117},['FRAME_COUNT_MISMATCH'])
trial('Q12_sync_anchor',move,{'event_offset_ms':90},['EVENT_SYNC_REVIEW'])
trial('Q13_slide_intended_clip',move,{'safe_area_breach':True,'entrance_interval':True},[])
trial('Q14_static_overlay_clip',move,{'safe_area_breach':True},['OVERLAY_CLIP_REVIEW'])
(O/'WARNING_QA_SYNTHETIC_V3.json').write_text(json.dumps({'cases':cases,'executed':len(cases),'fixture_expectations_met':sum(c['fixture_expectation_met'] for c in cases),'claims':'14 designed fixtures only; no empirical LoL false-positive rate; thresholds proposals; warning only; no automatic repair or blocking'},indent=2),'utf-8')
print(json.dumps({'source_compare_pages':len(pages),'legacy_badges':len(badges),'similarity_pairs':len(pairs),'warning_cases':len(cases)}))
