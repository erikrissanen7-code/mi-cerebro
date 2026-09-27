#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mi cerebro · build.py

Liest alles aus  inhalte/  und erzeugt daraus  docs/  (die Website) und die PDFs.

    python3 build.py

Du bearbeitest NIE eine HTML-Datei von Hand. Du bearbeitest nur Markdown
in inhalte/ und laesst danach dieses Skript laufen.
"""
import os, re, json, glob, html

ROOT = os.path.dirname(os.path.abspath(__file__))
INH  = os.path.join(ROOT, "inhalte")
DOCS = os.path.join(ROOT, "docs")
ES   = os.path.join(DOCS, "espanol")
PDF  = os.path.join(DOCS, "pdf")
for d in (ES, PDF, os.path.join(ES, "lernzettel")):
    os.makedirs(d, exist_ok=True)

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;'
         '9..144,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">')


def head(title, css="assets/style.css", extra=""):
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#0E4744">
<title>{html.escape(title)}</title>
{FONTS}
<link rel="stylesheet" href="{css}">
{extra}
</head>
<body>
"""


# ===================================================== Vokabeln einlesen
def read_vocab():
    """inhalte/vokabeln/*.md  ->  [{datei, titel, gruppe, es, de, s, sd}]"""
    out = []
    for path in sorted(glob.glob(os.path.join(INH, "vokabeln", "*.md"))):
        datei = os.path.basename(path)[:-3]
        titel, gruppe = datei, datei
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.startswith("<!--") or not line.strip():
                continue
            if line.startswith("## "):
                gruppe = line[3:].strip(); continue
            if line.startswith("# "):
                titel = line[2:].strip(); gruppe = titel; continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 2:
                print(f"  ! uebersprungen ({datei}): {line[:50]}"); continue
            while len(parts) < 4:
                parts.append("")
            out.append({"datei": datei, "titel": titel, "gruppe": gruppe,
                        "es": parts[0], "de": parts[1], "s": parts[2], "sd": parts[3]})
    return out


