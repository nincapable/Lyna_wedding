"""Assemble two illustrated automatic-camera contact sheets with vector timestamps."""
import sys,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tmp/pdf-deps'))
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf

DATA=json.loads((ROOT/'production.json').read_text(encoding='utf-8'))
SOURCES=ROOT/'illustrations_sources'
VIEWS=ROOT/'vues'
QA=ROOT/'verification'
EXPORTS=ROOT/'planches_300dpi'
for folder in (SOURCES,VIEWS,QA,EXPORTS):folder.mkdir(exist_ok=True)
# The generated triptychs have slightly unequal panels. Extract inside their seams.
BOUNDS=[
 [(0,589),(594,1180),(1185,1774)],
 [(0,588),(594,1180),(1185,1774)],
 [(0,588),(594,1180),(1185,1774)],
 [(0,566),(572,1076),(1082,1536)],
 [(0,561),(568,1123),(1130,1774)],
 [(0,560),(596,1138),(1147,1774)],
 [(0,560),(596,1138),(1149,1774)],
 [(0,560),(596,1138),(1149,1774)],
]
frames=[]
for index,path in enumerate(DATA['source_strips']):
    dst=SOURCES/f'sequence_{index+1:02d}.png'
    shutil.copy2(path,dst)
    with Image.open(dst) as source:
        w,h=source.size
        for j,(top,bottom) in enumerate(BOUNDS[index]):
            page=index//4
            number=(index%4)*3+j
            time=DATA['times'][page][number]
            filename='MR_'+time.replace(':','')
            target=VIEWS/(filename+'.png')
            # Document panel extraction only: retain original scene pixels and framing.
            source.crop((0,top,w,bottom)).save(target)
            frames.append({'page':page,'number':number,'time':time,'filename':filename,
                           'path':str(target),'pixels':[w,bottom-top]})

CORRECTIONS=json.loads((ROOT/'corrections_format.json').read_text(encoding='utf-8'))
for i,source in enumerate(CORRECTIONS['sources']):
    frame=frames[9+i]
    shutil.copy2(source,frame['path'])
    shutil.copy2(source,SOURCES/f'vue_individuelle_{frame["filename"]}.png')
    with Image.open(frame['path']) as im: frame['pixels']=list(im.size)

for name,filename in [('Body','arial.ttf'),('Bold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+filename))
OUT=ROOT/'planches_prises_de_vue_automatiques.pdf'
C=canvas.Canvas(str(OUT),pagesize=landscape(A4),pageCompression=1)
C.setTitle('MODE AUTO - Planches A et B')
C.setAuthor('')
C.setSubject('MR_184038 - MR_184721')
W,H=landscape(A4)
M=28
GAP=10
CW=(W-2*M-3*GAP)/4
IH=CW/1.5
INK=HexColor('#262b29')
PAPER=HexColor('#f5f4ee')
GREY=HexColor('#666a66')

def text(x,y,s,size=8,font='Body',color=INK):
    C.setFillColor(color)
    C.setFont(font,size)
    C.drawString(x,H-y-size,s)

def right(x,y,s,size=8,font='Body',color=INK):
    C.setFillColor(color)
    C.setFont(font,size)
    C.drawRightString(x,H-y-size,s)

for page in range(2):
    label='AB'[page]
    selected=[f for f in frames if f['page']==page]
    C.setFillColor(PAPER)
    C.rect(0,0,W,H,fill=1,stroke=0)
    text(M,20,'MODE AUTO',19,'Bold')
    text(M+138,27,'PLANCHE '+label,10,'Bold')
    right(W-M,25,selected[0]['filename']+' - '+selected[-1]['filename'],10)
    C.setStrokeColor(HexColor('#93958f'))
    C.setLineWidth(.45)
    C.line(M,H-47,W-M,H-47)
    text(M,53,'horloge interne non synchronisée',8,color=GREY)
    right(W-M,53,'Horodatages : heure enregistrée par le boîtier',8,color=GREY)
    for f in selected:
        row,col=divmod(f['number'],4)
        x=M+col*(CW+GAP)
        y=76+row*162
        iw,ih=f['pixels']
        scale=max(CW/iw,IH/ih)
        dw,dh=iw*scale,ih*scale
        C.setFillColor(HexColor('#262725'))
        C.rect(x,H-y-IH,CW,IH,fill=1,stroke=0)
        C.saveState()
        clip=C.beginPath()
        clip.rect(x,H-y-IH,CW,IH)
        C.clipPath(clip,stroke=0,fill=0)
        C.drawImage(f['path'],x+CW-dw,H-y-IH+(IH-dh)/2,width=dw,height=dh)
        C.restoreState()
        f['effective_dpi']=round(72/scale,2)
        text(x,y+IH+5,f['filename'],8.3,'Bold')
        right(x+CW,y+IH+5,f['time'],8.8,'Bold')
        text(x,y+IH+18,'35 mm  /  f/4  /  1/125 s  /  ISO 800',7.2)
    C.setStrokeColor(HexColor('#93958f'))
    C.line(M,29,W-M,29)
    text(M,H-22,'12 fichiers  /  MODE AUTO',7.5,color=GREY)
    right(W-M,H-22,f'{page+1} / 2',8,color=GREY)
    C.showPage()
C.save()

doc=pymupdf.open(OUT)
assert len(doc)==2
assert len(frames)==24
assert len({f['filename'] for f in frames})==24
assert all(f['effective_dpi']>=300 for f in frames)
alltext='\n'.join(page.get_text() for page in doc)
for forbidden in ['Salomé','Kern','Vasco','Bellini','Milo','Saran','indice','suspect','coupable','preuve','correspondance','matching','joueurs','photographe']:
    assert not re.search(r'\b'+re.escape(forbidden)+r'\b',alltext,re.I),forbidden
for i,page in enumerate(doc):
    txt=page.get_text()
    assert txt.count('ISO 800')==12
    assert txt.count('horloge interne non synchronisée')==1
    for timestamp in DATA['times'][i]:assert timestamp in txt,timestamp
    for frame in [f for f in frames if f['page']==i]:assert frame['filename'] in txt
    assert DATA['times'][i]==sorted(DATA['times'][i])
    page.get_pixmap(dpi=140).save(QA/f'planche_{"AB"[i]}.png')
    page.get_pixmap(dpi=300).save(EXPORTS/f'planche_{"AB"[i]}.png')
    single=pymupdf.open()
    single.insert_pdf(doc,from_page=i,to_page=i)
    single.save(ROOT/f'planche_{"AB"[i]}.pdf')

(ROOT/'verification.json').write_text(json.dumps({'pages':2,'format':'A4 paysage','vues_par_page':12,'minimum_dpi':min(f['effective_dpi'] for f in frames),'timestamps':'24 vérifiés','names':'absents','frames':frames},ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'prompts_generation.md').write_text('# Génération des prises de vue automatiques\n\nOutil : image_gen intégré. Chaque séquence contient trois vues illustrées. Les trois dernières vues de A sont produites individuellement pour uniformiser le format.\n\n'+'\n\n'.join(f'## Séquence {i+1:02d}\n\n{prompt}' for i,prompt in enumerate(DATA['prompts']))+'\n\n'+'\n\n'.join(f'## Vue individuelle {i+1}\n\n{p}' for i,p in enumerate(CORRECTIONS['prompts'])),encoding='utf-8')
print(OUT)
print('2 pages / 24 vues / 24 horodatages / définition minimale :',min(f['effective_dpi'] for f in frames),'dpi')
