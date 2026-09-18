from pathlib import Path
import sys, json
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'tmp/pdf-deps'))
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import fitz

ROOT.mkdir(parents=True, exist_ok=True)
for name, file in [('Book','times.ttf'),('Bold','timesbd.ttf'),('Italic','timesi.ttf'),('Sans','segoeui.ttf'),('Hand','segoepr.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+file))
W,H = 595.276,841.89
INK=HexColor('#34352f'); MUTED=HexColor('#76786d')
style=ParagraphStyle('body',fontName='Book',fontSize=11.5,leading=16.6,textColor=INK,alignment=4,spaceAfter=12)
note_style=ParagraphStyle('note',fontName='Book',fontSize=8.8,leading=11.8,textColor=INK)
pages=[
('1. État du dossier et chronologie conservée',[
"La réception donnée à l’occasion du mariage de Lyna Remali et de Clément Goldstein occupe une place limitée dans les récits de son époque. Les travaux consacrés aux continuités familiales lui ont cependant accordé une attention croissante. Cette attention repose sur deux ensembles distincts : les pièces relatives au déroulement de la soirée et les reconstructions, beaucoup plus tardives, des trajectoires issues de l’union. Leur réunion dans un même dossier ne doit pas effacer la différence de leur statut documentaire.",
"L’anneau cérémoniel était conservé dans un écrin sombre, posé sur une commode du salon réservé aux mariés. Une présence rapportée vers 18 h 28 et un constat formel d’absence à 18 h 50 encadrent la partie connue de l’incident. Le second horaire désigne la constatation formelle de l’absence ; il ne date pas le déplacement de l’objet. La plage séparant ces observations demeure indéterminée dans les pièces contemporaines.<super>1</super>",
"L’absence fut constatée avant que l’engagement ne soit scellé. Les documents d’organisation enregistrent un retard et plusieurs modifications de l’ordre prévu pour la cérémonie. Les récits familiaux évoquent des échanges tendus, une recherche dans les pièces voisines et la crainte que l’union ne puisse être célébrée. Ils ne permettent ni de mesurer uniformément l’intensité de ces tensions, ni d’attribuer à tous les invités une même perception de la situation.<super>2</super>",
"L’anneau fut restitué avant 21 h 16. La cérémonie put alors avoir lieu. Cette borne est retenue par l’édition critique du registre cérémoniel ; elle ne constitue pas un horaire à la seconde de la remise matérielle. Les pièces disponibles attestent le rétablissement de la disposition nécessaire à l’union, sans décrire de manière continue les opérations qui le précédèrent.<super>3</super>",
"On peut donc établir une absence temporaire, une interruption du déroulement prévu, puis une restitution antérieure à l’engagement. La description des gestes, des personnes et des lieux intermédiaires exige en revanche une documentation qui n’a pas été conservée dans le fonds consulté."
],[
"1. Archives de la réception, fonds LC, SALON-07, signalement rédigé à 19 h 03 ; copie de conservation, série R/12, f. 7-8.",
"2. Fonds LC, carnet de service, f. 19-21 ; récits familiaux déposés dans la collection Remali, RF/03, pièces 4 et 9. Les récits ont été consignés après la réception.",
"3. Registre cérémoniel LC, f. 32 ; édition critique de l’Institut, RC-LC/2461, notice 17. La restitution y est située avant 21 h 16."
]),
('2. Lacune documentaire et traditions du récit',[
"Le dossier présente une lacune entre le constat de l’absence et la restitution. Les feuillets conservés mentionnent la recherche et la reprise des préparatifs, mais aucune série complète de transmissions n’en relie les étapes. L’absence d’un procès-verbal de remise interdit notamment d’identifier avec certitude la personne qui rapporta l’anneau, le lieu où elle l’avait trouvé ou les conditions dans lesquelles l’objet avait été conservé.<super>4</super>",
"La présente étude n’a pas réussi à déterminer le coupable de la disparition de l’anneau. Le dépouillement des fonds disponibles et l’examen des attributions tardives n’ont permis de retenir aucune identité. Cette absence constitue la principale difficulté du dossier : la restitution est documentée, tandis que l’intervention qui l’a rendue nécessaire demeure sans auteur connu. Les récits tardifs ne comblent pas cette lacune ; aucun document conservé ne suit l’anneau sans interruption depuis l’écrin jusqu’à sa restitution.",
"Les premiers témoignages décrivent surtout une difficulté pratique : retarder l’engagement, préserver l’organisation de la réception et éviter une rupture entre les familles. Les traditions postérieures déplacent l’accent vers la valeur de l’anneau et vers le devenir du couple. La crainte d’une annulation, perceptible dans plusieurs récits, doit ainsi être distinguée d’une décision d’annuler. Aucune décision formelle de cette nature n’est enregistrée.<super>5</super>",
"Deux lectures historiographiques se sont développées. La première considère l’incident comme une contingence domestique dont l’importance provient de la descendance du couple. La seconde l’inscrit dans les études de stabilisation et examine la manière dont une interruption brève peut être intégrée à une séquence durable. Cette seconde approche est une construction analytique ; elle ne restitue pas le savoir des personnes présentes à la réception.<super>6</super>",
"Il serait également excessif de déduire de la célébration finale que toutes les tensions furent résolues pendant la soirée. La reprise de la cérémonie est documentée ; l’apaisement des relations relève de récits plus dispersés. L’état du fonds autorise une chronologie courte de l’événement, sans fournir une histoire complète de ses effets immédiats sur les invités."
],[
"4. Inventaire du fonds LC, révision 2459, section « Réception et service », p. 61-64. Les numéros manquants ne permettent pas de restituer le contenu des pièces perdues.",
"5. Collection Remali, RF/03, pièces 4, 9 et 12 ; registre cérémoniel LC, f. 32-33.",
"6. A. Séverin, Interruptions brèves et continuités familiales, Institut de Continuité Historique, 2446, p. 118-126 ; M. Derval, Études des séquences locales, ICH, 2457, p. 73-81."
]),
('3. Restitution de l’anneau et survie des chronologies',[
"Les analyses de continuité attribuent à l’anneau une fonction d’ancrage au moment de l’union. Selon les reconstructions de l’Institut, son vol, s’il n’avait pas été suivi d’une restitution avant 21 h 16, aurait entraîné l’extinction de plusieurs chronologies dépendantes. L’interruption aurait dépassé la réception et la descendance immédiate du couple : des histoires entières, avec leurs populations et leurs transmissions, auraient cessé de se maintenir.<super>7</super>",
"La restitution appartient aux faits documentés. Les conséquences de son absence sont établies par des modèles rétrospectifs, dont les calculs convergent sur la perte des branches dépendantes. Dans ces modèles, une remise après la fermeture de la fenêtre de stabilisation ne rétablit pas les structures humaines effacées. La borne de 21 h 16 constitue ainsi une limite critique, et non un simple horaire d’organisation de la cérémonie.<super>8</super>",
"La branche Remali, suivie jusqu’à Élise puis Éléonore Remali dans l’arbre de 2187, figure parmi les lignées maintenues. Les réseaux politiques et scientifiques issus de ces transmissions relient à leur tour plusieurs chronologies. Leur conservation dépend de la stabilisation de l’union autour de son ancre. La restitution de l’anneau a préservé cet ensemble de continuités ; la portée exacte de chaque dépendance reste discutée.<super>9</super>",
"L’incapacité à identifier le voleur constitue, dans ce contexte, une lacune majeure. L’étude ne peut déterminer si la personne qui prit l’anneau connaissait sa fonction, avait prévu de le restituer ou avait laissé à un tiers le soin de le rapporter. Ces possibilités décrivent des situations très différentes : une interruption maîtrisée, un retrait durable ou une restitution dont rien ne garantissait l’aboutissement. Les archives ne permettent pas de trancher.",
"La restitution préserve les chronologies dépendantes, mais les archives ne permettent pas d’établir ce qui a assuré le retour de l’anneau dans le délai critique. L’identité du voleur et les conditions de sa décision demeurent inconnues."
],[
"7. ICH, Dossier d’ancrage LC, AC-LC/2465, § 12-19 : reconstructions de non-restitution et extinction des branches dépendantes.",
"8. N. Valère, Stabilisation et transmission des séquences, ICH, 2462, p. 202-219 ; AC-LC/2465, annexe II, fermeture de la fenêtre locale.",
"9. Atelier généalogique, 2187, FR-2187-064 ; ICH, Répertoire des trajectoires secondaires, 2464, notices REM/12-27. La filiation conservée et les dépendances modélisées sont des séries distinctes."
])]

out=ROOT/'notice_historique_disparition_restitution_anneau.pdf'
c=canvas.Canvas(str(out),pagesize=(W,H))
c.setTitle('Le mariage de Lyna et Clément : crise brève et stabilisation de la continuité')
c.setAuthor('Salomé Kern')
for i,(heading,paras,notes) in enumerate(pages):
    c.setFillColor(HexColor('#faf8f1')); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setStrokeColor(HexColor('#ddd8ca')); c.setLineWidth(.5)
    c.line(62,784,W-62,784)
    c.setFillColor(MUTED); c.setFont('Sans',7.6)
    c.drawString(62,797,'INSTITUT DE CONTINUITÉ HISTORIQUE')
    c.drawRightString(W-62,797,'Études de continuité · 2468')
    y=764
    if i==0:
        title=Paragraph('Le mariage de Lyna et Clément :<br/>crise brève et stabilisation de la continuité',ParagraphStyle('title',fontName='Bold',fontSize=18,leading=22,textColor=INK))
        _,hh=title.wrap(W-124,100); title.drawOn(c,62,y-hh); y-=hh+12
        c.setFont('Italic',9.2); c.setFillColor(MUTED); c.drawString(62,y,'Salomé Kern · Histoires locales et transmissions, vol. IV'); y-=26
    else:
        c.setFont('Italic',10); c.setFillColor(MUTED); c.drawString(62,y,'Le mariage de Lyna et Clément'); y-=30
    c.setFont('Bold',11.5); c.setFillColor(INK); c.drawString(62,y,heading); y-=24
    for txt in paras:
        p=Paragraph(txt,style); _,hh=p.wrap(W-124,700); p.drawOn(c,62,y-hh); y-=hh+12
    if i==2:
        personal=Paragraph("Je reviens toujours à cette inconnue. Qui devait le rendre ? Comment laisser tant de vies dépendre d’une personne dont je ne sais rien ? Peut-être que quelqu’un, avec cette même inquiétude, a fini par prendre l’anneau pour être certain de le remettre à temps. Peut-être que ne pas savoir qui l’avait volé a suffi à décider quelqu’un à le faire.<br/>S. K.",ParagraphStyle('personal',fontName='Hand',fontSize=9.8,leading=14,textColor=HexColor('#62635e'),alignment=0))
        _,hh=personal.wrap(W-142,160)
        personal.drawOn(c,72,y-hh-2); y-=hh+14
    note_y=69
    heights=[]
    for note in notes:
        p=Paragraph(note,note_style); _,hh=p.wrap(W-124,100); heights.append((p,hh))
    total=sum(hh+7 for p,hh in heights)
    top=note_y+total
    assert y>top+14,(i,y,top)
    c.setStrokeColor(MUTED); c.line(62,top+11,193,top+11)
    cursor=top
    for p,hh in heights:
        p.drawOn(c,62,cursor-hh); cursor-=hh+7
    c.setFont('Book',11); c.setFillColor(INK); c.drawCentredString(W/2,36,str(214+i))
    if i==0:
        c.saveState(); c.translate(W-24,338); c.rotate(90)
        c.setFillColor(HexColor('#696b67')); c.setFont('Hand',8)
        c.drawString(0,0,'Et si quelqu’un l’avait pris pour être sûr de le rendre ?')
        c.restoreState()
        c.saveState(); c.translate(450,187); c.rotate(-5)
        c.setStrokeColor(HexColor('#889487')); c.setFillColor(HexColor('#889487')); c.setLineWidth(.7)
        c.roundRect(-70,-22,140,44,3,fill=0,stroke=1)
        c.setFont('Sans',7); c.drawCentredString(0,8,'INSTITUT · CONSULTATION')
        c.setFont('Sans',8); c.drawCentredString(0,-4,'17 / 09 / 2468')
        c.setFont('Sans',6); c.drawCentredString(0,-15,'Salle C · ICH / 4-214'); c.restoreState()
    if i==1:
        c.saveState(); c.translate(30,451); c.rotate(90); c.setFillColor(HexColor('#696b67')); c.setFont('Hand',9)
        c.drawString(0,0,'séquence admise : 18 h 42 / avant 21 h 16'); c.restoreState()
    c.showPage()
c.save()
doc=fitz.open(out)
text='\n'.join(p.get_text() for p in doc)
assert len(doc)==3
assert text.count('18 h 42')==1
assert 'Salomé Kern' in text
assert 'n’a pas réussi à déterminer le coupable' in text
for word in ['indice','suspect','preuve','matching','joueurs']:
    assert word.lower() not in text.lower(),word
(ROOT/'texte_notice.txt').write_text(text,encoding='utf-8')
for dpi,folder in [(110,'verification'),(300,'pages_300dpi')]:
    target=ROOT/folder; target.mkdir(exist_ok=True)
    for i,page in enumerate(doc):
        page.get_pixmap(dpi=dpi).save(target/f'page_{214+i}.png')
(ROOT/'verification.json').write_text(json.dumps({'pages':3,'pagination':[214,215,216],'publication':2468,'annotation_unique':True,'export_dpi':300,'format':'A4 portrait'},indent=2),encoding='utf-8')
print(out)

