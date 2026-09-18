import sys,json,random,re,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf

D=json.loads((ROOT/'production.json').read_text(encoding='utf-8'))
for font,file in [('Serif','pala.ttf'),('SerifBold','palab.ttf'),('Italic','palai.ttf'),('Sans','segoeui.ttf'),('Light','segoeuil.ttf'),('Hand','segoepr.ttf')]:
    pdfmetrics.registerFont(TTFont(font,'C:/Windows/Fonts/'+file))
OUT=ROOT/'arbre_genealogique_Remali_A3.pdf'
C=canvas.Canvas(str(OUT),pagesize=landscape(A3),pageCompression=1)
C.setTitle('Descendance Lyna '+D['lyna_nom']+' - Clément '+D['clement_nom'])
C.setAuthor('Atelier des Filiations')
C.setSubject('Édition familiale 2187 / FR-2187-064')
W,H=landscape(A3)
INK=HexColor('#343e36')
MID=HexColor('#7c7766')
LINE=HexColor('#b3a078')
PAPER=HexColor('#faf7ee')
C.setFillColor(PAPER)
C.rect(0,0,W,H,fill=1,stroke=0)

def txt(x,y,s,size=12,font='Serif',color=INK):
    C.setFillColor(color);C.setFont(font,size)
    C.drawString(x,H-y-size,s)

def centered(cx,y,s,size=12,font='Serif',color=INK):
    C.setFillColor(color);C.setFont(font,size)
    C.drawCentredString(cx,H-y-size,s)

def line(x,y,x2,y2,width=.8,color=LINE):
    C.setStrokeColor(color);C.setLineWidth(width)
    C.line(x,H-y,x2,H-y2)

# A clean archival sheet: fine gold rules and a quiet pearlescent inner rule.
iridescent=['#b6a17a','#b6b7a1','#bec1bb','#c8bdbe','#cabea7','#b6a17a']
for inset,lw,color in [(23,.65,'#c1ad85'),(28,.22,'#dbccb0'),(34,.3,'#ddd5bd')]:
    C.setStrokeColor(HexColor(color));C.setLineWidth(lw)
    C.rect(inset,inset,W-2*inset,H-2*inset,fill=0,stroke=1)
for i,color in enumerate(iridescent):
    line(48+i*(W-96)/6,35,48+(i+1)*(W-96)/6,35,.4,HexColor(color))
for cx,cy in [(44,44),(W-44,44),(44,H-44),(W-44,H-44)]:
    C.setStrokeColor(HexColor('#bda679'));C.setLineWidth(.35)
    C.circle(cx,cy,6,fill=0,stroke=1)
    C.circle(cx,cy,2,fill=0,stroke=1)
for offset,width,color in [(-.7,1.1,'#f4f0e5'),(0,.2,'#ece6d8'),(.5,.45,'#fffdf5')]:
    line(W/2+offset,38,W/2+offset,H-38,width,HexColor(color))
    line(38,H/2+offset,W-38,H/2+offset,width,HexColor(color))
def tracked(x,y,s,size=8,spacing=2,color=MID):
    C.saveState()
    C.setFillColor(color)
    t=C.beginText(x,H-y-size);t.setFont('Sans',size);t.setCharSpace(spacing);t.textOut(s);C.drawText(t)
    C.restoreState()

centered(W/2,47,'ARCHIVES FAMILIALES  ·  ÉDITION 2187',8.5,'Sans',MID)
centered(W/2,67,'Famille Remali',34,'Serif')
centered(W/2,112,'Descendance de Lyna '+D['lyna_nom']+' et Clément '+D['clement_nom'],14,'Italic',INK)
line(W/2-145,140,W/2-12,140,.4)
line(W/2+12,140,W/2+145,140,.4)
C.setStrokeColor(LINE);C.setLineWidth(.45)
C.circle(W/2,H-140,2,fill=0,stroke=1)

# Workshop device: a restrained geometric seal printed into the family sheet.
sx,sy=185,273
for radius,start,extent,width,color in [(66,0,360,.55,'#bca477'),(63,0,360,.2,'#d0bd99'),(54,0,360,.3,'#baad93')]:
    C.setStrokeColor(HexColor(color));C.setLineWidth(width)
    C.arc(sx-radius,H-sy-radius,sx+radius,H-sy+radius,start,extent)
for phase,color in [(0,'#c0ae88'),(math.pi,'#c3beb0')]:
    p=C.beginPath()
    for k in range(721):
        t=k*math.pi/360
        radius=59+2.4*math.sin(24*t+phase)
        x=sx+radius*math.cos(t);y=H-sy+radius*math.sin(t)
        if k==0:p.moveTo(x,y)
        else:p.lineTo(x,y)
    C.setStrokeColor(HexColor(color));C.setLineWidth(.2);C.drawPath(p,stroke=1,fill=0)
centered(sx,sy-35,'R',55,'Italic',HexColor('#a58a57'))
centered(sx,353,'Mémoire familiale',11,'Italic',MID)
centered(sx,375,'2187',10,'Serif',MID)

