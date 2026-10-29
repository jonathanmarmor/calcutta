import subprocess,concurrent.futures,sys
numbers=list(map(int,sys.argv[1:])) or list(range(1,17))
def run(k):subprocess.run([sys.executable,'render_volumes.py',str(k)],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,numbers))
