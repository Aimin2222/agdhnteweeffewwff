import sys,threading,gc,traceback,faulthandler
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import legacy_app
faulthandler.enable(sys.stderr,all_threads=True)
main=threading.get_ident()
def track(phase,info):
 if threading.get_ident()!=main:
  print('OFF-MAIN GC',phase,threading.current_thread().name,info,file=sys.stderr,flush=True)
  if phase=='start':traceback.print_stack(file=sys.stderr)
gc.callbacks.append(track)
import pytest
raise SystemExit(pytest.main(['tests','-v','--junitxml=autocine-v51021-pytest.xml']))
