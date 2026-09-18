from pathlib import Path
import sys,json,random
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
for n,f in [('Sans','arial.ttf'),('Bold','arialbd.ttf'),('Hand','segoepr.ttf')]:
    pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f))
ROOT.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'liste_emargement_photo_groupe_A4.pdf'
W,H=A4;c=canvas.Canvas(str(OUT),pagesize=A4)
c.setTitle('Photo de groupe - appel 18 h 40 - jardin intérieur')
INK=HexColor('#3c423b');GREY=HexColor('#868d7d')
def txt(x,y,s,font='Sans',size=8,color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawString(x,H-y-size,s)
def rect(x,y,w,h,fill,stroke=None,r=0):
    c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke or fill));c.setLineWidth(.6)
    if r:c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
    else:c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))
# Board, paper and a metal clip; every part stays within print margins.
rect(16,20,W-32,H-38,'#dedfd7',r=13)
rect(13,16,W-32,H-38,'#a5977e','#756f60',13)
for inset in [20,23]:
    c.setStrokeColor(HexColor('#b0a58f'));c.setLineWidth(.4);c.roundRect(inset,23,W-2*inset,H-47,9,fill=0,stroke=1)
rect(33,49,W-62,H-93,'#c4bdac')
rect(30,46,W-62,H-93,'#faf8ef','#d1cebf')
rect(W/2-69,24,138,43,'#7c817b','#515951',7)
rect(W/2-61,28,122,29,'#bdc4bd','#737c73',5)
rect(W/2-45,34,90,8,'#dce0d7',r=3)
for x in [W/2-54,W/2+54]:
    c.setFillColor(HexColor('#6f7971'));c.circle(x,H-49,3,fill=1,stroke=0)
txt(47,84,'Photo de groupe','Bold',19)
txt(47,112,'Appel 18 h 40 — jardin intérieur','Sans',12)
txt(47,143,'Placement / liste de travail','Sans',8,GREY)
rows=[
('Arnaud, Camille','Famille Lyna'),('Aubert, Julien','Amis Clément'),('Baron, Inès','Famille Lyna'),
('Bellini, Vasco','Invité'),('Bertrand, Alice','Amis Lyna'),('Besson, Olivier','Amis Clément'),
('Bonnet, Léa','Famille Clément'),('Caron, Hugo','Amis Lyna'),('Charrier, Louise','Famille Lyna'),
('Chevalier, Paul','Amis Clément'),('Colin, Manon','Amis Lyna'),('de Montfaucon, Adrien','Amis Clément'),
('Denis, Raphaël','Famille Clément'),('Dumas, Sophie','Famille Lyna'),('Fabre, Luc','Amis Clément'),
('Faure, Zoé','Famille Lyna'),('Fontaine, Marc','Famille Clément'),('Garnier, Éva','Amis Lyna'),
('Girard, Mathis','Amis Clément'),('Guérin, Chloé','Famille Lyna'),('Henry, Émile','Famille Clément'),
('Kern, Salomé','Amis Clément'),('Lambert, Agathe','Amis Lyna'),('Laurent, Noé','Famille Lyna'),
('Lefèvre, Claire','Famille Clément'),('Leroy, Simon','Amis Clément'),('Martin, Anaïs','Famille Lyna'),
('Mercier, Louis','Amis Lyna'),('Moreau, Jeanne','Famille Clément'),('Orsen, Gabriel','Famille Lyna'),
('Petit, Arthur','Amis Clément'),('Remali, Éléonore dite Nora','Famille Lyna'),('Robert, Sarah','Famille Clément'),
('Roux, Victor','Amis Lyna'),('Saran, Milo','Amis Clément'),('Thomas, Marie','Famille Lyna')]
xs=[47,218,315,366,409,545]
top=170;header=34;rh=14.9
rect(xs[0],top,xs[-1]-xs[0],header,'#e9ebdf')
for x,w,s in zip(xs,[171,97,51,43,136],['Nom','Groupe familial<br/>ou relation','Premier<br/>appel','Placé','Observation logistique']):
    p=Paragraph(s,ParagraphStyle('h',fontName='Bold',fontSize=7.4,leading=9,textColor=INK))
    _,hh=p.wrap(w-10,40);p.drawOn(c,x+5,H-top-8-hh)
bottom=top+header+len(rows)*rh
c.setStrokeColor(HexColor('#cbd0bd'));c.setLineWidth(.4)
for x in xs:c.line(x,H-top,x,H-bottom)
for k in range(len(rows)+1):c.line(xs[0],H-top-header-k*rh,xs[-1],H-top-header-k*rh)
positions={}
for i,(name,group) in enumerate(rows):
    yy=top+header+i*rh;positions[name]=yy
    txt(52,yy+3.7,name,size=7.9);txt(223,yy+3.7,group,size=7.4)
    unchecked=name in ['Kern, Salomé','Remali, Éléonore dite Nora','Baron, Inès','Chevalier, Paul','Henry, Émile','Robert, Sarah','Thomas, Marie']
    for j,x in enumerate([336,383]):
        c.setStrokeColor(GREY);c.setLineWidth(.5);c.rect(x,H-yy-11,7,7,fill=0,stroke=1)
        if not unchecked:
            c.setStrokeColor(HexColor('#5e6862'));c.setLineWidth(.9)
            p=c.beginPath();p.moveTo(x+.6,H-yy-7);p.lineTo(x+3,H-yy-10);p.lineTo(x+8,H-yy-3);c.drawPath(p,stroke=1,fill=0)
    if name=='Fontaine, Marc':txt(414,yy+2.3,'témoin : cherche veste','Hand',7.2)
    if name=='Laurent, Noé':txt(414,yy+2.3,'fond → premier rang','Hand',7.2)
    if name=='Girard, Mathis':txt(414,yy+2.3,'fond → premier rang','Hand',7.2)
for name in ['Laurent, Noé','Girard, Mathis']:
    yy=positions[name]
    c.setStrokeColor(HexColor('#777d72'));c.setLineWidth(.65);c.line(413,H-yy-7,432,H-yy-9)
txt(53,753,'Enfants au premier rang.','Hand',9)
txt(270,753,'Une prise suffit.','Hand',9)
c.setStrokeColor(HexColor('#737970'));c.setLineWidth(.7);c.line(268,H-761,370,H-763)
txt(380,753,'seconde prise demandée','Hand',8)
c.showPage();c.save()
doc=pymupdf.open(OUT);assert len(doc)==1
text=doc[0].get_text();assert 'non vue au placement' not in text
assert 'absente' not in text.lower()
doc[0].get_pixmap(dpi=140).save(ROOT/'verification_A4.png')
doc[0].get_pixmap(dpi=300).save(ROOT/'liste_emargement_300dpi.png')
(ROOT/'texte_liste.txt').write_text(text,encoding='utf-8')
print(OUT)
