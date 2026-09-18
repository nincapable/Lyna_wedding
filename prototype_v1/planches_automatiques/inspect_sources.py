import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tmp/pdf-deps'))
from PIL import Image,ImageChops,ImageStat
data=json.loads((ROOT/'production.json').read_text(encoding='utf-8'))
for i,path in enumerate(data['source_strips'],1):
    im=Image.open(path).convert('L')
    w,h=im.size
    print(i,w,h)
    for fraction in [1/3,2/3]:
        scores=[]
        for y in range(int(h*(fraction-.08)),int(h*(fraction+.08))):
            a=im.crop((0,y,w,y+1))
            b=im.crop((0,y-1,w,y))
            scores.append((ImageStat.Stat(ImageChops.difference(a,b)).mean[0],y))
        print(sorted(scores,reverse=True)[:4])
