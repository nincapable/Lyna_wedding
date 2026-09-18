import sys, json, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import pymupdf

data = json.loads((ROOT / 'production.json').read_text(encoding='utf-8'))
assets = ROOT / 'fiches'
assets.mkdir(exist_ok=True)
out = ROOT / 'registre_biometrique_LC-18-42.pdf'
pdfmetrics.registerFont(TTFont('TimesLocal', 'C:/Windows/Fonts/times.ttf'))
pdfmetrics.registerFont(TTFont('TimesLocalBold', 'C:/Windows/Fonts/timesbd.ttf'))
c = canvas.Canvas(str(out), pagesize=A4)
c.setTitle('Unité de contrôle des déplacements - Registre biométrique provisoire')
c.setAuthor('Unité de contrôle des déplacements')
W,H = A4
def text(x,y,s,size=12,bold=False):
    c.setFont('TimesLocalBold' if bold else 'TimesLocal',size)
    c.drawString(x,y,s)
def center(y,s,size=12,bold=False):
    c.setFont('TimesLocalBold' if bold else 'TimesLocal',size)
    c.drawCentredString(W/2,y,s)
c.setFillColorRGB(.967,.961,.935)
c.rect(0,0,W,H,fill=1,stroke=0)
c.setFillColorRGB(.21,.22,.22)
c.setStrokeColorRGB(.44,.45,.44)
c.setLineWidth(.5)
center(H-62,'Unité de contrôle des déplacements',19,True)
c.line(43,H-78,W-43,H-78)
text(49,H-116,'SÉRIE LC / ENREGISTREMENT PROVISOIRE',9)
center(H-248,'Registre biométrique',31,True)
center(H-286,'provisoire',31,True)
center(H-329,'Dossier LC-18/42',16)
center(H-353,'relevés établis sur identité déclarée',13)
c.rect(64,240,W-128,146)
text(80,362,'TABLE DES FICHES',11,True)
for i,p in enumerate(data['people']):
    y = 339-i*17
    text(80,y,f'{i+1:02d}   {p[1]} {p[0]}',11)
    text(W-111,y,f'{i+2} / 7',10)
text(49,167,'Scellé : LC-18/42-RB',11)
text(49,140,'Date : ____ / ____ / ______',10)
text(260,140,'Heure : ____ : ____',10)
text(49,113,'Paraphe opérateur : ____________________',10)
c.line(43,76,W-43,76)
center(57,'identité non certifiée — déclaration de l’intéressé(e)',9)
text(W-68,39,'1 / 7',10)
c.showPage()
dimensions=[]
for src,name in zip(data['images'],data['names']):
    dst=assets/(name+'.png')
    shutil.copy2(src,dst)
    with Image.open(dst) as im:
        iw,ih=im.size
    # Preserve original pixels; add printing margins with document placement.
    margin=25
    scale=min((W-2*margin)/iw,(H-2*margin)/ih)
    dw,dh=iw*scale,ih*scale
    c.drawImage(str(dst),(W-dw)/2,(H-dh)/2,width=dw,height=dh)
    dimensions.append({'fiche':name,'pixels':[iw,ih],'dpi_effectifs':round(iw/dw*72)})
    c.showPage()
c.save()
qa=ROOT/'verification'
qa.mkdir(exist_ok=True)
doc=pymupdf.open(out)
assert len(doc)==7
for i,page in enumerate(doc):
    page.get_pixmap(dpi=110).save(qa/f'page_{i+1:02d}.png')
(ROOT/'verification.json').write_text(json.dumps({'pages':7,'format':'A4 portrait','images':dimensions},ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'prompts_generation.md').write_text('# Prompts de génération\n\nOutil utilisé : image_gen intégré.\n\n'+'\n\n'.join(f'## Fiche {i+1:02d}\n\n{p}' for i,p in enumerate(data['prompts'])),encoding='utf-8')
print(str(out))
print(json.dumps(dimensions))
