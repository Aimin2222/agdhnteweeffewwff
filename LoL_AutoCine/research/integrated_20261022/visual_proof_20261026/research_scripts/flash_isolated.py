from common import *
import itertools
rows=[]
for fps,rate,event in itertools.product([F(30),F(60),F(60000,1001)],[F(1),F(1,2)],[F('0.1004'),F('0.1084'),F('0.3002'),F('0.5004')]):
 t=event/rate;N=math.ceil((t+F(1,5))*fps);a=np.full((N,48,64,3),80,np.uint8)
 base=ff(['-f','rawvideo','-pix_fmt','rgb24','-s','64x48','-r',str(fps),'-i','pipe:0','-vf','eq=brightness=0:eval=frame','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],a.tobytes());base=np.frombuffer(base,np.uint8).reshape(a.shape)
 graph=f"eq=brightness='if(gte(n,{math.ceil(t*fps)}),0.278*exp(-18*abs(t-{float(t):.12f})),0)':eval=frame"
 b=ff(['-f','rawvideo','-pix_fmt','rgb24','-s','64x48','-r',str(fps),'-i','pipe:0','-vf',graph,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],a.tobytes());b=np.frombuffer(b,np.uint8).reshape(a.shape);d=np.abs(b.astype(int)-base.astype(int)).max((1,2,3));pre=[n for n in range(N) if F(n)/fps<t];changed=np.flatnonzero(d>0)
 rows.append({'fps':str(fps),'replay_rate':str(rate),'replay_event':str(event),'output_event':str(t),'expected_onset':math.ceil(t*fps),'actual_onset':int(changed[0]),'pre_event_max_rgb_delta':int(d[pre].max()),'status':'PASS' if d[pre].max()==0 and changed[0]==math.ceil(t*fps) else 'FAIL','graph':graph})
save('FLASH_ISOLATED_EVENTS.json',{'cases':rows,'scope':'24 isolated V5 event terms, actual CPU RGB rendering; causal term gating at every unique event time; no enable-window/stacks; original compound tests remain FLASH_RESULTS.json'})
print('isolated events',len(rows),'pass',sum(x['status']=='PASS' for x in rows))
