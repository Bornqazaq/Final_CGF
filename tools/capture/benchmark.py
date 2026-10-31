"""Reproducible, uncapped 1280x720 gameplay benchmark with raw frame times."""
from pathlib import Path
import subprocess,time,ctypes,csv,json,math,statistics
from ctypes import wintypes
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidence/benchmarks';OUT.mkdir(exist_ok=True)
class Counters(ctypes.Structure):
 _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage']]
kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True)
kernel.OpenProcess.restype=wintypes.HANDLE;kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
kernel.CloseHandle.argtypes=[wintypes.HANDLE]
psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
results=[]
for run in range(1,4):
 with (OUT/f'run-{run}.log').open('w') as log:
  game=subprocess.Popen([str(ROOT/'build/LaserVaultHeist.exe'),'--root',str(ROOT),'--auto-route','--seconds','65'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  handle=kernel.OpenProcess(0x410,False,game.pid);peak=private=0
  while game.poll() is None:
   counters=Counters();counters.cb=ctypes.sizeof(counters)
   if handle and psapi.GetProcessMemoryInfo(handle,ctypes.byref(counters),ctypes.sizeof(counters)):
    peak=max(peak,counters.PeakWorkingSetSize);private=max(private,counters.PrivateUsage)
   time.sleep(.25)
  if handle:kernel.CloseHandle(handle)
  if game.returncode:raise RuntimeError(f'Benchmark {run} failed')
 raw=(ROOT/'evidence/frame-times.csv').read_bytes();(OUT/f'run-{run}.csv').write_bytes(raw)
 rows=list(csv.DictReader(raw.decode().splitlines()))
 # First five seconds of the measured loop are warmup; initialization is excluded.
 start=float(rows[0]['seconds']);values=[float(x['frame_ms']) for x in rows if float(x['seconds'])-start>=5]
 ordered=sorted(values)
 def pct(p):return ordered[min(len(ordered)-1,math.ceil(p*len(ordered))-1)]
 worst=ordered[-max(1,math.ceil(.01*len(ordered))):]
 result={'run':run,'frames':len(values),'measured_seconds':sum(values)/1000,'average_fps':1000/statistics.mean(values),'p50_ms':pct(.5),'p95_ms':pct(.95),'p99_ms':pct(.99),'one_percent_low_fps':1000/statistics.mean(worst),'minimum_frame_fps':1000/max(values),'peak_working_set_mib':peak/1048576,'peak_private_mib':private/1048576}
 results.append(result);print(json.dumps(result),flush=True)
summary={'resolution':[1280,720],'vsync':False,'frame_limit':None,'window_visible':True,'capture':False,'scenario':'Repeated legal crouch routes, live CCTV, moving lasers/spotlights, safe opening and retry','warmup_seconds':5,'requested_seconds_per_run':65,'one_percent_low_definition':'1000 / mean of the slowest 1% of frame times in milliseconds','timing_scope':'Complete frame-loop wall time, including simulation, draw submission, UI, CSV logging and presentation; not isolated GPU timer queries','runs':results,'ta_hardware':'Not supplied or tested'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
print('All three benchmark runs completed')
