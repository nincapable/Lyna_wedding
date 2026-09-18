from pathlib import Path
import sys,re,html
sys.path.insert(0,str(Path('tmp/pdf-deps').resolve()))
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf
for n,f in [('Body','segoeui.ttf'),('BodyBold','segoeuib.ttf')]:
    pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
s=getSampleStyleSheet()
s.add(ParagraphStyle(name='TextR',fontName='Body',fontSize=10.3,leading=15,spaceAfter=9))
s.add(ParagraphStyle(name='TitleR',fontName='BodyBold',fontSize=23,leading=29,spaceAfter=18))
s.add(ParagraphStyle(name='H2R',fontName='BodyBold',fontSize=15,leading=20,spaceBefore=15,spaceAfter=9,keepWithNext=True,textColor=HexColor('#263c45')))
s.add(ParagraphStyle(name='H3R',fontName='BodyBold',fontSize=12,leading=17,spaceBefore=10,spaceAfter=7,keepWithNext=True))
source=Path('prototype_v1/rapport_enquete_complet.md')
out=Path('documents_a_imprimer/A4/20_Rapport_enquete_resolution.pdf')
story=[]
for block in source.read_text(encoding='utf-8').split('\n\n'):
    if not block.strip():continue
    style='TextR'
    for prefix,st in [('### ','H3R'),('## ','H2R'),('# ','TitleR')]:
        if block.startswith(prefix):block=block[len(prefix):];style=st;break
    text=html.escape(block).replace('\n',' ')
    text=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',text)
    story.append(Paragraph(text,s[style]))
def footer(c,d):
    c.setFont('Body',8);c.setFillColor(HexColor('#637078'))
    c.drawString(43,23,'Résolution — réservé à l’organisation')
    c.drawRightString(A4[0]-43,23,str(d.page))
SimpleDocTemplate(str(out),pagesize=A4,leftMargin=43,rightMargin=43,topMargin=40,bottomMargin=43,title='Rapport d’enquête — disparition de l’anneau').build(story,onFirstPage=footer,onLaterPages=footer)
qa=Path('tmp/rapport_enquete');qa.mkdir(exist_ok=True)
with pymupdf.open(out) as doc:
    for i,p in enumerate(doc):
        p.get_pixmap(dpi=85).save(qa/f'page_{i+1}.png')
    print(len(doc),'pages')
