from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import pymupdf
for n,f in [('Sans','arial.ttf'),('Bold','arialbd.ttf'),('Book','times.ttf'),('Hand','segoepr.ttf')]:
    pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f))
ROOT.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'signalement_objet_manquant_SALON-07.pdf'
W,H=A4;c=canvas.Canvas(str(OUT),pagesize=A4)
c.setTitle('Signalement d’un objet manquant - SALON-07');c.setAuthor('Responsable du lieu de réception')
INK=HexColor('#333b36');MID=HexColor('#778073');RULE=HexColor('#cbd1c5')
c.setFillColor(HexColor('#faf9f2'));c.rect(0,0,W,H,fill=1,stroke=0)
def txt(x,y,s,font='Sans',size=9,color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawString(x,H-y-size,s)
def line(y):
    c.setStrokeColor(RULE);c.setLineWidth(.5);c.line(47,H-y,W-47,H-y)
def section(y,n,s):
    txt(47,y,n,'Sans',8,MID);txt(73,y,s,'Bold',9)
def para(y,s):
    p=Paragraph(s,ParagraphStyle('body',fontName='Book',fontSize=11.5,leading=16.5,textColor=INK))
    _,h=p.wrap(W-104,200);p.drawOn(c,52,H-y-h);return y+h
txt(47,34,'LIEU DE RÉCEPTION / REGISTRE DES INCIDENTS','Sans',8,MID)
txt(47,62,'Signalement d’un objet manquant','Bold',20)
txt(47,97,'Référence : SALON-07','Sans',9)
txt(340,97,'Rédaction : 19 h 03','Bold',10)
txt(47,118,'Jour de la réception / mariage de Lyna Remali et Clément Goldstein','Sans',9,MID)
line(145)
section(163,'01','PERSONNES PORTANT LE SIGNALEMENT')
txt(52,186,'Déclarant : Lucie Renaud, personnel de service','Sans',10)
txt(52,208,'Responsable du lieu : Marc Valette','Sans',10)
section(249,'02','OBJET ET EMPLACEMENT')
para(271,'Anneau cérémoniel déclaré conservé dans un écrin sombre posé sur la commode du salon réservé aux mariés. Écrin de petit format, à couvercle articulé, revêtement sombre et garniture intérieure claire. Lors du constat, l’écrin est ouvert ; son logement ne contient pas l’anneau.')
section(356,'03','VÉRIFICATIONS RAPPORTÉES ET CONSTAT')
txt(52,381,'Vers 18 h 28 / présence rapportée','Bold',10)
para(401,'Adrien de Montfaucon déclare avoir vu l’anneau dans l’écrin lorsqu’il rapporte un objet demandé par Lyna. L’horaire est donné comme approximatif.')
txt(52,450,'18 h 50 / premier constat formel de l’écrin vide','Bold',10)
para(470,'Lucie Renaud constate que le logement de l’écrin ne contient pas l’anneau et en informe le responsable du lieu. Cet horaire désigne le constat de l’absence ; l’heure à laquelle l’objet a quitté l’écrin n’est pas déterminée.')
para(536,'La plage comprise entre la dernière vérification rapportée et le premier constat demeure indéterminée.')
section(592,'04','MESURES IMMÉDIATES')
for i,s in enumerate(['Limiter l’accès au salon aux personnes autorisées par les mariés.','Demander la vérification des effets et objets trouvés remis au service.','Conserver les images disponibles et leurs fichiers d’origine.']):
    y=617+i*24
    c.setStrokeColor(MID);c.setLineWidth(.5);c.rect(53,H-y-10,8,8,fill=0,stroke=1)
    c.setLineWidth(.8);c.line(54,H-y-6,57,H-y-9);c.line(57,H-y-9,62,H-y-2)
    txt(73,y,s,'Sans',9)
line(706)
txt(52,726,'Déclarant / lu et maintenu','Sans',8,MID)
txt(337,726,'Responsable du lieu','Sans',8,MID)
txt(60,750,'Lucie Renaud','Hand',14)
txt(345,750,'M. Valette','Hand',14)
txt(47,801,'SALON-07 / exemplaire conservé au registre','Sans',8,MID)
txt(W-71,801,'1 / 1','Sans',8,MID)
c.showPage();c.save()
doc=pymupdf.open(OUT);assert len(doc)==1
text=doc[0].get_text();assert '18 h 42' not in text
for s in ['19 h 03','18 h 50','18 h 28','demeure indéterminée','Lucie Renaud']:
    assert s in text,s
for s in ['coupable','suspect','preuve','indice','joueurs']:
    assert s not in text.lower(),s
doc[0].get_pixmap(dpi=110).save(ROOT/'verification_A4.png')
doc[0].get_pixmap(dpi=300).save(ROOT/'signalement_SALON-07_300dpi.png')
(ROOT/'texte_signalement.txt').write_text(text,encoding='utf-8')
(ROOT/'production.json').write_text(json.dumps({'declarant':'Lucie Renaud','fonction':'personnel de service','responsable':'Marc Valette','constat':'18 h 50','redaction':'19 h 03','reference':'SALON-07'},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT)
