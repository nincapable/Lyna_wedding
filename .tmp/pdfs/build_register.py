import sys
from pathlib import Path
sys.path.insert(0, str(Path('.tmp/pdf-libs').resolve()))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import fitz

ROOT=Path.cwd()
for name,file in [('Arial','arial.ttf'),('ArialB','arialbd.ttf'),('CourierR','cour.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+file))
out=ROOT/'output/pdf/registre_signaletique.pdf'
c=canvas.Canvas(str(out),pagesize=A4)
c.setTitle('Registre signalétique - Relevés individuels')
c.setAuthor('Bureau des relevés signalétiques')
W,H=A4
def text(x,y,s,size=10,font='Arial'):
    c.setFillColorRGB(.08,.08,.08); c.setFont(font,size); c.drawString(x,H-y,s)
def line(x,y,x2,y2):
    c.setStrokeColorRGB(.34,.34,.34); c.setLineWidth(.5); c.line(x,H-y,x2,H-y2)
def rect(x,y,w,h):
    c.setStrokeColorRGB(.34,.34,.34); c.setLineWidth(.5); c.rect(x,H-y-h,w,h)
def band(y,label):
    c.setFillColorRGB(.94,.94,.94);c.rect(42,H-y-23,511,23,stroke=0,fill=1)
    rect(42,y,511,23);text(51,y+15,label,9,'ArialB')
people=[
('REMALI','Éléonore','Nora','29 ans','F','Cousine éloignée de Lyna.','RS-4827'),
('KERN','Salomé','Néant déclaré','Non renseigné','F','Ancienne collègue universitaire de Clément.','RS-1936'),
('SARAN','Milo','Néant déclaré','Non renseigné','M','Ami de Clément rencontré en voyage.','RS-7052'),
('BELLINI','Vasco','Néant déclaré','Non renseigné','M','Invité ; lien avec les mariés non précisé.','RS-3618'),
('ORSEN','Gabriel','Néant déclaré','Non renseigné','M','Vieil ami de la famille de Lyna.','RS-9243'),
('DE MONTFAUCON','Adrien','Néant déclaré','Non renseigné','M',"Ami de Clément rencontré lors d’un séjour à l’étranger.",'RS-5681')]
for i,(nom,prenom,usage,age,sexe,lien,num) in enumerate(people):
    c.setStrokeColorRGB(.95,.95,.95);c.setLineWidth(.35)
    c.line(5, H-15-i*2, 20, H-6-i*2)
    c.line(W-5, 19+i*3, W-17, 6+i*3)
    text(42,43,'SERVICE D’IDENTIFICATION',10,'ArialB')
    text(42,59,'Bureau des relevés signalétiques',9)
    text(419,43,'SÉRIE RS / 04',9,'CourierR')
    text(419,59,'Exemplaire de service',8)
    line(42,72,553,72)
    text(42,103,'REGISTRE SIGNALÉTIQUE',19,'ArialB')
    text(42,124,'FICHE INDIVIDUELLE DE RELEVÉ DACTYLOSCOPIQUE',10)
    rect(42,144,511,40)
    text(51,160,'DOSSIER',7);text(51,176,'Mariage de Lyna et Clément',10,'CourierR')
    line(368,144,368,184);text(378,160,'N° DE FICHE',7);text(378,176,num,11,'CourierR')
    band(201,'01   IDENTITÉ PRÉSUMÉE / DÉCLARATIONS RECUEILLIES')
    rect(42,224,511,178)
    text(51,240,'IDENTITÉ DÉCLARÉE',7)
    declared=prenom+' '+('de Montfaucon' if i==5 else nom.title())
    if i==0: declared+=' (« Nora »)'
    text(51,259,declared,12,'CourierR')
    line(42,271,553,271)
    text(51,286,'NOM',7); text(51,304,nom,11,'CourierR')
    line(309,271,309,317);text(319,286,'PRÉNOM',7);text(319,304,prenom,11,'CourierR')
    line(42,317,553,317)
    text(51,332,'ÂGE DÉCLARÉ',7);text(51,350,age,10,'CourierR')
    line(237,317,237,361);text(247,332,'SEXE',7);text(247,350,sexe,10,'CourierR')
    line(309,317,309,361);text(319,332,'PRÉNOM D’USAGE / SURNOM',7);text(319,350,usage,10,'CourierR')
    line(42,361,553,361);text(51,376,'QUALITÉ DÉCLARÉE / LIEN AVEC LE MARIAGE',7);text(51,392,lien,9)
    band(421,'02   RELEVÉS DIGITAUX À L’ENCRE')
    rect(42,444,511,194);line(297.5,444,297.5,638)
    text(51,461,'INDEX DROIT / EMPREINTE ROULÉE',8,'ArialB')
    text(307,461,'INDEX GAUCHE / EMPREINTE ROULÉE',8,'ArialB')
    line(42,472,553,472)
    # Place each region by PDF clipping; preserve the original raster asset.
    for j,xc in enumerate([290,732]):
        x=120+j*255.5; top=486; width=100; height=137
        sy=[10,256,510,760,1010,1260][i]
        cropw=230; croph=[245,250,250,250,250,265][i]; scale=min(width/cropw,height/croph)
        rw=cropw*scale;rh=croph*scale
        c.saveState();p=c.beginPath();p.rect(x,H-top-rh,rw,rh);c.clipPath(p,stroke=0)
        left=xc-cropw/2
        c.drawImage(str(ROOT/'output/assets/releves.png'),x-left*scale,H-top-(1536-sy)*scale,width=1024*scale,height=1536*scale)
        c.restoreState()
    band(657,'03   ENREGISTREMENT')
    rect(42,680,511,77)
    text(51,697,'MODE DE RECUEIL',7);text(51,714,'Encrage sur support papier',9,'CourierR')
    text(320,697,'POSTE / AGENT',7);text(320,714,'02 / A.17',9,'CourierR')
    line(42,725,553,725);text(51,744,'ANNEXES : 0',8,'CourierR');text(230,744,'CLASSEMENT : RS / LC',8,'CourierR')
    line(42,784,553,784)
    text(42,800,'RS-02  /  Relevé individuel  /  Conservation au dossier',7)
    text(477,800,f'Feuillet {i+1} / 6',8,'CourierR')
    c.showPage()
c.save()
doc=fitz.open(out)
for i,page in enumerate(doc):
    page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(str(ROOT/f'.tmp/pdfs/page-{i+1}.png'))
print(out)
print('Pages:',len(doc))
