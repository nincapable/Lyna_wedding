from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import pymupdf
for n,f in [('Sans','arial.ttf'),('Bold','arialbd.ttf'),('Serif','times.ttf')]:
    pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f))
ROOT.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'inventaire_AM-06_necessaire_ancien.pdf'
c=canvas.Canvas(str(OUT),pagesize=A4);W,H=A4
c.setTitle('Inventaire AM-06');c.setAuthor('Cellule technique de constatation')
INK=HexColor('#343b37');MID=HexColor('#71796f')
def txt(x,y,s,font='Sans',size=9,color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawString(x,H-y-size,s)
def base(page,title):
    c.setFillColor(HexColor('#faf9f2'));c.rect(0,0,W,H,fill=1,stroke=0)
    txt(45,31,'CELLULE TECHNIQUE DE CONSTATATION','Sans',8,MID)
    txt(45,60,title,'Bold',21)
    txt(45,95,'AM-06 / vestiaire / inventaire matériel','Sans',9,MID)
    c.setStrokeColor(HexColor('#c9cec2'));c.setLineWidth(.5);c.line(45,H-123,W-45,H-123)
    txt(45,802,'AM-06 / scellé AM-06-S1 / opérateur L. Perrin','Sans',8,MID)
    txt(W-74,802,str(page)+' / 2','Sans',8,MID)
def para(y,s):
    p=Paragraph(s,ParagraphStyle('p',fontName='Serif',fontSize=11,leading=16,textColor=INK))
    _,h=p.wrap(W-90,200);p.drawOn(c,45,H-y-h);return y+h
base(1,'Fiche d’inventaire')
txt(45,147,'LIEU DE DÉCOUVERTE','Bold',8,MID)
para(169,'Poche intérieure d’un manteau attribué à Adrien de Montfaucon, vestiaire du lieu de réception.')
txt(45,225,'OBJETS CONDITIONNÉS ENSEMBLE','Bold',8,MID)
rows=[('01','Étui de cuir ancien','1','Logements intérieurs partiellement vides.'),('02','Crochets fins','3','Métal poli ; profils distincts ; usure ancienne.'),('03','Outil de tension','1','Pièce coudée ; surface entretenue.'),('04','Petite lime','1','Stries visibles ; traces d’usage antérieures.'),('05','Fil rigide','1','Segment métallique ; extrémités émoussées.'),('06','Clé universelle ancienne','1','Anneau et panneton ; patine régulière.'),('07','Chiffon','1','Tissu clair plié ; traces de polissage.')]
for i,(code,name,qty,desc) in enumerate(rows):
    y=253+i*49
    txt(45,y,code,'Sans',9,MID);txt(78,y,name,'Bold',10);txt(501,y,qty,'Sans',10)
    txt(78,y+20,desc,'Sans',9)
    c.setStrokeColor(HexColor('#d7d9ce'));c.line(45,H-y-39,W-45,H-y-39)
txt(45,620,'ÉTAT ET EXAMEN DE SURFACE','Bold',8,MID)
para(642,'Outils anciens, entretenus, présentant des traces d’usage antérieures. Nécessaire incomplet. Aucune fibre noire semblable à l’enveloppe isolante ; aucun résidu provenant de l’écrin. Aucun contenant isolant présent dans cet ensemble.')
para(722,'Étiquette solidaire de l’étui : « Atelier Veyrac — révision 1896 ». Ensemble placé sous scellé AM-06-S1 après inventaire ; planche descriptive jointe.')
c.showPage()
base(2,'Planche des objets inventoriés')
# Grid and vector illustrations; proportions illustrative, no operational drawing.
left,top,bw,bh=45,151,W-90,607
c.setStrokeColor(HexColor('#e2e4d9'));c.setLineWidth(.25)
for x in range(45,552,12):c.line(x,H-top,x,H-top-bh)
for y in range(151,759,12):c.line(left,H-y,left+bw,H-y)
def rect(x,y,w,h,fill,r=2):
    c.setFillColor(HexColor(fill));c.setStrokeColor(INK);c.setLineWidth(.8)
    c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=1)
def path(points,width=2,color=INK):
    c.setStrokeColor(color);c.setLineWidth(width);c.setLineCap(1)
    p=c.beginPath();p.moveTo(points[0][0],H-points[0][1])
    for x,y in points[1:]:p.lineTo(x,H-y)
    c.drawPath(p,stroke=1,fill=0)
rect(75,182,175,135,'#8d7560',9);rect(82,192,161,114,'#b09a7c',5)
for x in [104,130,156,182,208]:
    path([(x,204),(x,295)],.6,HexColor('#705e4e'))
for y in [216,275]:rect(91,y,143,10,'#887059')
txt(80,328,'01 / étui','Sans',9)
path([(230,217),(270,204),(285,236)],.7)
rect(257,190,111,46,'#ebe6d3')
txt(265,199,'Atelier Veyrac','Serif',10);txt(265,215,'révision 1896','Serif',9)
# Three fine metal tools with understated profiles.
for i,x in enumerate([305,365,425]):
    rect(x-8,283,16,86,'#797d78',4)
    path([(x,283),(x,254),(x+3+i*2,248),(x+8,250)],2,HexColor('#747c7b'))
    path([(x-3,297),(x-3,353)],.6,HexColor('#c5c9bf'))
txt(300,382,'02 / trois crochets fins','Sans',9)
path([(308,436),(423,436),(423,414)],4,HexColor('#7e8580'))
txt(298,459,'03 / outil de tension','Sans',9)
rect(318,510,119,12,'#afb3ab');rect(437,506,47,20,'#817361',4)
for x in range(325,433,5):path([(x,512),(x-3,520)],.5)
txt(318,538,'04 / petite lime','Sans',9)
path([(318,590),(482,583)],1.8,HexColor('#7a817e'))
txt(318,606,'05 / fil rigide','Sans',9)
c.setStrokeColor(INK);c.setFillColor(HexColor('#b5a587'));c.setLineWidth(1)
c.circle(114,H-463,21,fill=1,stroke=1)
c.setFillColor(HexColor('#faf9f2'));c.circle(114,H-463,12,fill=1,stroke=1)
rect(109,484,10,91,'#b5a587');rect(119,554,25,21,'#b5a587',0)
txt(78,598,'06 / clé ancienne','Sans',9)
rect(82,643,167,79,'#d9d4c3',7)
path([(95,651),(238,669),(235,710),(94,696),(95,651)],.5,HexColor('#8d8f7b'))
path([(95,664),(230,685)],.4,HexColor('#a7a793'))
txt(84,734,'07 / chiffon','Sans',9)
c.showPage();c.save()
doc=pymupdf.open(OUT);assert len(doc)==2
for dpi,folder in [(110,'verification'),(300,'pages_300dpi')]:
    d=ROOT/folder;d.mkdir(exist_ok=True)
    for i,p in enumerate(doc):p.get_pixmap(dpi=dpi).save(d/f'page_{i+1:02}.png')
(ROOT/'texte_inventaire.txt').write_text('\n'.join(p.get_text() for p in doc),encoding='utf-8')
print(OUT)
