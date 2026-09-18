from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
import pymupdf
for n,f in [('Serif','pala.ttf'),('Bold','palab.ttf'),('Italic','palai.ttf'),('Sans','segoeui.ttf'),('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f))
ROOT.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'ordre_mission_Gabriel_Orsen_DC-LC-731.pdf'
W,H=A4;c=canvas.Canvas(str(OUT),pagesize=A4)
c.setTitle('Doctrine de la Continuité - Ordre DC-LC-731');c.setAuthor('Collège des Événements Attestés')
INK=HexColor('#263a50');MID=HexColor('#657589');LINE=HexColor('#adbaca')
c.setFillColor(HexColor('#f0f3f8'));c.rect(0,0,W,H,fill=1,stroke=0)
c.setStrokeColor(LINE);c.setLineWidth(.5);c.rect(27,27,W-54,H-54,fill=0,stroke=1)
c.rect(32,32,W-64,H-64,fill=0,stroke=1)
def txt(x,y,s,font='Sans',size=10,color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawString(x,H-y-size,s)
def center(y,s,font='Serif',size=12,color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawCentredString(W/2,H-y-size,s)
def line(y):
    c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(55,H-y,W-55,H-y)
def para(y,s,size=11):
    p=Paragraph(s,ParagraphStyle('body',fontName='Serif',fontSize=size,leading=16,textColor=INK))
    _,h=p.wrap(W-110,200);p.drawOn(c,55,H-y-h);return y+h
def section(y,n,s):
    txt(55,y,n,'Mono',8,MID);txt(83,y-2,s,'Sans',9,INK)

# Geometric device of the Doctrine, drawn without a real institutional logo.
cx,cy=W/2,H-95
c.setStrokeColor(INK);c.setLineWidth(.7)
for radius in [42,38,28,23]:c.circle(cx,cy,radius,fill=0,stroke=1)
for k in range(24):
    a=k*math.pi/12
    c.line(cx+31*math.cos(a),cy+31*math.sin(a),cx+35*math.cos(a),cy+35*math.sin(a))
for dx in [-1,1]:
    c.line(cx+dx*52,cy,cx+dx*155,cy)
    c.line(cx+dx*65,cy-3,cx+dx*138,cy-3)
for rotation in [0,math.pi/4]:
    p=c.beginPath()
    for i in range(4):
        angle=rotation+math.pi/4+i*math.pi/2
        x=cx+19*math.cos(angle);y=cy+19*math.sin(angle)
        if i==0:p.moveTo(x,y)
        else:p.lineTo(x,y)
    p.close();c.drawPath(p,stroke=1,fill=0)
c.circle(cx,cy,3,fill=0,stroke=1)
center(135,'DOCTRINE DE LA CONTINUITÉ','Sans',11)
center(156,'Il n’est de salut que dans ce qui doit advenir.','Italic',11,MID)
center(190,'Mandat de l’Anneau','Bold',26)
center(227,'COLLÈGE DES ÉVÉNEMENTS ATTESTÉS · 2312 · DC-LC-731','Serif',9,MID)
line(254)
txt(55,270,'DÉPOSITAIRE ÉLU','Serif',8,MID);txt(195,265,'Gabriel Orsen','Bold',17)
txt(55,302,'UNION CONSACRÉE','Serif',8,MID);txt(195,299,'Lyna Remali et Clément Goldstein','Serif',11)
section(338,'I','PAROLE DU COLLÈGE')
para(359,"Frère Gabriel, tu assureras la disparition temporaire de l’anneau cérémoniel. Tu le garderas intact dans la gaine neutre, puis le replaceras dans son écrin avant que l’engagement soit scellé. Tu n’agiras ni par désir ni par crainte. Ce qui est attesté doit s’accomplir ; ta volonté s’effacera devant la Continuité.")
section(443,'II','LES QUATRE OBSERVANCES / HEURES LOCALES')
schedule=[('18 h 51','Franchir le seuil du salon réservé aux mariés.'),('18 h 52 à 18 h 54','Retirer l’anneau ; le préserver dans la gaine neutre.'),('21 h 08','Rendre l’anneau à son écrin, sans altération.'),('Avant 21 h 16','Veiller à sa présence avant le scellement de l’union.')]
for i,(time,action) in enumerate(schedule):
    yy=466+i*28
    txt(65,yy,time,'Mono',9);txt(204,yy,action,'Serif',10)
    c.setStrokeColor(LINE);c.setLineWidth(.3);c.line(55,H-yy-22,W-55,H-yy-22)
section(596,'III','LE SEUIL ET LE SILENCE')
para(617,"Depuis la salle principale, emprunter le couloir donnant accès au salon réservé aux mariés. L’écrin repose sur la commode du salon.",10.5)
para(660,"Si l’anneau est déjà absent : ne pas intervenir, observer la continuité et rendre compte au Collège. Tu ne substitueras aucun objet. Tu accepteras le silence comme tu acceptes l’ordre. Le doute n’autorise aucun écart ; nul dépositaire ne corrige ce qui est attesté.",10.5)
line(730)
txt(55,744,'Que ma volonté cède et que la Continuité demeure.','Italic',11)
txt(55,765,'Collège des Événements Attestés / CEA·IX-731·2F6A-91C0','Serif',8,MID)
txt(395,746,'Sous le sceau · 2312','Serif',8,MID)
txt(395,765,'Exemplaire 01 / 01','Mono',8,MID)
c.showPage();c.save()
doc=pymupdf.open(OUT);assert len(doc)==1
text=doc[0].get_text()
for s in ['Gabriel Orsen','2312','18 h 51','18 h 52 à 18 h 54','21 h 08','21 h 16','ne pas intervenir']:
    assert s in text,s
assert '18 h 42' not in text
for s in ['suspect','coupable','preuve','joueurs','indice']:
    assert s not in text.lower(),s
qa=ROOT/'verification';qa.mkdir(exist_ok=True)
doc[0].get_pixmap(dpi=110).save(qa/'page_01.png')
doc[0].get_pixmap(dpi=300).save(ROOT/'ordre_mission_Gabriel_Orsen_300dpi.png')
(ROOT/'texte_ordre.txt').write_text(text,encoding='utf-8')
(ROOT/'verification.json').write_text(json.dumps({'pages':1,'format':'A4 portrait','export_dpi':300,'texte_et_sceau':'vectoriels','annee':2312,'reference':'DC-LC-731'},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT)