# ===================================================== Grammatik einlesen
def read_grammar():
    rows = []
    p = os.path.join(INH, "grammatik", "index.md")
    if not os.path.exists(p):
        return rows
    for line in open(p, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#") or line.startswith("<!--") or not line.strip():
            continue
        parts = [x.strip() for x in line.split("|")]
        while len(parts) < 4:
            parts.append("")
        rows.append({"status": parts[0], "thema": parts[1], "datei": parts[2], "text": parts[3]})
    return rows


# ===================================================== Seite: Vokabeltrainer
def page_vokabeln(cards):
    data = [{"g": c["gruppe"], "es": c["es"], "de": c["de"], "s": c["s"], "sd": c["sd"]} for c in cards]
    extra = """<style>
.decks{display:grid;grid-template-columns:1fr;gap:9px}
.deck{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--teal);
      border-radius:12px;padding:12px 14px;cursor:pointer;text-align:left;font-family:inherit;width:100%}
.deck.hl{border-left-color:var(--gold)}
.deck .u{font-family:'Fraunces',serif;font-weight:600;color:var(--teal-deep);font-size:1rem}
.deck .st{font-size:.76rem;color:var(--soft);margin:3px 0 5px}
.dir{display:flex;gap:7px;margin-bottom:13px}
.dir button{flex:1;border:1px solid var(--line);background:var(--card);color:var(--soft);
  font-family:inherit;font-size:.79rem;font-weight:600;border-radius:10px;padding:9px;cursor:pointer}
.dir button.on{background:var(--teal);color:#fff;border-color:var(--teal)}
#trainer{display:none}
.meta{display:flex;justify-content:space-between;font-size:.77rem;color:var(--soft);margin-bottom:5px}
.kcard{background:var(--card);border:1px solid var(--line);border-radius:18px;min-height:200px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;padding:26px 20px;
  text-align:center;cursor:pointer;margin-top:11px;user-select:none}
.kcard .word{font-family:'Fraunces',serif;font-size:1.6rem;font-weight:600;color:var(--teal-deep);line-height:1.25}
.kcard .hint{color:var(--soft);font-size:.77rem;margin-top:13px}
.kcard .answer{font-size:1.1rem;margin-top:14px;padding-top:14px;border-top:1px solid var(--line);width:100%}
.kcard .ex{margin-top:12px;font-size:.87rem;font-style:italic}
.kcard .exd{font-size:.79rem;color:var(--soft);margin-top:2px}
.boxtag{font-size:.7rem;color:var(--soft);margin-bottom:8px}
.fin{text-align:center;padding:26px 18px;background:var(--card);border:1px solid var(--line);
     border-radius:18px;margin-top:12px}
.fin .big{font-family:'Fraunces',serif;font-size:2.2rem;font-weight:600;color:var(--teal-deep)}
.fin .msg{color:var(--soft);margin:4px 0 14px;font-size:.88rem}
</style>"""
    return head("Vokabeln · Español", "../assets/style.css", extra) + f"""
<div class="backbar"><a href="index.html">← Español</a></div>
<header class="hero"><div class="in">
  <h1>Vokabeln</h1>
  <p>{len(data)} Karten · was du kannst, kommt seltener — was wackelt, kommt morgen wieder.</p>
</div></header>
<div class="wrap">
  <section id="picker">
    <h2>Richtung</h2>
    <div class="dir" id="dir">
      <button data-d="es" type="button">Spanisch → Deutsch</button>
      <button class="on" data-d="de" type="button">Deutsch → Spanisch</button>
    </div>
    <div class="note note-info">Deutsch → Spanisch ist schwerer und bringt mehr: In der Klausur musst du
    selbst produzieren, nicht wiedererkennen.</div>
    <h2>Was übst du?</h2>
    <div class="sub">In Klammern: wie viele Karten heute dran sind.</div>
    <div class="decks" id="decks"></div>
  </section>
  <section id="trainer">
    <div style="display:flex;gap:9px;align-items:center;margin-bottom:11px">
      <button class="btn btn-soft" style="width:auto;padding:7px 12px;font-size:.78rem" type="button" onclick="showPicker()">← zurück</button>
      <span style="flex:1;font-weight:600;color:var(--teal-deep);font-size:.9rem" id="tt"></span>
    </div>
    <div class="meta"><span id="counter"></span><span id="sc"></span></div>
    <div class="bar"><i id="pbar" style="width:0%"></i></div>
    <div id="slot"></div><div id="ctrl"></div>
  </section>
</div>
<footer>Leitner · Fach 1 heute · 2 in 2 Tagen · 3 in 4 · 4 in 8 · 5 in 16</footer>
<script src="../assets/core.js"></script>
<script>
const CARDS={json.dumps(data, ensure_ascii=False)};
const GROUPS={{}}; CARDS.forEach((c,i)=>{{(GROUPS[c.g]=GROUPS[c.g]||[]).push('es:'+c.es)}});
const ID=i=>'es:'+CARDS[i].es;
let DIR='de',queue=[],pos=0,right=0,wrong=0,flip=false;
const byId={{}}; CARDS.forEach(c=>byId['es:'+c.es]=c);

function renderPicker(){{
  const all=CARDS.map(ID);
  let h='<button class="deck hl" type="button" onclick="start(\\'due\\')"><div class="u">Heute fällig</div>'
   +'<div class="st">'+MC.dueList(all).length+' Karten · '+MC.boxStats(all).percent+' % sicher</div>'
   +'<div class="bar"><i style="width:'+MC.boxStats(all).percent+'%"></i></div></button>';
  for(const g in GROUPS){{const ids=GROUPS[g],b=MC.boxStats(ids);
    h+='<button class="deck" type="button" onclick="start('+JSON.stringify(g)+')"><div class="u">'+g+'</div>'
      +'<div class="st">'+ids.length+' Karten ('+MC.dueList(ids).length+' fällig) · '+b.percent+' % sicher</div>'
      +'<div class="bar"><i style="width:'+b.percent+'%"></i></div></button>';}}
  document.getElementById('decks').innerHTML=h;
}}
const shuffle=a=>{{a=a.slice();for(let i=a.length-1;i>0;i--){{const j=Math.random()*(i+1)|0;[a[i],a[j]]=[a[j],a[i]]}}return a}};
function start(w){{
  let ids = w==='due' ? MC.dueList(CARDS.map(ID)) : shuffle(GROUPS[w]);
  if(!ids.length){{alert('Nichts fällig – alles aktuell. Wähl eine Gruppe, wenn du trotzdem üben willst.');return}}
  queue=ids.slice(0,40);pos=0;right=0;wrong=0;flip=false;
  picker.style.display='none';trainer.style.display='block';
  document.getElementById('tt').textContent = w==='due'?'Heute fällig':w;
  draw();scrollTo(0,0);
}}
function showPicker(){{trainer.style.display='none';picker.style.display='block';renderPicker();scrollTo(0,0)}}
function draw(){{
  if(pos>=queue.length)return done();
  const c=byId[queue[pos]],st=MC.card(queue[pos]);
  const f=DIR==='es'?c.es:c.de,b=DIR==='es'?c.de:c.es;
  counter.textContent='Karte '+(pos+1)+' von '+queue.length;
  sc.textContent=right+' sicher · '+wrong+' nochmal';
  pbar.style.width=Math.round(pos/queue.length*100)+'%';
  slot.innerHTML='<div class="kcard" onclick="turn()"><div class="boxtag">'+(st?'Fach '+st.box:'neu')+'</div>'
   +'<div class="word">'+f+'</div>'
   +(flip?'<div class="answer">'+b+'</div>'+(c.s?'<div class="ex">'+c.s+'</div><div class="exd">'+c.sd+'</div>':'')
         :'<div class="hint">Antippen zum Umdrehen</div>')+'</div>';
  ctrl.innerHTML=flip
   ?'<div class="btnrow"><button class="btn btn-again" type="button" onclick="mark(false)">Nochmal</button>'
    +'<button class="btn btn-ok" type="button" onclick="mark(true)">Kann ich</button></div>'
   :'<div class="btnrow"><button class="btn btn-soft" type="button" onclick="turn()">Antwort zeigen</button></div>';
}}
function turn(){{flip=true;draw()}}
function mark(ok){{MC.grade(queue[pos],ok);if(ok)right++;else{{wrong++;queue.push(queue[pos])}}pos++;flip=false;draw()}}
function done(){{
  const p=right+wrong?Math.round(right/(right+wrong)*100):0;
  const m=p>=85?'Sitzt. Die sicheren Karten kommen erst in ein paar Tagen wieder.'
        :p>=60?'Solide. Die schwachen siehst du morgen erneut.'
        :'Viele wackeln noch – genau die kommen morgen wieder. Das ist normal.';
  slot.innerHTML='<div class="fin"><div class="big">'+p+' %</div><div class="msg">'+m+'</div>'
   +'<div style="font-size:.84rem;color:var(--soft)">'+right+' sicher · '+wrong+' zurück auf Fach 1</div></div>';
  ctrl.innerHTML='<div class="btnrow"><button class="btn btn-soft" type="button" onclick="showPicker()">Fertig</button></div>';
  pbar.style.width='100%';counter.textContent='Durch';sc.textContent='';
}}
dir.addEventListener('click',e=>{{const b=e.target.closest('button');if(!b)return;DIR=b.dataset.d;
  [...dir.querySelectorAll('button')].forEach(x=>x.classList.toggle('on',x===b))}});
renderPicker();
</script>
</body></html>"""


# ===================================================== Seite: Grammatik-Übersicht
def page_grammatik(rows):
    fertig = [r for r in rows if r["status"] == "fertig"]
    offen  = [r for r in rows if r["status"] != "fertig"]
    tiles = ""
    for r in fertig:
        tiles += (f'<a class="tile" href="{r["datei"]}" data-topic="{html.escape(r["thema"])}">'
                  f'<div class="n">{html.escape(r["thema"])} <span class="badge ok">fertig</span></div>'
                  f'<div class="d">{html.escape(r["text"])}</div>'
                  f'<div class="d stand" style="margin-top:5px"></div></a>\n')
    for r in offen:
        tiles += (f'<div class="tile dim"><div class="n">{html.escape(r["thema"])} '
                  f'<span class="badge open">offen</span></div>'
                  f'<div class="d">{html.escape(r["text"])}</div></div>\n')
    return head("Grammatik · Español", "../assets/style.css") + f"""
<div class="backbar"><a href="index.html">← Español</a></div>
<header class="hero"><div class="in">
  <h1>Grammatik</h1>
  <p>Alle Themen bis zum Abitur — was fertig ist, was noch kommt, und wie du stehst.</p>
  <div class="chip" id="fortschritt">{len(fertig)} von {len(rows)} Themen aufbereitet</div>
</div></header>
<div class="wrap">
  <section>
    <h2>Deine Themen</h2>
    <div class="sub">Grammatikseiten sind zum <b>Nachschlagen</b> da, nicht zum Auswendiglernen.
    Der Selbsttest auf jeder Seite zählt in deinen Fortschritt.</div>
    {tiles}
  </section>
  <section>
    <div class="bar" style="height:10px"><i style="width:{round(len(fertig)/max(1,len(rows))*100)}%"></i></div>
    <div class="sub" style="margin-top:7px">Grammatik ist ein Projekt mit Ende. Wenn alle Themen stehen,
    ist dieser Teil für das Abitur abgehakt.</div>
  </section>
</div>
<footer>Grammatik · <b>mi cerebro</b></footer>
<script src="../assets/core.js"></script>
<script>
document.querySelectorAll('.tile[data-topic]').forEach(function(t){{
  var s=MC.score(t.dataset.topic), el=t.querySelector('.stand');
  el.textContent = s ? ('Dein Stand: '+s.percent+' % · zuletzt vor '+s.daysAgo+' Tagen')
                     : 'Noch nicht getestet';
  el.style.color = s && s.percent<70 ? 'var(--terra)' : 'var(--soft)';
}});
</script>
</body></html>"""


# ===================================================== Seite: Español-Dashboard
def page_espanol(cards, rows, pdfs=None):
    fertig = [r for r in rows if r["status"] == "fertig"]
    topics = {r["thema"]: r["thema"] for r in fertig}
    decks = {}
    for c in cards:
        decks.setdefault(c["gruppe"], []).append("es:" + c["es"])
    pdftiles = ""
    for name, n, titel in (pdfs or []):
        pdftiles += (f'<a class="tile" href="../pdf/{name}"><div class="n">{html.escape(titel)}</div>'
                     f'<div class="d">{n} Vokabeln als PDF</div></a>\n')
    return head("Español · mi cerebro", "../assets/style.css") + f"""
<div class="backbar"><a href="../index.html">← Startseite</a></div>
<header class="hero"><div class="in">
  <h1>Español</h1>
  <p>Cornelsen ¡Vamos! · Q1</p>
  <div class="chip" id="pct">–</div>
</div></header>
<div class="wrap">
  <section>
    <h2>Woran du arbeiten solltest</h2>
    <div class="sub">Berechnet aus deinen Übungen – nicht geraten.</div>
    <div id="weak"></div>
  </section>
  <section>
    <h2>Üben</h2>
    <a class="tile" href="vokabeln.html"><div class="n">Karteikarten</div>
      <div class="d" id="dv">{len(cards)} Vokabeln mit Leitner-System</div></a>
    <a class="tile" href="grammatik.html"><div class="n">Grammatik</div>
      <div class="d">{len(fertig)} von {len(rows)} Themen aufbereitet · mit Selbsttest</div></a>
  </section>
  <section>
    <h2>Zum Ausdrucken</h2>
    <div class="sub">Eine Liste pro Thema – damit du nicht 33 Seiten druckst, wenn du eine brauchst.</div>
    {pdftiles}
  </section>
  <section>
    <h2>Archiv</h2>
    <div class="note note-info">Scans, Arbeitsblätter und Klausuren liegen <b>privat</b> im
    iCloud-Ordner <b>Español</b> — nicht hier auf der Website.</div>
  </section>
  <section>
    <h2>Lernbericht</h2>
    <div class="sub">Kopiert deinen Stand als Text. Im Claude-Chat einfügen → du bekommst Übungen,
    die genau auf deine Lücken zielen.</div>
    <button class="btn btn-main" type="button" id="rep">Lernbericht kopieren</button>
  </section>
</div>
<footer>Español · <b>mi cerebro</b></footer>
<script src="../assets/core.js"></script>
<script>
const DECKS={json.dumps(decks, ensure_ascii=False)};
const TOPICS={json.dumps(topics, ensure_ascii=False)};
let all=[]; for(const k in DECKS) all=all.concat(DECKS[k]);
const b=MC.boxStats(all);
pct.textContent=b.percent+' % der Vokabeln sitzen';
dv.textContent=MC.dueList(all).length+' von '+b.total+' heute fällig · '+b.neu+' noch nie gesehen';
const w=MC.weak(TOPICS), e=MC.topErrors(3);
weak.innerHTML = (!w.length && !e.length)
  ? '<div class="note note-info">Noch keine Übungsdaten. Mach einen Selbsttest – danach steht hier, wo es hakt.</div>'
  : w.slice(0,3).map(x=>'<div class="note '+(x.text.includes('%')?'note-warn':'note-info')+'"><b>'+x.label+'</b><br>'+x.text+'</div>').join('')
    + (e.length?'<div class="note note-warn"><b>Wiederkehrende Fehler</b><br>'+e.map(x=>x.tag+' ('+x.count+'×)').join(' · ')+'</div>':'');
rep.addEventListener('click',function(){{MC.copy(MC.report({{label:'Español',decks:DECKS,topics:TOPICS}}),this)}});
</script>
</body></html>"""


# ===================================================== Seite: Startseite
def page_start(cards, rows):
    decks = {}
    for c in cards:
        decks.setdefault(c["gruppe"], []).append("es:" + c["es"])
    topics = {r["thema"]: r["thema"] for r in rows if r["status"] == "fertig"}
    return head("mi cerebro", "assets/style.css") + f"""
<header class="hero"><div class="in">
  <h1 id="greet">¡Hola, <em>Erik</em>!</h1>
  <p id="lead">Dein Lernsystem lädt …</p>
  <div class="chip" id="streak">🔥 –</div>
</div></header>
<div class="wrap">
  <section>
    <h2>Heute</h2>
    <div class="sub">Der Plan wird aus deinem Fortschritt berechnet, nicht aus einem Stundenplan.</div>
    <div class="plan"><div class="head">Session <span>≈ 30 Min</span></div><div id="tasks"></div></div>
  </section>
  <section>
    <h2>Timer</h2>
    <div class="sub">25 Minuten konzentriert, 5 Minuten Pause. Die Zeit zählt in deinen Bericht.</div>
    <div class="timer" id="timer"><div class="clock">25:00</div><div class="lab">Konzentration</div>
      <button type="button">Start</button></div>
  </section>
  <section>
    <h2>Fächer</h2>
    <a class="tile" href="espanol/index.html"><div class="n">🇪🇸 Español</div>
      <div class="d" id="es">{len(cards)} Vokabeln · Grammatik · Übungen</div>
      <div class="bar" style="margin-top:9px"><i id="esbar" style="width:0%"></i></div></a>
    <div class="tile dim"><div class="n">➕ Weiteres Fach</div>
      <div class="d">Ordner kopieren, Inhalte einsetzen – core.js gilt für alle</div></div>
  </section>
  <section>
    <h2>Fortschritt sichern</h2>
    <div class="sub">Liegt in diesem Browser, auf diesem Gerät. Sichere ihn ab und zu.</div>
    <div class="btnrow">
      <button class="btn btn-soft" type="button" onclick="MC.exportData()">Backup speichern</button>
      <button class="btn btn-soft" type="button" onclick="imp.click()">Backup laden</button>
    </div>
    <input type="file" id="imp" accept="application/json" hidden>
  </section>
</div>
<footer>Hecho para <b>Erik</b> · un cerebro, todas las asignaturas</footer>
<script src="assets/core.js"></script>
<script>
const DECKS={json.dumps(decks, ensure_ascii=False)};
const TOPICS={json.dumps(topics, ensure_ascii=False)};
let all=[]; for(const k in DECKS) all=all.concat(DECKS[k]);
const b=MC.boxStats(all), due=MC.dueList(all), s=MC.streak(), t=MC.todayStats();
greet.innerHTML=MC.greeting()+', <em>Erik</em>!';
streak.textContent = s.count ? '🔥 '+s.count+' Tage in Folge' : '🔥 Heute wieder anfangen';
lead.textContent = due.length+' Karten fällig · '+t.minutes+' Min heute gelernt';
esbar.style.width=b.percent+'%';
es.textContent=b.percent+' % der '+b.total+' Vokabeln sitzen sicher';
const w=MC.weak(TOPICS);
const T=[
 {{ic:'🎴',t:due.length?due.length+' Karten fällig':'Alle Karten sind aktuell',
   s:due.length?'Leitner-Trainer · ca. 10 Min':'Trotzdem üben? Such dir eine Gruppe.',h:'espanol/vokabeln.html'}},
 {{ic:'🎯',t:w.length?'Drill: '+w[0].label:'Grammatik-Selbsttest',
   s:w.length?w[0].text:'Noch keine Daten – einmal testen, dann erkennt das System deine Lücken.',h:'espanol/grammatik.html'}},
 {{ic:'✍️',t:'5 eigene Sätze schreiben',
   s:'Mit den neuen Vokabeln · im Chat korrigieren lassen',h:'espanol/vokabeln.html'}}
];
tasks.innerHTML=T.map(x=>'<a class="task" href="'+x.h+'"><div class="ic">'+x.ic+'</div>'
 +'<div><div class="t">'+x.t+'</div><div class="s">'+x.s+'</div></div></a>').join('');
new MC.Timer(document.getElementById('timer'));
imp.addEventListener('change',e=>{{if(!e.target.files.length)return;
  MC.importData(e.target.files[0],ok=>{{alert(ok?'Fortschritt geladen.':'Datei konnte nicht gelesen werden.');if(ok)location.reload()}})}});
</script>
</body></html>"""


# ===================================================== PDF
def build_pdf(cards):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle

    TEAL = colors.HexColor("#0E4744"); SOFT = colors.HexColor("#6B5E48")
    LINE = colors.HexColor("#E7DBC2"); P2 = colors.HexColor("#F4EAD6")
    INK = colors.HexColor("#2B2419")
    h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=17, textColor=TEAL, leading=20, spaceAfter=3)
    sub = ParagraphStyle("sub", fontName="Helvetica", fontSize=8.5, textColor=SOFT, spaceAfter=12)
    h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, textColor=TEAL, spaceBefore=11, spaceAfter=5)
    es = ParagraphStyle("es", fontName="Helvetica-Bold", fontSize=8.8, textColor=TEAL, leading=11)
    de = ParagraphStyle("de", fontName="Helvetica", fontSize=8.8, textColor=INK, leading=11)
    ex = ParagraphStyle("ex", fontName="Helvetica-Oblique", fontSize=7.7, textColor=SOFT, leading=10)

    def one(pfad, titel, items):
        doc = SimpleDocTemplate(pfad, pagesize=A4, leftMargin=16*mm, rightMargin=16*mm,
                                topMargin=15*mm, bottomMargin=15*mm,
                                title=titel + " · mi cerebro", author="Erik")
        story = [Paragraph(titel, h1),
                 Paragraph(f"{len(items)} Vokabeln · erzeugt aus inhalte/vokabeln/", sub)]
        gruppen = []
        for c in items:
            if not gruppen or gruppen[-1][0] != c["gruppe"]:
                gruppen.append((c["gruppe"], []))
            gruppen[-1][1].append(c)
        for name, teil in gruppen:
            rows = [[Paragraph("<b>Español</b>", es), Paragraph("<b>Deutsch</b>", de)]]
            trenner = [1]
            for c in teil:
                trenner.append(len(rows))
                rows.append([Paragraph(c["es"], es), Paragraph(c["de"], de)])
                if c["s"]:
                    rows.append([Paragraph(c["s"], ex), Paragraph(c["sd"], ex)])
            t = Table(rows, colWidths=[85*mm, 85*mm], repeatRows=1)
            st = [("VALIGN", (0,0), (-1,-1), "TOP"), ("TOPPADDING", (0,0), (-1,-1), 2.5),
                  ("BOTTOMPADDING", (0,0), (-1,-1), 2.5), ("LEFTPADDING", (0,0), (-1,-1), 5),
                  ("BACKGROUND", (0,0), (-1,0), P2)]
            for r in sorted(set(trenner)):
                if 0 < r < len(rows):
                    st.append(("LINEABOVE", (0,r), (-1,r), 0.4, LINE))
            t.setStyle(TableStyle(st))
            story += [Paragraph(name, h2), t]
        doc.build(story)

    erzeugt = []
    # eine PDF pro Quelldatei
    nach_datei = {}
    for c in cards:
        nach_datei.setdefault(c["datei"], []).append(c)
    for datei, items in nach_datei.items():
        p = os.path.join(PDF, f"vokabeln-{datei}.pdf")
        one(p, items[0]["titel"], items)
        erzeugt.append((p, len(items), items[0]["titel"]))
    # und eine Gesamtliste
    p = os.path.join(PDF, "vokabeln-gesamt.pdf")
    one(p, "Vokabelliste · alles", cards)
    erzeugt.append((p, len(cards), "Alles zusammen"))
    return erzeugt


# ===================================================== main
def main():
    cards = read_vocab()
    rows = read_grammar()
    print(f"gelesen: {len(cards)} Vokabeln · {len(rows)} Grammatikthemen")

    pdfs = []
    try:
        pdfs = build_pdf(cards)
    except ImportError:
        pass
    pdfmeta = [(os.path.basename(p), n, t) for p, n, t in pdfs]

    open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8").write(page_start(cards, rows))
    open(os.path.join(ES, "index.html"), "w", encoding="utf-8").write(page_espanol(cards, rows, pdfmeta))
    open(os.path.join(ES, "vokabeln.html"), "w", encoding="utf-8").write(page_vokabeln(cards))
    open(os.path.join(ES, "grammatik.html"), "w", encoding="utf-8").write(page_grammatik(rows))
    print("Seiten:  docs/index.html · espanol/index.html · vokabeln.html · grammatik.html")

    if pdfs:
        for p, n, _t in pdfs:
            print(f"PDF:     {os.path.relpath(p, ROOT):<44} {n:>5} Vokabeln")
    else:
        print("PDF:     uebersprungen (pip install reportlab)")

    print("\nFertig. Jetzt committen und pushen.")


if __name__ == "__main__":
    main()
