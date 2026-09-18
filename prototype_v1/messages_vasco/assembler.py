from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
import pymupdf

for n,f in [('Sans','segoeui.ttf'),('Bold','segoeuib.ttf'),('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f))
INK=HexColor('#303432'); GREY=HexColor('#767d78'); RULE=HexColor('#d6dbd5')
style=ParagraphStyle('message',fontName='Sans',fontSize=10.5,leading=14,textColor=INK)
messages=[[
('001','J-3','09:14:06','112:08:31','CENDRE-7','reçu',"Offre CN7-4V82. Objet : l’ancre portée lors de l’union. Paiement en Blemfalrk. Confirmez votre accès avant fixation du montant."),
('002','J-3','09:26:42','112:21:07','V.B.','envoyé',"accès confirmé. Je dois encore examiner les conditions de sortie."),
('003','J-3','09:28:19','112:22:44','CENDRE-7','reçu',"Acompte disponible : 400 Blemfalrk. Solde à la remise après contrôle. Canal de règlement : [7A91:D0F4:8C2E]."),
('004','J-3','09:35:11','112:29:36','V.B.','envoyé',"Acompte reçu. je serai sur place. Aucun engagement sur le transfert à ce stade."),
('005','J-2','16:03:27','143:41:02','CENDRE-7','reçu',"Fenêtre d’accès pendant la photo de groupe, appel entre 18 h 40 et 18 h 43. Salon réservé aux mariés. Écrin sur la commode."),
('006','J-2','16:17:54','143:55:29','V.B.','envoyé',"extraction à évaluer. Il faut un contenant isolant adapté à cette classe d’ancrage. Un étui ordinaire ne convient pas."),
('007','J-2','16:20:08','143:57:43','CENDRE-7','reçu',"Apportez votre contenant. Remise après 21 h 30, verrière nord. Le contrôle précédera le versement du solde."),
('008','J-2','16:31:40','144:09:15','V.B.','envoyé',"Reçu. Transmettez les paramètres de stabilité et les conditions prévues après contrôle.")
],[
('009','J-1','10:06:15','161:12:50','CENDRE-7','reçu',"Paramètres joints : [bloc chiffré 02 / 6F0A:119C:72D8]. Votre tâche s’arrête à la livraison. L’utilisation suivante relève du client."),
('010','J-1','10:19:33','161:26:08','V.B.','envoyé',"Je refuse la destruction de l’ancre. Cette condition vaut aussi après la remise. Votre pièce jointe ne répond pas à ce point."),
('011','J-1','10:22:47','161:29:22','CENDRE-7','reçu',"Le client veut l’objet cette nuit. Les effets sur la branche d’origine seront traités ensuite. [segment illisible / 12 octets]"),
('012','J-1','10:38:02','161:44:37','V.B.','envoyé',"J’exige une garantie de restitution ou de substitution, avec protocole vérifiable. Précisez la compatibilité de la solution proposée."),
('013','J-1','10:41:26','161:48:01','CENDRE-7','reçu',"Pas de délai supplémentaire. Le solde peut être augmenté. Une substitution sera étudiée après réception ; aucune garantie préalable."),
('014','J-1','10:55:09','162:01:44','V.B.','envoyé',"je n’extrais rien sans solution stable. Le contenant protège le transport ; il ne règle pas la continuité d’origine."),
('015','J-1','11:02:18','162:08:53','CENDRE-7','reçu',"Votre accès est confirmé. Nous maintenons le rendez-vous après 21 h 30. Décidez avant la réception."),
('016','J-1','11:14:36','162:21:11','V.B.','brouillon non transmis',"En attente du protocole de stabilisation.")
]]
ROOT.mkdir(parents=True,exist_ok=True)
out=ROOT/'messages_chiffres_vasco_bellini.pdf'
c=canvas.Canvas(str(out),pagesize=A4); W,H=A4
c.setTitle('Relevé d’extraction de messagerie - VB-T09')
c.setAuthor('Unité de contrôle des déplacements')
for page,rows in enumerate(messages):
    c.setFillColor(HexColor('#edf0ed')); c.rect(0,0,W,H,fill=1,stroke=0)
    def text(x,y,s,font='Sans',size=9,color=INK):
        c.setFillColor(color);c.setFont(font,size);c.drawString(x,H-y-size,s)
    def box(x,y,w,h,fill,r=0,stroke=None):
        c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke or fill));c.setLineWidth(.5)
        if r:c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
        else:c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))
    box(23,24,W-46,H-48,'#fafbf8',12,'#bec6bf')
    box(23,24,W-46,113,'#252e29',12)
    box(23,111,W-46,26,'#252e29')
    text(42,36,'NŒUD / 07','Mono',8,HexColor('#cbd6cc'))
    text(350,36,'LOCAL / SUBJECTIF','Mono',8,HexColor('#cbd6cc'))
    for k in range(4):box(521+k*5,43-k*2,2,3+k*2,'#cbd6cc')
    c.setStrokeColor(HexColor('#cbd6cc'));c.setLineWidth(1)
    c.line(45,H-77,38,H-83);c.line(38,H-83,45,H-89)
    c.circle(77,H-83,15,stroke=1,fill=0)
    text(68,76,'C7','Mono',10,HexColor('#f6f8f3'))
    text(102,66,'CENDRE-7','Bold',19,HexColor('#f6f8f3'))
    text(102,94,'canal privé / CN7-4V82 / liaison scellée','Mono',8,HexColor('#b9c7bb'))
    text(41,119,'V.B.   /   ARCHIVE LOCALE','Mono',8,HexColor('#cbd6cc'))
    text(370,119,f'FLUX 0{page+1} / 02','Mono',8,HexColor('#cbd6cc'))
    box(23,137,39,H-185,'#e4e9e3')
    for j,label in enumerate(['01','02','03']):
        yy=160+j*38
        if j==0:box(29,yy-5,27,27,'#c5cec5',5)
        text(35,yy,label,'Mono',8,GREY)
    c.setStrokeColor(HexColor('#adb8ae'));c.setLineWidth(.6)
    c.line(42,H-283,42,H-701)
    for j in range(15):c.line(39,H-283-j*28,45,H-283-j*28)
    y=149
    current=None
    bubble_style=ParagraphStyle('bubble',fontName='Sans',fontSize=10,leading=13,textColor=INK)
    for code,day,loc,sub,sender,status,body in rows:
        if day!=current:
            box(254,y,90,17,'#e9eee7',7)
            text(265,y+3,day+' / réception','Mono',7,GREY)
            y+=24;current=day
        outgoing=sender=='V.B.'
        x=126 if outgoing else 77
        bw=421 if outgoing else 421
        p=Paragraph(body,bubble_style);_,hh=p.wrap(bw-24,100)
        bh=hh+35
        box(x,y,bw,bh,'#e0e7dd' if outgoing else '#f0f2ed',8,'#cbd3c8')
        text(x+12,y+7,sender,'Bold',8.5)
        text(x+bw-43,y+7,'#'+code,'Mono',7,GREY)
        p.drawOn(c,x+12,H-y-21-hh)
        text(x+12,y+bh-11,'LOC '+loc+'  /  SUB '+sub+'  /  '+status,'Mono',6.7,GREY)
        y+=bh+8
    assert y<771,(page,y)
    box(23,778,W-46,40,'#e4e9e3',10)
    text(39,786,'LECTURE SEULE / VB-T09 / LC-09-01','Mono',7,GREY)
    text(39,800,'J : jour de réception · SUB : durée subjective · horloges conservées','Sans',7,GREY)
    text(511,790,f'{page+1}/2','Mono',8,GREY)
    c.showPage()
c.save()
doc=pymupdf.open(out);assert len(doc)==2
alltext='\n'.join(p.get_text() for p in doc)
for s in ['accès confirmé','je serai sur place','extraction à évaluer','je n’extrais rien sans solution stable','brouillon non transmis','En attente du protocole de stabilisation.']:
    assert s in alltext,s
for s in ['suspect','coupable','preuve','matching','joueurs']:
    assert s not in alltext.lower(),s
for dpi,folder in [(110,'verification'),(300,'pages_300dpi')]:
    target=ROOT/folder;target.mkdir(exist_ok=True)
    for i,p in enumerate(doc):p.get_pixmap(dpi=dpi).save(target/f'page_{i+1:02}.png')
(ROOT/'texte_messages.txt').write_text(alltext,encoding='utf-8')
(ROOT/'verification.json').write_text(json.dumps({'pages':2,'format':'A4 portrait','dpi_export':300,'texte_vectoriel':True,'dates':'J-3 à J-1','dernier_statut':'brouillon non transmis'},ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
