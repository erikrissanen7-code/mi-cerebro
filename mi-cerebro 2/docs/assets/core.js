/* mi cerebro · core.js
   Ein Gedaechtnis fuer alle Seiten: Leitner-Faecher, Streak, Timer, Lernbericht.
   Alles liegt lokal im Browser (localStorage). */
(function (g) {
  'use strict';
  var KEY = 'miCerebro.v2';
  var IV = { 1: 0, 2: 2, 3: 4, 4: 8, 5: 16 };   // Fach -> Tage bis zur Wiederholung

  function blank() {
    return { streak: { count: 0, last: null, best: 0 }, days: {},
             cards: {}, topics: {}, errors: {} };
  }
  var db = (function () {
    try {
      var d = JSON.parse(localStorage.getItem(KEY));
      if (!d) return blank();
      var b = blank(); for (var k in b) if (!(k in d)) d[k] = b[k];
      return d;
    } catch (e) { return blank(); }
  })();
  function save() { try { localStorage.setItem(KEY, JSON.stringify(db)); } catch (e) {} }

  function today() { return new Date().toISOString().slice(0, 10); }
  function addDays(n) { var d = new Date(); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); }
  function gap(a, b) { return Math.round((new Date(b + 'T12:00') - new Date(a + 'T12:00')) / 864e5); }

  /* ---------- Karten ---------- */
  function card(id) { return db.cards[id] || null; }
  function due(id) { var c = db.cards[id]; return !c || c.due <= today(); }
  function grade(id, ok) {
    var c = db.cards[id] || { box: 1, seen: 0, wrong: 0 };
    c.seen++; if (ok) c.box = Math.min(5, c.box + 1); else { c.box = 1; c.wrong++; }
    c.due = addDays(IV[c.box]); db.cards[id] = c; touch('cards', 1); save(); return c;
  }
  function boxStats(ids) {
    var s = { 1:0, 2:0, 3:0, 4:0, 5:0, neu:0, total: ids.length };
    ids.forEach(function (i) { var c = db.cards[i]; if (!c) s.neu++; else s[c.box]++; });
    s.mastered = s[4] + s[5];
    s.percent = ids.length ? Math.round(s.mastered / ids.length * 100) : 0;
    return s;
  }
  function dueList(ids) {
    return ids.filter(due).sort(function (a, b) {
      return ((db.cards[a] || {box:1}).box) - ((db.cards[b] || {box:1}).box);
    });
  }

  /* ---------- Themen (Grammatik) ---------- */
  function answer(topic, ok, tag) {
    var t = db.topics[topic] || { right: 0, wrong: 0, last: null };
    if (ok) t.right++; else t.wrong++;
    t.last = today(); db.topics[topic] = t;
    if (!ok && tag) db.errors[topic + '|' + tag] = (db.errors[topic + '|' + tag] || 0) + 1;
    touch('drills', 1); save();
  }
  function score(topic) {
    var t = db.topics[topic]; if (!t || !(t.right + t.wrong)) return null;
    return { percent: Math.round(t.right / (t.right + t.wrong) * 100),
             total: t.right + t.wrong, daysAgo: t.last ? gap(t.last, today()) : null };
  }
  function weak(labels) {
    var out = [];
    Object.keys(labels || {}).forEach(function (k) {
      var s = score(k), l = labels[k];
      if (!s) { out.push({ k: k, label: l, text: l + ' – noch nie geübt', w: 3 }); return; }
      if (s.percent < 70) out.push({ k: k, label: l, text: l + ' – nur ' + s.percent + ' % richtig', w: 12 - Math.floor(s.percent / 10) });
      else if (s.daysAgo >= 7) out.push({ k: k, label: l, text: l + ' – seit ' + s.daysAgo + ' Tagen nicht geübt', w: 2 + Math.min(4, Math.floor(s.daysAgo / 7)) });
    });
    return out.sort(function (a, b) { return b.w - a.w; });
  }
  function topErrors(n) {
    return Object.keys(db.errors).map(function (k) {
      var p = k.split('|'); return { topic: p[0], tag: p[1], count: db.errors[k] };
    }).sort(function (a, b) { return b.count - a.count; }).slice(0, n || 5);
  }

  /* ---------- Streak & Tag ---------- */
  function touch(what, n) {
    var t = today(), d = db.days[t] || { minutes: 0, cards: 0, drills: 0 };
    d[what] = (d[what] || 0) + (n || 1); db.days[t] = d;
    var s = db.streak;
    if (s.last !== t) {
      s.count = (s.last && gap(s.last, t) === 1) ? s.count + 1 : 1;
      s.last = t; if (s.count > s.best) s.best = s.count;
    }
    save();
  }
  function streak() {
    var s = db.streak;
    if (s.last && gap(s.last, today()) > 1) return { count: 0, best: s.best };
    return { count: s.count, best: s.best };
  }
  function todayStats() { return db.days[today()] || { minutes: 0, cards: 0, drills: 0 }; }

  /* ---------- Pomodoro ---------- */
  function Timer(el, focusMin, breakMin) {
    var F = (focusMin || 25) * 60, B = (breakMin || 5) * 60;
    var left = F, mode = 'focus', tick = null;
    var clock = el.querySelector('.clock'), lab = el.querySelector('.lab'), btn = el.querySelector('button');
    function fmt(s) { var m = s / 60 | 0, r = s % 60; return m + ':' + (r < 10 ? '0' : '') + r; }
    function paint() {
      clock.textContent = fmt(left);
      lab.textContent = mode === 'focus' ? 'Konzentration – Handy weglegen' : 'Pause – aufstehen, Fenster auf';
      el.classList.toggle('running', !!tick); btn.textContent = tick ? 'Pause' : 'Start';
    }
    btn.addEventListener('click', function () {
      if (tick) { clearInterval(tick); tick = null; }
      else tick = setInterval(function () {
        if (--left > 0) return paint();
        clearInterval(tick); tick = null;
        if (mode === 'focus') { touch('minutes', F / 60 | 0); mode = 'break'; left = B; }
        else { mode = 'focus'; left = F; }
        paint();
      }, 1000);
      paint();
    });
    paint();
  }

  /* ---------- Lernbericht ---------- */
  function report(cfg) {
    var L = [], s = streak(), t = todayStats();
    L.push('LERNBERICHT · ' + (cfg.label || 'Español') + ' · ' + today());
    L.push('Streak ' + s.count + ' Tage (Rekord ' + s.best + ') · heute ' + t.minutes + ' Min, ' + t.cards + ' Karten, ' + t.drills + ' Übungen');
    L.push('');
    if (cfg.decks) {
      L.push('VOKABELN:');
      var all = [];
      Object.keys(cfg.decks).forEach(function (n) {
        var ids = cfg.decks[n]; all = all.concat(ids);
        var b = boxStats(ids);
        L.push('  ' + n + ': ' + b.percent + ' % sicher (' + b.mastered + '/' + b.total + ') · Fach 1: ' + b[1] + ' · neu: ' + b.neu + ' · fällig: ' + dueList(ids).length);
      });
      var a = boxStats(all);
      L.push('  GESAMT: ' + a.percent + ' % von ' + a.total + ' Karten');
      L.push('');
    }
    if (cfg.topics) {
      L.push('GRAMMATIK:');
      Object.keys(cfg.topics).forEach(function (k) {
        var sc = score(k);
        L.push('  ' + cfg.topics[k] + ': ' + (sc ? sc.percent + ' % (' + sc.total + ' Aufgaben, vor ' + sc.daysAgo + ' Tagen)' : 'noch nie geübt'));
      });
      L.push('');
      var w = weak(cfg.topics);
      if (w.length) { L.push('SCHWACHSTELLEN:'); w.slice(0, 5).forEach(function (x) { L.push('  - ' + x.text); }); L.push(''); }
    }
    var e = topErrors(6);
    if (e.length) { L.push('HÄUFIGSTE EINZELFEHLER:'); e.forEach(function (x) { L.push('  - ' + x.tag + ' (' + x.topic + '): ' + x.count + '×'); }); L.push(''); }
    L.push('Bitte bau mir gezielte Übungen zu den Schwachstellen.');
    return L.join('\n');
  }

  function copy(text, btn) {
    function ok() {
      if (!btn) return;
      var o = btn.textContent; btn.textContent = '✓ Kopiert – jetzt im Chat einfügen';
      btn.classList.add('done'); setTimeout(function () { btn.textContent = o; btn.classList.remove('done'); }, 2400);
    }
    if (navigator.clipboard && navigator.clipboard.writeText)
      navigator.clipboard.writeText(text).then(ok, function () { fb(text, ok); });
    else fb(text, ok);
  }
  function fb(text, ok) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); ok(); } catch (e) { alert(text); }
    document.body.removeChild(ta);
  }

  function exportData() {
    var b = new Blob([JSON.stringify(db, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(b); a.download = 'mi-cerebro-backup-' + today() + '.json';
    a.click(); URL.revokeObjectURL(a.href);
  }
  function importData(file, cb) {
    var r = new FileReader();
    r.onload = function () { try { db = JSON.parse(r.result); save(); cb(true); } catch (e) { cb(false); } };
    r.readAsText(file);
  }
  function greeting() {
    var h = new Date().getHours();
    return h < 11 ? '¡Buenos días' : h < 19 ? '¡Buenas tardes' : '¡Buenas noches';
  }

  g.MC = { today: today, card: card, due: due, grade: grade, boxStats: boxStats, dueList: dueList,
           answer: answer, score: score, weak: weak, topErrors: topErrors,
           touch: touch, streak: streak, todayStats: todayStats, Timer: Timer,
           report: report, copy: copy, exportData: exportData, importData: importData,
           greeting: greeting };
})(window);
