from pathlib import Path
import sys,math,json
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
for n,f in [('Sans','arial.ttf'),('Bold','arialbd.ttf'),('Book','times.ttf'),('Italic','timesi.ttf'),('Mono','consola.ttf'),('Hand','segoepr.ttf')]:
    pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f))
ROOT.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'compatibilite_structurelle_ancres_AT-NI-88.pdf'
W,H=A4;c=canvas.Canvas(str(OUT),pagesize=A4)
c.setTitle('Compatibilité structurelle des ancres de continuité');c.setAuthor('Institut des Structures Temporelles')
INK=HexColor('#303a3c');MID=HexColor('#737e7a');LINE=HexColor('#c7cfc6')
def txt(x,y,s,font='Sans',size=10,color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawString(x,H-y-size,s)
def line(y,x=48,x2=W-48):
    c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(x,H-y,x2,H-y)
def para(y,s):
    p=Paragraph(s,ParagraphStyle('p',fontName='Book',fontSize=11.5,leading=16.5,textColor=INK))
    _,hh=p.wrap(W-96,300);p.drawOn(c,48,H-y-hh);return y+hh
def section(y,s):txt(48,y,s,'Bold',11)
def base(n,heading):
    c.setFillColor(HexColor('#f8f8f1'));c.rect(0,0,W,H,fill=1,stroke=0)
    # Folded to pocket dimensions; no damage over the technical text.
    for yy in [H/3,2*H/3]:
        for off,col in [(-1,'#efeee4'),(0,'#dedfd4'),(1,'#fffef8')]:
            c.setStrokeColor(HexColor(col));c.setLineWidth(.4);c.line(25,yy+off,W-25,yy+off)
    for off,col in [(-1,'#efeee4'),(0,'#dedfd4'),(1,'#fffef8')]:
        c.setStrokeColor(HexColor(col));c.setLineWidth(.4);c.line(W/2+off,25,W/2+off,H-25)
    txt(48,32,'INSTITUT DES STRUCTURES TEMPORELLES','Sans',8,MID)
    txt(48,56,'Compatibilité structurelle','Bold',21)
    txt(48,83,'des ancres de continuité','Bold',21)
    txt(48,119,'BULLETIN AT-NI/88 / série Ancrage / révision 06','Mono',8,MID)
    line(145);txt(48,164,heading,'Bold',13)
    line(783);txt(48,797,'AT-NI/88 / exemplaire de consultation 017','Mono',8,MID)
    txt(W-78,797,f'{n} / 4','Mono',8,MID)
def network(cx,cy,r,phase,label):
    c.setStrokeColor(INK);c.setLineWidth(.6)
    pts=[]
    for k in range(6):
        a=k*math.pi/3+phase;pts.append((cx+r*math.cos(a),H-cy+r*math.sin(a)))
    for i,j in [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0),(0,3),(1,4),(2,5)]:
        c.line(*pts[i],*pts[j])
    c.setFillColor(HexColor('#f8f8f1'))
    for x,y in pts:c.circle(x,y,3,fill=1,stroke=1)
    c.circle(cx,H-cy,7,fill=1,stroke=1)
    txt(cx-42,cy+r+19,label,'Mono',9)
def table(y,headers,rows,widths):
    xs=[48]
    for w in widths:xs.append(xs[-1]+w)
    for i,(cells,bold) in enumerate([(headers,True)]+[(row,False) for row in rows]):
        yy=y+i*37
        if bold:
            c.setFillColor(HexColor('#e9ede4'));c.rect(48,H-yy-31,sum(widths),31,fill=1,stroke=0)
        for x,s in zip(xs,cells):txt(x+8,yy+8,s,'Bold' if bold else 'Sans',9)
        line(yy+32)

base(1,'1. Domaine et signature historique')
para(205,'Une ancre maintient une relation structurelle avec l’histoire qui l’a constituée. Sa forme matérielle ne décrit pas cette relation : deux objets de même composition peuvent porter des signatures historiques incompatibles. Le présent bulletin traite des retraits, du transport et des tentatives de substitution entre branches distinctes.')
section(299,'Définitions de travail')
para(323,'H désigne la structure historique d’une branche ; A son ancre ; s(A) la signature d’ancrage ; K(A,H) la compatibilité structurelle. K = 1 signifie que la signature satisfait les contraintes propres à H. Une ressemblance de forme ou d’énergie ne suffit pas à établir K = 1.')
txt(83,405,'K(A,H) = 1  si  s(A) = s(H)','Mono',12)
txt(83,433,'s(H1) ≠ s(H2)  =>  K(A1,H2) = 0','Mono',12)
network(171,559,58,0,'H1 / A1');network(420,559,58,.28,'H2 / A2')
txt(245,551,'s(H1) ≠ s(H2)','Mono',9)
txt(48,657,'Figure 1. Deux structures distinctes et leurs relations internes.','Italic',10)
para(693,'La compatibilité est définie par la signature complète. Les relations dessinées ci-dessus représentent des contraintes abstraites ; elles ne constituent pas un itinéraire de transfert.')
c.showPage()

