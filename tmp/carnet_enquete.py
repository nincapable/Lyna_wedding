from pathlib import Path
import sys
sys.path.insert(0,str(Path('tmp/pdf-deps').resolve()))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf

OUT=Path('documents_a_imprimer/A4/21_Carnet_enquete.pdf')
for n,f in [('Text','segoeui.ttf'),('Bold','segoeuib.ttf')]:
    pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f))
W,H=A4
c=canvas.Canvas(str(OUT),pagesize=A4)
c.setTitle('Carnet d’enquête — le mariage de Lyna et Clément')
ink=HexColor('#283b43');grey=HexColor('#66727a');rule=HexColor('#c5cdd1')
page=0
def text(x,y,s,size=10,font='Text',color=ink):
    c.setFont(font,size);c.setFillColor(color);c.drawString(x,H-y,s)
def line(y,x=42,end=W-42):
    c.setStrokeColor(rule);c.setLineWidth(.45);c.line(x,H-y,end,H-y)
def start(title,subtitle):
    global page
    page+=1
    text(42,42,'LE MARIAGE DE LYNA ET CLÉMENT',8,'Bold',grey)
    text(42,79,title,22,'Bold')
    text(42,105,subtitle,10,'Text',grey)
    line(121)
def finish():
    text(42,H-25,'Carnet personnel · aide de jeu',8,'Text',grey)
    text(W-52,H-25,str(page),8,'Text',grey)
    c.showPage()
def section(y,title):text(42,y,title,12,'Bold')
def ruled(y,n,gap=25):
    for i in range(n):line(y+i*gap)
def box(y,h,title):
    c.setStrokeColor(rule);c.setLineWidth(.6);c.rect(42,H-y-h,W-84,h)
    text(53,y+20,title,10,'Bold')
    for yy in range(int(y+47),int(y+h-8),25):line(yy,53,W-53)

start('Carnet d’enquête','Nom ou équipe : __________________________________________')
section(159,'Notre objectif')
text(42,182,'Retrouver l’anneau, comprendre sa disparition et expliquer les faits.')
text(42,202,'Les personnages ne peuvent pas être interrogés. L’enquête repose sur les pièces.',9,'Text',grey)
section(224,'Pour garder les idées claires')
for y,s in [(249,'Noter la pièce et la page d’où vient chaque information.'),(271,'Séparer ce qui est constaté de ce que nous supposons.'),(293,'Distinguer un projet de vol du geste réellement accompli.'),(315,'Comparer les déclarations écrites aux autres pièces disponibles.')]:text(42,y,s,10)
box(350,150,'Ce que nous savons au départ')
box(521,150,'Nos premières questions')
text(42,704,'Repères : fait = observé ou documenté · propos = déclaré · hypothèse = à vérifier',9,'Text',grey)
finish()

for name in ['Éléonore « Nora » Remali','Salomé Kern','Milo Saran','Vasco Bellini','Gabriel Orsen','Adrien de Montfaucon']:
    start(name,'Fiche de personne · compléter à partir des documents')
    text(42,151,'Identité déclarée / lien avec les mariés :',10,'Bold');ruled(180,2)
    text(42,233,'Autres éléments sur son identité · source :',10,'Bold');ruled(260,2)
    text(42,313,'Ce qu’elle cherche à obtenir ou à protéger · pourquoi :',10,'Bold');ruled(340,3)
    text(42,418,'Déplacements rapportés · par qui / dans quelle pièce :',10,'Bold');ruled(447,3)
    text(42,527,'Éléments qui confirment ou contredisent son récit :',10,'Bold');ruled(553,3)
    text(42,635,'Points à vérifier / pièces à consulter ou à comparer :',10,'Bold');ruled(662,4)
    finish()

start('Chronologie','Noter les heures telles qu’elles apparaissent, avec leurs réserves.')
xs=[42,117,257,407,W-42]
headers=['Heure / ordre','Événement ou déplacement','Source','Précision / réserve']
for x,s in zip(xs,headers):text(x+5,151,s,8.5,'Bold')
top=164;bottom=714
for y in range(top,bottom+1,50):line(y)
c.setStrokeColor(rule)
for x in xs:c.line(x,H-top,x,H-bottom)
text(42,747,'Une heure de constat ne donne pas nécessairement l’heure de l’action.',9,'Text',grey)
finish()

start('Les pièces du dossier','Nommer la pièce ; noter ce qu’elle apporte et ce qu’elle ne permet pas de dire.')
for y in [148,346,544]:
    text(42,y,'Pièce / référence : ______________________________________________',11,'Bold')
    text(42,y+27,'Observation précise :',9,'Bold');ruled(y+51,2)
    text(42,y+96,'Ce que nous pouvons en déduire / réserve :',9,'Bold');ruled(y+121,2)
    text(42,y+165,'À rapprocher de : ______________________________________________',9)
finish()

start('Recoupements','Chercher les accords et les contradictions entre les sources.')
for y in [151,354,557]:
    text(42,y,'Question examinée : ____________________________________________',11,'Bold')
    text(42,y+28,'Source A / ce qu’elle indique :',9,'Bold');ruled(y+50,2,21)
    text(42,y+94,'Source B / ce qu’elle indique :',9,'Bold');ruled(y+116,2,21)
    text(42,y+160,'Accord, contradiction ou information manquante :',9,'Bold');line(y+181)
finish()

start('Nos hypothèses','Tester chaque hypothèse en la confrontant aux documents disponibles.')
for y in [149,442]:
    text(42,y,'Hypothèse : __________________________________________________',11,'Bold')
    text(42,y+34,'Qui ? Dans quel but ? Comment ?');ruled(y+60,3)
    text(42,y+136,'Éléments en sa faveur / éléments qui la fragilisent :');ruled(y+163,3)
    text(42,y+239,'Pièces à comparer pour la confirmer ou l’écarter :');line(y+266)
finish()

start('Conclusion de l’équipe','Faire apparaître le raisonnement, pas seulement un nom.')
box(149,75,'Où est l’anneau ? Comment assurer son retour ?')
box(243,75,'Qui a matériellement déplacé l’anneau ?')
box(337,100,'Quel était son mobile ?')
box(456,125,'Reconstitution : ordre des actes, méthode et destination de l’objet')
box(600,140,'Éléments décisifs · autres explications écartées · incertitudes restantes')
finish()
c.save()
qa=Path('tmp/carnet_enquete');qa.mkdir(exist_ok=True)
with pymupdf.open(OUT) as doc:
    for i,p in enumerate(doc):p.get_pixmap(dpi=85).save(qa/f'page_{i+1}.png')
    print(len(doc),'pages')