nodes=[]
def person(cx,y,name,detail,width=194,extra=None):
    left=cx-width/2
    root=y==159
    C.setFillColor(PAPER)
    C.rect(left,H-y-56,width,56,fill=1,stroke=0)
    line(left+16,y+54,left+width-16,y+54,.35,HexColor('#c9b58b'))
    size=15 if pdfmetrics.stringWidth(name,'SerifBold',15)<=width-18 else 13.4
    assert pdfmetrics.stringWidth(name,'SerifBold',size)<=width-16,name
    centered(cx,y+9,name,size,'SerifBold',INK)
    if detail:
        centered(cx,y+35,detail,10.5,'Italic',MID)
    if extra:centered(cx,y+62,extra,9.5,'Italic',MID)
    nodes.append({'name':name,'cx':cx,'top':y,'width':width})

def couple(y,leftname,leftdetail,rightname,rightdetail,union):
    person(480,y,leftname,leftdetail,204)
    person(710,y,rightname,rightdetail,204)
    line(582,y+25,608,y+25)
    line(595,y+25,595,y+55)
    centered(595,y+62,union,10,'Italic',MID)

def descent(start_y,child_y,centers):
    # Parent origin is the midpoint of the union, or centre of an individual card.
    junction=child_y-20
    line(595,start_y,595,junction)
    if len(centers)>1 or centers[0]!=595:
        line(min([595]+centers),junction,max([595]+centers),junction)
    for cx in centers:line(cx,junction,cx,child_y)
    C.setFillColor(PAPER);C.setStrokeColor(LINE);C.setLineWidth(.7)
    C.circle(595,H-junction,2.1,fill=1,stroke=1)

couple(159,'Lyna '+D['lyna_nom'],'','Clément '+D['clement_nom'],'','Union : '+D['date_mariage'])
descent(237,266,[480])
couple(266,'Ariane Remali','née en 2034','Thomas Varenne','né en 2031','Union : 2061')
descent(344,373,[480,1010])
couple(373,'Lucien Remali','né en 2065','Inès Vidal','née en 2068','Union : 2092')
person(1010,373,'Célia Remali','née en 2069',218)
descent(451,480,[180,480])
couple(480,'Jeanne Remali','née en 2096','Émile Morel','né en 2094','Union : 2124')
person(180,480,'Maud Remali','née en 2100',218)
descent(558,587,[595,1010])
person(595,587,'Élise Remali','née en 2128',248)
person(1010,587,'Adrien de MontFaucont','né en 2131',218)
descent(643,694,[180,595])
person(595,694,'Éléonore « Nora » Remali','née en 2158 · 29 ans en 2187',248)
person(180,694,'Sacha Remali','né en 2162 · 25 ans en 2187',218)

# Modest workshop imprint. Family details stay on the sheet without commentary.
line(58,781,W-190,781,.55)
tracked(58,793,'ATELIER DES FILIATIONS',7.5,1.2)
txt(285,793,'FR-2187-064  /  12 novembre 2187',8.5,'Sans',MID)
txt(682,793,'Exemplaire familial',8.5,'Sans',MID)

# A lifted lower-right corner exposes a small portion of the handwritten reverse.
C.setFillColor(HexColor('#e5dfd0'))
p=C.beginPath();p.moveTo(W-112,0);p.lineTo(W,108);p.lineTo(W,0);p.close()
C.drawPath(p,fill=1,stroke=0)
C.setFillColor(HexColor('#fffdf6'))
C.setStrokeColor(HexColor('#d3c6aa'))
p=C.beginPath();p.moveTo(W-111,0);p.curveTo(W-119,37,W-116,77,W-108,108);p.lineTo(W,108);p.close()
C.drawPath(p,fill=1,stroke=1)
C.saveState();C.translate(W-99,48);C.rotate(13)
C.setFillColor(HexColor('#7b715e'));C.setFont('Hand',10)
C.drawString(0,0,'pour Nora')
C.restoreState()
C.showPage();C.save()

doc=pymupdf.open(OUT)
assert len(doc)==1
text=doc[0].get_text()
assert '2158' in text and '29 ans en 2187' in text
assert 'Adrien de MontFaucont' in text
assert 'Léon Remali' not in text
for forbidden in ['cousine','indice','suspect','preuve','cela prouve','joueurs','énigme','contredit']:
    assert not re.search(r'\b'+re.escape(forbidden)+r'\b',text,re.I),forbidden
for name in ['Ariane Remali','Lucien Remali','Jeanne Remali','Élise Remali','Éléonore « Nora » Remali']:
    assert name in text,name
years=[2034,2065,2096,2128,2158]
assert all(20<=b-a<=40 for a,b in zip(years,years[1:]))
assert 2187-2158==29
for item in D['branche_principale']:
    if 'union' in item:
        assert item['union']-item['naissance']>=18
        assert item['union']-item['naissance_conjoint']>=18
qa=ROOT/'verification';qa.mkdir(exist_ok=True)
doc[0].get_pixmap(dpi=100).save(qa/'arbre_A3.png')
doc[0].get_pixmap(dpi=300).save(ROOT/'arbre_genealogique_Remali_A3_300dpi.png')
(ROOT/'verification.json').write_text(json.dumps({'pages':1,'format':'A3 paysage','text_and_lines':'vectoriels','export_dpi':300,'direct_line':['Lyna Remali et Clément Goldstein']+[x['nom'] for x in D['branche_principale']],'birth_years':years,'ages_checked':True,'names_pending':False,'wedding_date_pending':True},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT)