base(2,'2. Classes et comportement au retrait')
para(205,'La classification ci-dessous décrit l’état de liaison. Elle ne constitue pas une échelle de valeur des objets. Le retrait d’une ancre active rompt la relation avec sa branche d’origine tant que cette relation n’est pas rétablie dans sa fenêtre de stabilité.')
table(292,['Classe','Liaison historique','Substitution'],[
['A / active','Signature propre maintenue','Autre histoire : non'],
['R / retirée','Relation interrompue','Autre histoire : non'],
['T / transportée','Objet contenu, liaison suspendue','Autre histoire : non'],
['E / effondrée','Structure humaine effacée','Reconstruction : non']], [98,232,169])
section(513,'Cas d’étude LC : anneau cérémoniel')
para(539,'L’anneau associé à l’union de Lyna Remali et Clément Goldstein appartient à la classe A au sein de sa séquence. Son extraction déstabiliserait la chronologie d’origine. Le déplacer vers une autre branche ne transfère ni la filiation ni les événements liés à cette union.')
para(625,'L’introduction de cet anneau dans une chronologie déjà effondrée ne reconstruirait pas les personnes disparues ni les événements perdus. La présence d’une ancre active étrangère ne restitue pas la structure historique qui a cessé de se maintenir.')
txt(92,720,'K(A_LC,H_effondrée) = 0','Mono',12)
c.showPage()

base(3,'3. Réceptacle et limites du transport')
para(205,'Un réceptacle protège le porteur et l’objet pendant le transport. Il réduit leur exposition aux perturbations locales ; il ne modifie pas la signature historique de l’ancre. Un objet correctement isolé reste lié à son histoire d’origine.')
c.setStrokeColor(INK);c.setLineWidth(.8)
c.roundRect(211,H-463,172,145,18,fill=0,stroke=1)
c.roundRect(223,H-451,148,121,14,fill=0,stroke=1)
c.circle(297,H-390,28,fill=0,stroke=1)
txt(277,383,'A_LC','Mono',11)
txt(251,474,'Volume isolé','Mono',10)
txt(48,508,'Figure 2. Isolation du volume ; la signature s(A) reste inchangée.','Italic',10)
section(547,'Fonctions séparées')
table(573,['Fonction','Effet du réceptacle'],[
['Protection du porteur','Oui, pendant le transport'],
['Protection matérielle de l’objet','Oui, selon les conditions de confinement'],
['Substitution entre histoires','Aucun effet'],
['Reconstruction après effondrement','Aucun effet']], [215,284])
c.showPage()

base(4,'4. Synthèse et fiche de circulation')
para(205,'Deux ancres liées à des histoires différentes ne sont pas interchangeables. L’isolation matérielle et la compatibilité historique sont deux propriétés indépendantes. Aucun contenant ne convertit une signature d’ancrage en une autre.')
para(286,'Dans le cas LC, le retrait de l’anneau déstabiliserait sa chronologie d’origine. Son introduction dans une branche effondrée ne ramènerait ni les personnes ni les événements perdus. Un réceptacle protège uniquement le porteur et l’objet au cours du transport ; il ne réalise aucune substitution.')
txt(48,398,'aucune restitution des structures humaines effacées','Book',12)
c.setStrokeColor(HexColor('#85847b'));c.setLineWidth(.65)
p=c.beginPath();p.moveTo(47,H-414);p.curveTo(166,H-415,281,H-413,395,H-415);c.drawPath(p,stroke=1,fill=0)
para(439,'La limite s’applique même lorsque l’ancre transportée est intacte. La conservation d’un objet ne vaut pas conservation de la structure humaine d’une histoire disparue.')
section(536,'Fiche de prêt / exemplaire 017')
table(562,['Consultation','Initiales','Retour'],[['Sur place','', 'Déposé au comptoir']], [227,118,154])
txt(295,609,'M.S.','Hand',14,HexColor('#65675e'))
txt(48,647,'Exemplaire remis plié ; circulation sur place.','Sans',9,MID)
# A light circular contact mark, uneven and unlabelled.
c.setStrokeColor(HexColor('#ddd6c5'));c.setLineWidth(1.5)
c.arc(421,H-739,511,H-649,12,292)
c.setStrokeColor(HexColor('#e5dece'));c.setLineWidth(.7)
c.arc(424,H-736,508,H-652,190,110)
txt(48,732,'Service de documentation / fonds Ancrage / AT-NI/88','Mono',8,MID)
c.showPage();c.save()
doc=pymupdf.open(OUT);assert len(doc)==4
text='\n'.join(p.get_text() for p in doc)
for s in ['M.S.','aucune restitution des structures humaines effacées','ne sont pas interchangeables','Clément Goldstein']:
    assert s in text,s
for s in ['Milo','a renoncé','coupable','suspect','preuve','indice']:
    assert s.lower() not in text.lower(),s
for dpi,folder in [(110,'verification'),(300,'pages_300dpi')]:
    target=ROOT/folder;target.mkdir(exist_ok=True)
    for i,p in enumerate(doc):p.get_pixmap(dpi=dpi).save(target/f'page_{i+1:02}.png')
(ROOT/'texte_bulletin.txt').write_text(text,encoding='utf-8')
(ROOT/'verification.json').write_text(json.dumps({'pages':4,'format':'A4 portrait','export_dpi':300,'texte_et_schemas':'vectoriels','reference':'AT-NI/88','consultation':'initiales manuscrites M.S.'},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT)
