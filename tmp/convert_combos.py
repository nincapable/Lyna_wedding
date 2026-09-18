from pathlib import Path
import sys,re,html
sys.path.insert(0,str(Path('tmp/pdf-deps').resolve()))
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Preformatted,KeepTogether,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf

root=Path('documents_a_imprimer/A4')
for name,file in [('Sans','segoeui.ttf'),('Bold','segoeuib.ttf'),('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='HeadingCombo',fontName='Bold',fontSize=12,leading=16,textColor=HexColor('#253c43'),spaceAfter=6))
styles.add(ParagraphStyle(name='BodyCombo',fontName='Sans',fontSize=10.5,leading=15,spaceAfter=7))
styles.add(ParagraphStyle(name='CalcCombo',fontName='Mono',fontSize=9.5,leading=11))
styles.add(ParagraphStyle(name='TitleCombo',fontName='Bold',fontSize=23,leading=29,spaceAfter=16))

def para(s,style='BodyCombo'):
    return Paragraph(html.escape(s),styles[style])

def footer(c,d):
    c.setFont('Sans',8)
    c.setFillColor(HexColor('#66747a'))
    c.drawRightString(A4[0]-40,22,str(d.page))

for kind in ['Combat','Pioche']:
    source=root/f'Combo_&_Codes_{kind}.txt'
    text=source.read_text(encoding='utf-8-sig').strip()
    story=[para(f'Combos et codes — {kind}','TitleCombo'),para('R = +     U = −     B = ×     G = ÷'),Spacer(1,9)]
    if kind=='Combat':
        blocks=[x.strip() for x in text.split('\n\n') if 'Code' in x]
        for i,block in enumerate(blocks,1):
            sequence,result=re.split(r'\s*:\s*(?=\d+dmg)',block,maxsplit=1)
            damage,calc=re.split(r'\s*=>\s*Code\s*:\s*',result,maxsplit=1)
            story.append(KeepTogether([para(f'Combo {i} · {damage.replace("dmg"," dégâts")}','HeadingCombo'),para(sequence),para('Code : '+calc),Spacer(1,18)]))
    else:
        intro=text[text.index('Départ'):text.index('Combo 1')].strip()
        story.extend([para(intro),Spacer(1,8)])
        blocks=re.split(r'(?=Combo \d+\s*:)',text[text.index('Combo 1'):])
        for i,block in enumerate(filter(None,blocks),1):
            header,calculation=re.split(r'Calcul\s*:',block,maxsplit=1)
            label,details=header.split(':',1)
            sequence,result=re.split(r'\s*:\s*(?=\d+\s*[Cc]artes)',details,maxsplit=1)
            count,code=re.split(r'\s*=\s*>\s*Code\s*:\s*',result,maxsplit=1)
            rows=calculation.strip()
            elements=[para(f'{label.strip()} · {count.strip()} · Code {code.strip()}','HeadingCombo'),para(sequence.strip()),Preformatted(rows,styles['CalcCombo']),Spacer(1,12)]
            if i==4: story.extend([PageBreak(),para('Combos et codes — Pioche','TitleCombo')])
            story.append(KeepTogether(elements))
    output=source.with_suffix('.pdf')
    SimpleDocTemplate(str(output),pagesize=A4,leftMargin=40,rightMargin=40,topMargin=35,bottomMargin=35,title=f'Combos et codes - {kind}').build(story,onFirstPage=footer,onLaterPages=footer)
    with pymupdf.open(output) as doc:
        for i,p in enumerate(doc):
            p.get_pixmap(dpi=100).save(Path('tmp')/f'combo_{kind}_{i+1}.png')
        print(kind,len(doc),'pages')
