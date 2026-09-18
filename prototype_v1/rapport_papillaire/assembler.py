"""Compose LC-SR-04; original reference pixels are placed through PDF clipping."""
import sys, json, shutil, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent
WORK = ROOT.parents[1]
sys.path.insert(0, str(WORK / 'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from PIL import Image
import pymupdf

DATA = json.loads((ROOT/'production.json').read_text(encoding='utf-8'))
EXTRA = json.loads((ROOT/'illustrations.json').read_text(encoding='utf-8'))
ASSETS = ROOT/'illustrations'
ASSETS.mkdir(exist_ok=True)
MACRO = ASSETS/'surfaces_traitees.png'
PARTIAL = ASSETS/'P-03_trace_partielle.png'
shutil.copy2(DATA['macro_source'], MACRO)
shutil.copy2(EXTRA['partial_source'], PARTIAL)
for record in DATA['reference_crops']:
    shutil.copy2(ROOT.parent/'registre_biometrique/fiches'/record['file'], ASSETS/record['file'])
OUT = ROOT/'rapport_releves_papillaires_LC-SR-04.pdf'
for name,filename in [('Body','arial.ttf'),('Bold','arialbd.ttf'),('Italic','ariali.ttf'),('Title','timesbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+filename))
C = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
C.setTitle('Rapport de traitement des surfaces - salon réservé aux mariés')
C.setAuthor('Cellule technique de constatation')
C.setSubject('LC-SR-04 / Dossier LC-18/42')
W,H=A4
M=42
BW=W-2*M
INK=HexColor('#303633')
GREY=HexColor('#69706a')
RULE=HexColor('#9b9f96')
PAPER=HexColor('#f7f6ef')
FILL=HexColor('#e9ece5')
placed=[]

def txt(x,y,s,size=9,font='Body',color=INK):
    C.setFillColor(color)
    C.setFont(font,size)
    C.drawString(x,H-y-size,s)

def para(x,y,w,s,size=9,leading=None,font='Body',color=INK):
    style=ParagraphStyle('cell',fontName=font,fontSize=size,leading=leading or size*1.35,textColor=color)
    p=Paragraph(s,style)
    _,height=p.wrap(w,1000)
    p.drawOn(C,x,H-y-height)
    return height

def line(x1,y1,x2,y2,width=.45,color=RULE):
    C.setLineWidth(width)
    C.setStrokeColor(color)
    C.line(x1,H-y1,x2,H-y2)

def rect(x,y,w,h,fill=None,stroke=True):
    C.setLineWidth(.45)
    C.setStrokeColor(RULE)
    if fill: C.setFillColor(fill)
    C.rect(x,H-y-h,w,h,stroke=int(stroke),fill=int(fill is not None))

def section(y,number,title):
    txt(M,y,number,10,'Bold',GREY)
    txt(M+28,y,title,11,'Bold')
    line(M,y+21,W-M,y+21)

def head(page):
    rect(0,0,W,H,PAPER,False)
    txt(M,29,'CELLULE TECHNIQUE DE CONSTATATION',9,'Bold')
    txt(W-M-76,29,'LC-SR-04',10,'Bold')
    line(M,48,W-M,48)
    txt(M,60,'Rapport de traitement des surfaces',22,'Title')
    txt(M,89,'salon réservé aux mariés',17,'Title')
    txt(M,119,'Dossier LC-18/42',8.5)
    txt(226,119,'Lieu : salon réservé aux mariés',8.5)
    txt(W-M-58,119,f'Feuillet {page}/3',8.5)
    line(M,138,W-M,138)

def foot(page):
    line(M,780,W-M,780)
    txt(M,789,'LC-SR-04  /  Scellé LC-SR-04-S',8)
    txt(277,789,'Cellule technique de constatation',8)
    txt(W-M-28,789,f'{page} / 3',8)
    txt(M,806,'Date de rédaction : ____ / ____ / ______     Paraphe : __________',7.5,color=GREY)

def table(y,widths,headers,rows,heights,size=8.8):
    top=y
    for ri,row in enumerate([headers]+rows):
        height=heights[ri]
        x=M
        for ci,cell in enumerate(row):
            rect(x,top,widths[ci],height,FILL if ri==0 else None)
            ph=para(x+7,top+7,widths[ci]-14,cell,size if ri else size-.1,font='Bold' if ri==0 else 'Body')
            assert ph<=height-12, (ri,ci,ph,height,cell)
            x+=widths[ci]
        top+=height
    return top

def crop_place(path,box,x,y,width,tag):
    # Extract only the document illustration; never embed the surrounding identity sheet.
    with Image.open(path) as im: excerpt=im.crop(box).copy()
    l,t,r,b=box
    scale=width/(r-l)
    height=(b-t)*scale
    C.drawImage(ImageReader(excerpt),x,H-y-height,width=width,height=height)
    placed.append({'asset':tag,'effective_dpi':round(72/scale,2)})
    return height

def fingerprint(record,x,y,trace=False):
    box=record['box']
    scale=85/(box[2]-box[0])
    width=(box[2]-box[0])*scale
    height=(box[3]-box[1])*scale
    C.saveState()
    if trace:
        # A limited contact boundary is represented by the page's clipping path.
        p=C.beginPath()
        p.moveTo(x+2,H-y-1)
        p.lineTo(x+width-2,H-y-2)
        p.lineTo(x+width,H-y-height+3)
        p.lineTo(x+2,H-y-height+1)
        p.close()
        C.clipPath(p,stroke=0,fill=0)
    crop_place(ASSETS/record['file'],box,x,y,width,record['code']+(' trace' if trace else ' référence'))
    C.restoreState()
    # Thin numbered leaders are technical plate marks, without arrowheads.
    points=[(.26,.28,-15,.18),(.65,.57,width+11,.52),(.37,.83,-15,.88)]
    for n,(px,py,lx,ly) in enumerate(points,1):
        tx=x+px*width
        ty=y+py*height
        line(x+lx+3,y+ly*height+3,tx,ty,.25,INK)
        txt(x+lx-2,y+ly*height-1,str(n),6.5,'Body')

# PAGE 1
head(1)
section(151,'01','Inventaire des zones traitées')
rows=[
 ['P-01','Face supérieure du couvercle de l’écrin. Surface rigide lisse.','Poudre magnétique fine ; transfert adhésif sur fond clair.','Exploitable'],
 ['P-02','Angle avant droit de la commode. Bois verni.','Poudre noire ; transfert adhésif sur fond clair.','Exploitable'],
 ['P-03','Bord intérieur du tiroir supérieur. Bois verni.','Poudre magnétique fine ; transfert adhésif localisé.','Partielle'],
 ['P-04','Petit objet décoratif replacé sur la table voisine. Céramique émaillée.','Poudre noire ; transfert souple adapté à la courbure.','Exploitable'],
]
table(181,[38,173,194,BW-405],['Code','Zone / support','Révélation et prélèvement','Qualité'],rows,[26,43,43,43,53])
with Image.open(MACRO) as im: mw,mh=im.size
boxes=[(9,8,mw//2-13,mh//2-12),(mw//2+14,8,mw-9,mh//2-12),
       (9,mh//2+13,mw//2-13,mh-10),(mw//2+14,mh//2+13,mw-9,mh-10)]
gap=9
panel=(BW-3*gap)/4
for i,box in enumerate(boxes):
    x=M+i*(panel+gap)
    h=crop_place(MACRO,box,x,402,panel,f'Vignette P-0{i+1}')
    txt(x,402+h+5,f'P-0{i+1}  /  détail de surface',7.5)

section(508,'02','Relevé au trait des supports')
# Schematic front elevation: no invented room plan or secret compartments.
C.saveState()
C.translate(0,-12)
for a,b,d,e in [(55,548,200,548),(55,548,55,600),(200,548,200,600),(55,600,200,600),
                (59,562,196,562),(59,577,196,577),(59,592,196,592),
                (65,600,65,608),(190,600,190,608),(95,536,139,536),(95,536,95,547),
                (139,536,139,547),(95,541,139,541)]:
    line(a,b,d,e,.6,INK)
for y in [568,583,596]: line(117,y,137,y,.8,INK)
txt(99,523,'P-01',6.5)
txt(181,534,'P-02',6.5)
txt(61,551,'P-03',6.5)
# Adjacent table, elevation only.
line(224,562,279,562,.6,INK)
line(229,562,229,608,.6,INK)
line(275,562,275,608,.6,INK)
C.setLineWidth(.6)
C.setStrokeColor(INK)
C.ellipse(242,H-562,262,H-550,stroke=1,fill=0)
txt(240,536,'P-04',6.5)
C.restoreState()
para(313,541,235,'Élévations simplifiées, sans échelle.<br/><br/>Quatre transferts individualisés. Films fixés sur cartons de protection, faces adhésives isolées. Chaque enveloppe porte le code du prélèvement.',8.7)

section(631,'03','Chaîne de conservation')
table(660,[107,205,BW-312],['Opération','Conditionnement / contrôle','Visa'],[
 ['Mise sous enveloppes','LC-SR-04-P01 à P04 ; fermeture individuelle après fixation.','Opérateur : C.T. 12'],
 ['Dépôt technique','Scellé groupé LC-SR-04-S ; quatre enveloppes reçues fermées.','Réception : C.T. 08'],
],[25,35,35],8.2)
foot(1)
C.showPage()

# PAGE 2
head(2)
section(151,'04','Planche des tracés papillaires')
txt(M,179,'Examen manuel  /  Reproductions sans échelle  /  Repères numérotés de détail',8.5)
lookup={r['code']:r for r in DATA['reference_crops']}
short={'P-01':'Couvercle de l’écrin','P-02':'Angle de la commode','P-03':'Bord intérieur du tiroir','P-04':'Objet décoratif'}
card_width=(BW-16)/2
for i,code in enumerate(['P-01','P-02','P-03','P-04']):
    x=M+(i%2)*(card_width+16)
    y=206+(i//2)*264
    rect(x,y,card_width,250)
    txt(x+12,y+11,code,13,'Bold')
    txt(x+card_width-90,y+15,'Indéterminé' if code=='P-03' else lookup[code]['finger'].split()[0],9,'Bold')
    para(x+12,y+37,card_width-24,short[code],9)
    line(x+12,y+57,x+card_width-12,y+57)
    if code!='P-03':
        r=lookup[code]
        txt(x+24,y+65,'Empreinte relevée',7.5)
        txt(x+147,y+65,'Référence',7.5)
        fingerprint(r,x+26,y+88,True)
        fingerprint(r,x+147,y+88,False)
        txt(x+12,y+232,'Exploitable / examen manuel',8,color=GREY)
    else:
        txt(x+24,y+65,'Empreinte relevée',7.5)
        crop_place(PARTIAL,(330,295,930,973),x+70,y+87,110,'P-03 partielle')
        txt(x+12,y+232,'Partielle / surface lisible insuffisante',8,color=GREY)
para(M,735,BW,'Les repères numérotés désignent les détails lisibles des tracés. Reproductions sans échelle.',8.3)
foot(2)
C.showPage()

# PAGE 3
head(3)
section(151,'05','Résultats de l’examen manuel')
table(182,[38,112,64,123,BW-337],
 ['Code','Support','Qualité','Doigt','Réserve technique'],[
 ['P-01','Face supérieure du couvercle de l’écrin.','Exploitable','Pouce','Zone centrale lisible.'],
 ['P-02','Angle avant droit de la commode.','Exploitable','Index','Déformation locale en périphérie du transfert.'],
 ['P-03','Bord intérieur du tiroir supérieur.','Partielle','Indéterminé','Fragment discontinu ; caractères lisibles insuffisants.'],
 ['P-04','Petit objet décoratif replacé sur la table voisine.','Exploitable','Index','Courbure du support ; lecture limitée à la zone conservée.'],
 ],[39,84,94,80,102],8.7)
section(605,'06','Portée technique')
para(M,636,BW,'La datation d’une trace papillaire est impossible.',11,font='Bold')
para(M,661,BW,'Les réserves ci-dessus portent sur la lisibilité des tracés et l’état des transferts. L’examen est limité aux zones conservées.',9.2)
line(M,705,W-M,705)
txt(M,718,'Examen : C.T. 12',9)
txt(244,718,'Clôture technique : ____ / ____ / ______',9)
txt(M,743,'Conservation : LC-SR-04-S / enveloppes P01 à P04',8.5)
txt(383,743,'Visa : __________________',8.5)
foot(3)
C.showPage()
C.save()

# Validate the authored text, dimensions and effective raster density.
doc=pymupdf.open(OUT)
assert len(doc)==3
text='\n'.join(page.get_text() for page in doc)
for forbidden in ['indice','suspect','coupable','preuve','correspondance','matching','cela prouve que','cela innocente','cela implique que','18 h 42','18:42','jeu','joueurs']:
    assert not re.search(r'\b'+re.escape(forbidden)+r'\b',text,re.I),forbidden
for forbidden in ['Remali','Éléonore','Nora','Salomé','Kern','Milo','Saran','LC-RB-01','LC-RB-02','LC-RB-03','pouce droit','index droit','pouce gauche','index gauche','identité','attribution']:
    assert forbidden.casefold() not in text.casefold(),forbidden
for required in ['Pouce','Index','Indéterminé','La datation d’une trace papillaire est impossible.']:
    assert required in text,required
assert all(p['effective_dpi']>=300 for p in placed if p['asset'].startswith('Vignette') or p['asset']=='P-03 partielle'),placed
qa=ROOT/'verification'
qa.mkdir(exist_ok=True)
exports=ROOT/'pages_300dpi'
exports.mkdir(exist_ok=True)
for i,page in enumerate(doc,1):
    assert abs(page.rect.width-W)<1 and abs(page.rect.height-H)<1
    page.get_pixmap(dpi=120).save(qa/f'page_{i:02d}.png')
    page.get_pixmap(dpi=300).save(exports/f'LC-SR-04_page_{i:02d}.png')
(ROOT/'texte_rapport.txt').write_text(text,encoding='utf-8')
(ROOT/'verification.json').write_text(json.dumps({'pages':3,'format':'A4 portrait','fingerprint_width_mm':round(85*25.4/72,2),'export_dpi':300,'minimum_source_dpi':min(p['effective_dpi'] for p in placed),'source_limit':'Empreintes du registre agrandies sans ajout de détails ; résolution native conservée.','images':placed,'forbidden_terms':'absents'},ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'prompts_generation.md').write_text('# Illustrations du rapport LC-SR-04\n\nMode : outil image_gen intégré.\n\n## Surfaces traitées\n\n'+DATA['imagegen_prompt']+'\n\n## Trace partielle P-03\n\n'+EXTRA['partial_prompt']+'\n\nLes références P-01, P-02 et P-04 réutilisent les pixels des fiches du registre, cadrés directement dans le PDF. Les repères et le texte sont vectoriels.\n',encoding='utf-8')
print(OUT)
print('3 pages A4 ; texte contrôlé ; densité minimale :',min(p['effective_dpi'] for p in placed),'dpi')
