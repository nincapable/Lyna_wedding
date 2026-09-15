import sys, json, hashlib, zipfile
from pathlib import Path
sys.path.insert(0,str(Path('.tmp/pdf-libs').resolve()))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import pymupdf

ROOT=Path.cwd(); assets=ROOT/'output/registre_v2'
assets.mkdir(parents=True,exist_ok=True)
for name,file in [('Arial','arial.ttf'),('ArialB','arialbd.ttf'),('Mono','cour.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
people=[
 ('nora','REMALI','Éléonore','Nora','29 ans','F','Cousine éloignée de Lyna.','RS-4827'),
 ('salome','KERN','Salomé','Non renseigné','30-35 ans (est.)','F','Ancienne collègue universitaire de Clément.','RS-1936'),
 ('milo','SARAN','Milo','Non renseigné','35-40 ans (est.)','M','Ami de Clément rencontré en voyage.','RS-7052'),
 ('vasco','BELLINI','Vasco','Non renseigné','Env. 35 ans','M','Invité.','RS-3618'),
 ('gabriel','ORSEN','Gabriel','Non renseigné','50-55 ans (est.)','M','Vieil ami de la famille de Lyna.','RS-9243'),
 ('adrien','DE MONTFAUCON','Adrien','Non renseigné','30-35 ans (est.)','M',"Ami de Clément rencontré lors d’un séjour à l’étranger.",'RS-5681')]

# Lossless extraction only: no redraw, ridge synthesis or retouching.
def extract(source,cols,rows,targets):
    im=Image.open(assets/source)
    for row,col,name in targets:
        box=(round(col*im.width/cols),round(row*im.height/rows),round((col+1)*im.width/cols),round((row+1)*im.height/rows))
        if source=='portraits_atlas.png':
            ys=[0,round(im.height*481/1448),round(im.height*954/1448),im.height]
            box=(box[0]+2,ys[row]+2,box[2]-2,ys[row+1]-2)
        else:
            ys=[0,253,506,760,1014,1260,1536]
            box=(box[0],round(im.height*ys[row]/1536),box[2],round(im.height*ys[row+1]/1536))
        im.crop(box).save(assets/name)
extract('portraits_atlas.png',2,3,[(i//2,i%2,p[0]+'_portrait.png') for i,p in enumerate(people)])
extract('empreintes_atlas.png',3,6,[(i,j,p[0]+'_'+finger+'.png') for i,p in enumerate(people) for j,finger in enumerate(['index_droit','index_gauche','pouce_droit'])])

out=ROOT/'output/pdf/registre_signaletique_v2.pdf'
c=canvas.Canvas(str(out),pagesize=A4); W,H=A4
c.setTitle('Registre signalétique / RS-LC / Fiches individuelles')
c.setAuthor('Bureau des relevés signalétiques')
def text(x,y,s,size=9,font='Arial'):
    c.setFillColorRGB(.09,.09,.09);c.setFont(font,size);c.drawString(x,H-y,s)
def line(x,y,x2,y2):
    c.setStrokeColorRGB(.4,.4,.4);c.setLineWidth(.45);c.line(x,H-y,x2,H-y2)
def rect(x,y,w,h):
    c.setStrokeColorRGB(.4,.4,.4);c.setLineWidth(.45);c.rect(x,H-y-h,w,h)
def band(y,s):
    c.setFillColorRGB(.94,.94,.94);c.rect(40,H-y-20,515,20,fill=1,stroke=0);rect(40,y,515,20);text(48,y+13.5,s,8,'ArialB')
def field(x,y,label,value,size=10):
    text(x,y,label,6.7);text(x,y+16,value,size,'Mono')
def check(x,y,s,checked=False):
    rect(x,y-6,6,6)
    if checked:
        line(x+1,y-5,x+5,y-1);line(x+1,y-1,x+5,y-5)
    text(x+10,y,s,7)
date=sys.argv[1] if len(sys.argv)>1 else '____ / ____ / ______'
for i,(slug,nom,prenom,usage,age,sexe,lien,num) in enumerate(people):
    c.setStrokeColorRGB(.95,.95,.95);c.setLineWidth(.3)
    c.line(4,H-18-i,19,H-7-i);c.line(W-4,20+i,W-18,8+i)
    text(40,35,'SERVICE D’IDENTIFICATION',9,'ArialB')
    text(40,49,'Bureau des relevés signalétiques',8)
    text(428,35,'FORMULAIRE RS-03',8,'Mono');text(428,49,'Série LC / vol. 01',8,'Mono')
    line(40,61,555,61)
    text(40,85,'REGISTRE SIGNALÉTIQUE',17,'ArialB')
    text(40,102,'Relevé individuel d’identité présumée',10)
    rect(40,115,515,37);line(367,115,367,152)
    field(48,127,'RÉFÉRENCE DU DOSSIER','RS-LC / Mariage de Lyna et Clément',9)
    field(376,127,'NUMÉRO DE FICHE',num,10)
    band(165,'01   IDENTITÉ DÉCLARÉE')
    rect(40,185,515,219);line(396,185,396,358)
    declared=prenom+' '+('de Montfaucon' if slug=='adrien' else nom.title())
    if slug=='nora':declared+=' (« Nora »)'
    field(48,199,'IDENTITÉ DÉCLARÉE',declared,10)
    line(40,225,396,225)
    field(48,239,'NOM',nom,10);field(237,239,'PRÉNOM',prenom,10);line(228,225,228,269)
    line(40,269,396,269)
    field(48,283,'ÂGE / ESTIMATION',age,9);field(237,283,'SEXE',sexe,10);line(228,269,228,313)
    line(40,313,396,313);field(48,328,'PRÉNOM D’USAGE / SURNOM',usage,9)
    c.drawImage(str(assets/(slug+'_portrait.png')),410,H-197-142,131,142, preserveAspectRatio=True,anchor='c')
    text(413,350,'ILLUSTRATION SIGNALÉTIQUE',6.8)
    line(40,358,555,358);field(48,372,'QUALITÉ DÉCLARÉE / LIEN AVEC LE MARIAGE',lien,8.1)
    band(416,'02   CONDITIONS DU RELEVÉ')
    rect(40,436,515,60);line(241,436,241,474);line(353,436,353,474)
    field(48,449,'DATE DU RELEVÉ',date,9)
    field(249,449,'HEURE LOCALE',f'19 h {8+i*7:02d}',9)
    field(361,449,'POSTE / AGENT','02 / A.17',9)
    line(40,474,555,474)
    check(48,488,'Premier relevé',True);check(172,488,'Reprise');check(271,488,'Support papier',True);check(410,488,'Encrage noir',True)
    band(508,'03   RELEVÉS DACTYLOSCOPIQUES')
    rect(40,528,515,166)
    for j,(finger,label) in enumerate([('index_droit','INDEX DROIT'),('index_gauche','INDEX GAUCHE'),('pouce_droit','POUCE DROIT')]):
        x=40+j*515/3
        if j:line(x,528,x,694)
        text(x+9,542,label,8,'ArialB');text(x+9,553,'Empreinte roulée',7)
        c.drawImage(str(assets/(slug+'_'+finger+'.png')),x+29,H-565-118,114,118,preserveAspectRatio=True,anchor='c')
    line(40,560,555,560)
    band(706,'04   VISA ET CLASSEMENT')
    rect(40,726,515,65);line(297,726,297,770)
    text(48,739,'SIGNATURE DE LA PERSONNE',7);text(305,739,'VISA DE L’AGENT',7)
    line(40,770,555,770);text(48,784,'Annexes : 0    /    Classement : RS-LC / 01    /    Original papier',7,'Mono')
    text(40,811,'RS-03 / Rév. 02     •     Conservation au dossier',7)
    text(473,811,f'Feuillet {i+1} / 6',8,'Mono')
    c.showPage()
c.save()
doc=pymupdf.open(out)
for i,p in enumerate(doc):p.get_pixmap(matrix=pymupdf.Matrix(1.3,1.3)).save(ROOT/f'.tmp/pdfs/v2-page-{i+1}.png')
alltext='\n'.join(p.get_text() for p in doc).lower()
for word in ['suspect','coupable','preuve','correspondance','matching','indice','murder','énigme']:
    assert word not in alltext,word
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in assets.glob('*.png')}
(assets/'integrite_sha256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(ROOT/'output/registre_maitres_v2.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in assets.iterdir():z.write(p,p.name)
print(out)
print('6 pages; 18 relevés; contrôle textuel terminé.')
