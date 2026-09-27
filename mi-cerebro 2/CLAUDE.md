# mi cerebro — Eriks Lernsystem

Diese Datei liest du am Anfang jeder Sitzung. Sie erklärt, wie das Projekt funktioniert.

## Wer und wofür

Erik, Gymnasium NRW, Abitur 2028. Spanisch in Q1 (Cornelsen ¡Vamos!), später weitere
Fächer. Antworten auf **Deutsch**, einfache Formulierungen, keine Zeitformen, die im
Unterricht noch nicht dran waren.

## Das Grundprinzip

**Inhalt und Darstellung sind getrennt.**

```
inhalte/   ← hier wird gepflegt (Markdown, von Hand)
   ↓  python3 build.py
docs/      ← wird erzeugt (Website, niemals von Hand ändern)
```

**Regel:** Nie eine Datei in `docs/` direkt bearbeiten. Sie wird beim nächsten Build
überschrieben. Ausnahme: `docs/assets/` und `docs/espanol/lernzettel/` — die sind
handgeschrieben und werden nicht überschrieben.

## Ordner

| Pfad | Inhalt | wird erzeugt? |
|---|---|---|
| `inhalte/vokabeln/*.md` | alle Vokabeln, eine Datei pro Thema | nein |
| `inhalte/grammatik/index.md` | Status aller Grammatikthemen | nein |
| `build.py` | erzeugt Website + PDF | nein |
| `docs/assets/style.css` | Design für alle Seiten | nein |
| `docs/assets/core.js` | Leitner, Streak, Timer, Lernbericht | nein |
| `docs/espanol/lernzettel/*.html` | Grammatikseiten, eigenständig | nein |
| `docs/index.html` | Startseite | **ja** |
| `docs/espanol/index.html` | Fach-Dashboard | **ja** |
| `docs/espanol/vokabeln.html` | Karteikarten-Trainer | **ja** |
| `docs/espanol/grammatik.html` | Grammatik-Übersicht | **ja** |
| `docs/pdf/vokabeln-gesamt.pdf` | Vokabelliste zum Ausdrucken | **ja** |

## Vokabelformat

Eine Zeile = eine Karte, vier Felder mit `|` getrennt:

```
la toalla | das Handtuch | Antes cambiábamos las toallas. | Früher wechselten wir die Handtücher.
```

`## Überschrift` bildet eine Gruppe (= ein Deck im Trainer).
Beispielsatz und Übersetzung sind Pflicht — Vokabeln ohne Satz sind totes Wissen.
Beispielsätze nur in Zeitformen, die Erik schon hatte: presente, indefinido,
imperfecto, perfecto.

## Grammatikformat

```
status | thema | datei | kurzbeschreibung
```

`status` ist `fertig` oder `offen`. Bei `offen` bleibt die Datei-Spalte leer.
Das `thema` ist gleichzeitig der Schlüssel für den Fortschritt — es muss **exakt**
mit dem übereinstimmen, was der Lernzettel an `MC.answer()` übergibt.

## Eine neue Grammatikseite bauen

1. HTML nach `docs/espanol/lernzettel/<name>.html`, eigenständig (Design aus einer
   bestehenden Seite übernehmen, Farben und Schriften nicht ändern)
2. Selbsttest am Ende, der bei jeder Antwort `MC.answer('<Thema>', richtig, tag)` aufruft
3. In `inhalte/grammatik/index.md` den Status auf `fertig` setzen und die Datei eintragen
4. `python3 build.py`

Aufbau, der sich bewährt hat: Wozu das Ganze → Formen (Tabellen) → Wann benutzt du es
→ Signalwörter → typischer Aufgabentyp → häufigster Fehler → Selbsttest.

## Ablauf bei neuem Material

1. Erik fotografiert Arbeitsblätter, sie landen in iCloud `Español/00_Inbox`
2. Vokabeln daraus in die passende Datei in `inhalte/vokabeln/` anhängen —
   **alle** Wörter, auch die aus Aufgabenstellungen, nicht nur die auffälligen
3. `python3 build.py`
4. Committen und pushen

## Was NICHT ins Repo gehört

Das Repository ist **öffentlich**. Niemals hochladen:
Scans von Arbeitsblättern oder Klausuren, Namen von Lehrern oder Mitschülern,
Noten, Fortschritts-Backups. Das alles bleibt in iCloud.

## Design

Warmes Papier-Design, festgelegt in `docs/assets/style.css`. Farben und Schriften
nicht verändern — das System soll überall gleich aussehen.
Schriften: Fraunces (Überschriften), Inter (Text).

## Fortschritt

`core.js` speichert alles unter `miCerebro.v2` im localStorage des Browsers:
Leitner-Fächer pro Karte, Trefferquote pro Grammatikthema, Streak, Minuten.
Pro Gerät getrennt. Der Backup-Knopf auf der Startseite exportiert alles als JSON.

Der **Lernbericht-Knopf** auf dem Español-Dashboard kopiert den Stand als Text.
Erik fügt ihn in den Chat ein, daraus entstehen gezielte Übungen.

## Website

GitHub Pages, öffentlich, kostenlos.
Quelle: Branch `main`, Ordner `/docs`.
Adresse: https://erikrissanen7-code.github.io/mi-cerebro/

## Dateinamen in inhalte/vokabeln/

Die Zahl vorn bestimmt die Reihenfolge im Trainer und in der PDF:
`10–19` aktuelles Halbjahr · `20–29` themenübergreifend · `30+` Altbestand.

## Offen

- Die 977 EF-Karten haben noch **keine Beispielsätze** (Feld 3 und 4 sind leer).
  Nach und nach ergänzen, am besten die Unidades, die in der Klausur drankommen.
- Sechs Grammatikthemen stehen noch auf `offen`
- `indefinido-imperfecto.html` und `konjugation.html` melden ihren Selbsttest noch
  **nicht** an `MC.answer()` — dadurch erscheinen sie auf der Grammatikseite als
  „noch nicht getestet". Muss nachgerüstet werden.
- Übungsgenerator: Aufgaben, die sich bei jedem Aufruf neu würfeln
