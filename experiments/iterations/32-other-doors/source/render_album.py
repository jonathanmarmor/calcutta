"""Render independently in separate processes, keeping memory bounded."""
import subprocess,concurrent.futures,sys
numbers=[int(x) for x in sys.argv[1:]] or list(range(1,13))
def run(k):subprocess.run([sys.executable,'render_doors.py',str(k)],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,numbers))
