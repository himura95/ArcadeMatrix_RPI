import gzip, time

path = '/Users/red1l/Documents/work/git/perso/ArcadeMatrix_RPi/fighters_64/kfm/walk.fgt.gz'
t0 = time.time()
with gzip.open(path, 'rb') as f:
    data = f.read()
print("GZIP read time:", time.time() - t0)
