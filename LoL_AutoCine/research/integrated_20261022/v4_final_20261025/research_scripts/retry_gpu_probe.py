from lab_common import *
import sys,os,importlib
sys.dont_write_bytecode=True
os.environ['TMP']=str((W/'tmp').resolve());os.environ['TEMP']=os.environ['TMP']
sys.path.insert(0,str((OLD/'source_readonly/LoL_AutoCine').resolve()))
rows=[]
try:
 g=importlib.import_module('core.gpu_full');ok,msg=g.full_runtime_probe(FF);rows.append({'probe':'unchanged GPUFullStage','success':ok,'detail':msg})
except Exception as e:rows.append({'probe':'unchanged GPUFullStage','success':False,'detail':type(e).__name__+': '+str(e)})
r=ff(['-init_hw_device','opencl=ocl:,device_type=gpu','-filter_hw_device','ocl','-f','lavfi','-i','color=c=blue:s=64x64:r=30:d=0.2','-vf','format=rgba,hwupload,avgblur_opencl=sizeX=3:sizeY=3,hwdownload,format=rgba','-frames:v','3','-f','null','-']);rows.append({'probe':'independent FFmpeg OpenCL avgblur','success':not r.returncode,'return_code':r.returncode,'detail':r.stderr.decode(errors='replace')})
save('GPU_RETRY_ALTERNATIVE_V4.json',{'reason':'Sandbox OpenCL device initialization failed -12; retry outside managed sandbox without changing driver/settings','probes':rows,'LoL_or_all_FX_pass':False});print(json.dumps(rows))
