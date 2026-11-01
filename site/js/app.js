import { prepare, draw, partIcon, shapeOf, VIEWS } from './render.js';

const REPO = 'https://github.com/Savox76/minecraft-tools';
const BASE = document.querySelector('meta[name="site-base"]')?.content || '/';
const main = document.getElementById('inhalt');
const fmt = (n) => Number(n).toLocaleString('de-DE');
const stacks = (n) => { const s = Math.floor(n / 64), r = n % 64; return s ? `${s} St.${r ? ' + ' + r : ''}` : `${r}`; };
const esc = (t) => String(t ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const cssv = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const store = {
  get(k, d) { try { const v = localStorage.getItem('bw.' + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem('bw.' + k, JSON.stringify(v)); } catch { /* privat */ } },
};
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- Thema ---------- */
const themeSaved = store.get('thema', null);
if (themeSaved) document.documentElement.dataset.theme = themeSaved;
document.getElementById('thema').addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme
    ? document.documentElement.dataset.theme === 'dark'
    : matchMedia('(prefers-color-scheme: dark)').matches;
  const next = dark ? 'light' : 'dark';
  document.documentElement.dataset.theme = next; store.set('thema', next);
  redrawAll();
});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => redrawAll());

/* ---------- Daten ---------- */
let KAT = null;
const builds = new Map();
async function katalog() {
  if (!KAT) KAT = await (await fetch(`${BASE}data/katalog.json`)).json();
  return KAT;
}
async function ladeBau(id) {
  if (!builds.has(id)) builds.set(id, fetch(`${BASE}data/builds/${id}.json`).then((r) => r.json()));
  return builds.get(id);
}
const farben = () => ({ fadeTo: cssv('--sheet'), highlight: cssv('--hl'), ground: cssv('--sheet-2'), gridLine: cssv('--line') });

/* ---------- Neu zeichnen bei Größe/Thema ---------- */
let redrawers = [];
function onRedraw(fn) { redrawers.push(fn); }
function redrawAll() { redrawers.forEach((f) => f()); }
let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(redrawAll, 150); });

/* ---------- Bausteine ---------- */
const punkte = (n) => `<span class="punkte" title="Schwierigkeit ${n} von 5" aria-label="Schwierigkeit ${n} von 5">${[1, 2, 3, 4, 5].map((i) => `<i class="${i <= n ? 'an' : ''}"></i>`).join('')}</span>`;
const editionen = (e) => (e || []).map((x) => `<span class="marker ${x}">${x === 'java' ? 'Java' : 'Bedrock'}</span>`).join('');
const stunden = (b) => b && b.length ? `${b[0]}–${b[1]} Std.` : '';
const initialen = (n) => (n.match(/[A-ZÄÖÜ]/g) || [n[0]]).slice(0, 2).join('');

function bauKarte(b) {
  return `<a class="karte" href="${BASE}bau/${b.id}/" data-thumb="${b.id}">
    <div class="bild"><canvas aria-hidden="true"></canvas></div>
    <div class="text">
      <div class="chips">${editionen(b.edition)}${b.status === 'entwurf' ? '<span class="marker entwurf">Entwurf</span>' : ''}</div>
      <h3>${esc(b.titel)}</h3>
      <p>${esc(b.beschreibung)}</p>
      <div class="fakten">${punkte(b.schwierigkeit)}<span><b>${fmt(b.bloecke)}</b> Blöcke</span><span><b>${b.schritte}</b> Schritte</span><span>${stunden(b.bauzeit_stunden)}</span></div>
    </div></a>`;
}
function pluginKarte(p) {
  return `<a class="karte plugin-karte" href="${BASE}plugin/${p.id}/">
    <div class="text">
      <div class="plugin-kopf"><span class="plugin-symbol" aria-hidden="true">${initialen(p.name)}</span>
        <div><h3>${esc(p.name)}</h3><span class="marker">v${esc(p.version)}</span></div></div>
      <p>${esc(p.kurz)}</p>
      <div class="fakten"><span class="marker">${esc(KAT.plugin_kategorien[p.kategorie] || p.kategorie)}</span><span class="marker">${p.befehle.length} Befehle</span>${p.status === 'doku' ? '<span class="marker entwurf">Download folgt</span>' : ''}</div>
    </div></a>`;
}
const docLink = (d) => `<a class="liste-link" href="${BASE}anleitung/${d.id}/"><div><h3>${esc(d.titel)}</h3><p>${esc(d.kurz)}</p></div><span class="pfeil" aria-hidden="true">→</span></a>`;

// Vorschaubilder erst zeichnen, wenn sie sichtbar werden
const thumbObs = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (!e.isIntersecting) return;
    thumbObs.unobserve(e.target);
    const el = e.target, id = el.dataset.thumb;
    ladeBau(id).then((d) => {
      const P = prepare(d.model, { schnitt: d.ansicht?.schnitt });
      const cv = el.querySelector('canvas');
      const paint = () => { if (!cv.isConnected) return; const box = el.querySelector('.bild'); draw(cv, P, { width: box.clientWidth * .92, maxHeight: box.clientHeight * .92, rot: 0, ...farben(), ground: null }); };
      paint(); onRedraw(paint);
    });
  });
}, { rootMargin: '200px' });
function watchThumbs(root) { root.querySelectorAll('[data-thumb]').forEach((el) => thumbObs.observe(el)); }

/* ---------- Seiten ---------- */
async function startSeite() {
  const k = await katalog();
  const sum = k.builds.reduce((a, b) => a + b.bloecke, 0);
  main.innerHTML = `
  <section class="held"><div class="wrap">
    <div>
      <span class="eyebrow">Minecraft-Baupläne · Paper-Plugins</span>
      <h1>Bauen wie mit LEGO. Schritt für Schritt.</h1>
      <p class="lede">Jeder Bauplan zeigt pro Schritt genau, welche Blöcke du brauchst und wo sie hinkommen. Dazu Plugins für deinen eigenen Server. Alles kostenlos und einzeln zum Herunterladen.</p>
      <div class="knoepfe"><a class="btn" href="${BASE}bauplaene/">Baupläne ansehen</a><a class="btn zwei" href="${BASE}wuensche/">Bauplan wünschen</a></div>
      <div class="zahlen">
        <div><b>${k.builds.length}</b><span>Baupläne</span></div>
        <div><b>${fmt(sum)}</b><span>Blöcke geplant</span></div>
        <div><b>${k.plugins.length}</b><span>Plugins</span></div>
        <div><b>${k.docs.length}</b><span>Anleitungen</span></div>
      </div>
    </div>
    <figure class="held-bild" style="margin:0">
      <canvas id="held-cv" aria-label="Animation: Villa am Wasser wird Schritt für Schritt gebaut"></canvas>
      <figcaption class="unter"><span id="held-text">Villa am Wasser</span><a href="${BASE}bau/villa-am-wasser/">Zum Bauplan →</a></figcaption>
    </figure>
  </div></section>
  <section class="abschnitt"><div class="wrap">
    <div class="abschnitt-kopf"><div><h2>Baupläne</h2><p>Türme, Villen und Farmen. Jeder Plan mit LEGO-Schritten, Teileliste und Dateien für Litematica und WorldEdit.</p></div><a class="btn zwei klein" href="${BASE}bauplaene/">Alle Baupläne</a></div>
    <div class="raster">${k.builds.map(bauKarte).join('')}</div>
  </div></section>
  <section class="abschnitt"><div class="wrap">
    <div class="abschnitt-kopf"><div><h2>Eigene Plugins für Paper</h2><p>Shop, Lager, Arbeiter, Admin-Schutz und mehr. Entwickelt für einen fairen Server, auf dem keiner anderen schaden kann.</p></div><a class="btn zwei klein" href="${BASE}plugins/">Alle Plugins</a></div>
    <div class="raster">${k.plugins.slice(0, 4).map(pluginKarte).join('')}</div>
  </div></section>
  <section class="abschnitt"><div class="wrap zwei-spalten">
    <div><div class="abschnitt-kopf"><div><h2>Anleitungen</h2><p>Server-Wissen, das beim Bauen hilft.</p></div></div>${k.docs.map(docLink).join('')}</div>
    <div><div class="abschnitt-kopf"><div><h2>Was soll als Nächstes kommen?</h2><p>Wünsch dir ein Bauwerk. Die meistgewünschten werden zuerst gebaut.</p></div></div>
      ${wunschListe(k, 4)}<div style="margin-top:12px"><a class="btn" href="${BASE}wuensche/">Bauplan wünschen</a></div></div>
  </div></section>`;
  watchThumbs(main);
  heldAnimation();
}

async function heldAnimation() {
  const d = await ladeBau('villa-am-wasser');
  const cv = document.getElementById('held-cv'); if (!cv) return;
  const P = prepare(d.model);
  const stepOf = schrittKarte(P, d.schritte);
  let cur = reduced ? d.schritte.length : 0, timer = null;
  const txt = document.getElementById('held-text');
  const paint = () => {
    if (!cv.isConnected) { clearTimeout(timer); return; }
    const w = cv.parentElement.clientWidth - 28;
    draw(cv, P, { width: w, maxHeight: Math.min(460, w * .8), rot: 0, ...farben(),
      state: (i, x, y, z) => { const s = stepOf[P.at(x, y, z)]; if (s < 0) return 2; return s < cur ? 2 : s === cur ? 3 : 0; } });
    txt.textContent = cur < d.schritte.length ? `Villa am Wasser · Schritt ${cur + 1} von ${d.schritte.length}` : 'Villa am Wasser · fertig';
  };
  const tick = () => {
    cur++; if (cur > d.schritte.length + 12) cur = 0;
    paint(); timer = setTimeout(tick, cur === 0 ? 600 : 140);
  };
  paint(); onRedraw(paint);
  if (!reduced) timer = setTimeout(tick, 600);
}

function schrittKarte(P, schritte) {
  const m = new Int32Array(P.X * P.Y * P.Z).fill(-1);
  schritte.forEach((s, k) => { for (let j = 0; j < s.c.length; j += 4) m[P.at(s.c[j], s.c[j + 1], s.c[j + 2])] = k; });
  return m;
}

async function bauplaeneSeite() {
  const k = await katalog();
  const aktiv = store.get('filter', 'alle');
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <span class="eyebrow">Sammlung</span><h1>Baupläne</h1>
    <p class="lede">Jeder Bauplan gibt es als LEGO-Anleitung im Browser, als Litematica- und WorldEdit-Datei und als Teileliste.</p>
    <div class="chips" style="margin-top:18px" role="group" aria-label="Kategorie filtern">
      ${[['alle', 'Alle'], ...Object.entries(k.kategorien)].map(([id, n]) => `<button class="chip" data-f="${id}" aria-pressed="${id === aktiv}">${esc(n)}</button>`).join('')}
    </div></div></section>
    <section class="abschnitt" style="padding-top:8px"><div class="wrap"><div class="raster" id="liste"></div></div></section>`;
  const liste = main.querySelector('#liste');
  const zeige = (f) => {
    liste.innerHTML = k.builds.filter((b) => f === 'alle' || b.kategorie === f).map(bauKarte).join('');
    watchThumbs(liste);
    main.querySelectorAll('.chip').forEach((c) => c.setAttribute('aria-pressed', c.dataset.f === f));
    store.set('filter', f);
  };
  main.querySelectorAll('.chip').forEach((c) => c.addEventListener('click', () => zeige(c.dataset.f)));
  zeige(k.kategorien[aktiv] || aktiv === 'alle' ? aktiv : 'alle');
}

function fremdKarte(p) {
  return `<div class="karte plugin-karte fremd"><div class="text">
      <div class="plugin-kopf"><span class="plugin-symbol" aria-hidden="true">${initialen(p.name)}</span>
        <div><h3>${esc(p.name)}</h3>${p.autor ? `<span class="eyebrow">von ${esc(p.autor)}</span>` : ''}</div></div>
      <p>${esc(p.zweck)}</p>
      ${p.einsatz ? `<p class="einsatz"><b>Auf dem Server:</b> ${esc(p.einsatz)}</p>` : ''}
      <div class="fakten"><span class="marker ${p.status === 'empfohlen' ? '' : 'ok'}">${p.status === 'empfohlen' ? 'Empfohlen' : 'Im Einsatz'}</span>
        ${p.anleitung ? `<a class="marker" href="${BASE}anleitung/${esc(p.anleitung)}/">Anleitung</a>` : ''}
        ${p.link ? `<a class="marker" href="${esc(p.link)}" target="_blank" rel="noopener">Download-Seite ↗</a>` : ''}</div>
    </div></div>`;
}

async function pluginsSeite() {
  const k = await katalog();
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <span class="eyebrow">Für Paper-Server</span><h1>Plugins</h1>
    <p class="lede">Eigene Plugins für einen fairen Server mit Coins, Lager und Arbeitern, dazu die bewährten Plugins anderer Entwickler, die auf dem Server laufen.</p></div></section>
    <section class="abschnitt" style="padding-top:8px"><div class="wrap">
      <div class="abschnitt-kopf"><div><h2>Eigene Plugins</h2><p>Von Savox entwickelt. Die Dokumentation ist komplett, Quellcode und Downloads folgen.</p></div></div>
      <div class="raster">${k.plugins.map(pluginKarte).join('')}</div></div></section>
    ${k.fremd?.length ? `<section class="abschnitt"><div class="wrap">
      <div class="abschnitt-kopf"><div><h2>Plugins anderer Entwickler</h2><p>Bewährte Plugins, die es schon gibt. Heruntergeladen wird immer von der offiziellen Seite des Entwicklers.</p></div></div>
      <div class="raster">${k.fremd.map(fremdKarte).join('')}</div></div></section>` : ''}`;
}

async function anleitungenSeite() {
  const k = await katalog();
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <span class="eyebrow">Wissen</span><h1>Anleitungen</h1>
    <p class="lede">Hilfen rund um deinen Server: Farmen ohne Spieler laufen lassen, Aktionen nachvollziehen und mehr.</p></div></section>
    <section class="abschnitt" style="padding-top:8px"><div class="wrap" style="max-width:820px">${k.docs.map(docLink).join('')}</div></section>`;
}

function wunschListe(k, max = 99) {
  const w = (k.wuensche || []).slice().sort((a, b) => b.stimmen - a.stimmen).slice(0, max);
  if (!w.length) return `<div class="leer">Noch keine offenen Wünsche. Sei der Erste!</div>`;
  return w.map((x) => `<a class="wunsch" href="${esc(x.url)}"><span class="stimmen" title="Stimmen">${x.stimmen}</span><div><b>${esc(x.titel)}</b><div class="eyebrow">#${x.nr} · ${x.art === 'plugin' ? 'Plugin-Wunsch' : 'Bauwunsch'}</div></div></a>`).join('');
}

async function wuenscheSeite() {
  const k = await katalog();
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <span class="eyebrow">Mitmachen</span><h1>Wünsche</h1>
    <p class="lede">Welches Bauwerk oder Plugin fehlt dir? Reich deinen Wunsch ein und stimm mit 👍 für die Wünsche anderer ab. Die meistgewünschten kommen zuerst dran.</p>
    <div class="knoepfe" style="display:flex;gap:10px;flex-wrap:wrap;margin-top:18px">
      <a class="btn" href="${REPO}/issues/new?template=bauwunsch.yml">Bauplan wünschen</a>
      <a class="btn zwei" href="${REPO}/issues/new?template=plugin-wunsch.yml">Plugin wünschen</a>
      <a class="btn zwei" href="${REPO}/issues/new?template=fehler.yml">Fehler melden</a>
    </div>
    <p style="margin-top:12px;color:var(--ink-mute);font-size:.9rem">Zum Einreichen und Abstimmen brauchst du ein kostenloses GitHub-Konto. Die Liste unten wird einmal täglich aktualisiert.</p>
  </div></section>
  <section class="abschnitt" style="padding-top:8px"><div class="wrap" style="max-width:820px"><h2 style="margin-bottom:14px">Offene Wünsche</h2>${wunschListe(k)}</div></section>`;
}

async function pluginSeite(id) {
  const k = await katalog();
  const p = k.plugins.find((x) => x.id === id);
  if (!p) return nichtGefunden();
  const wer = { spieler: 'Spieler', admin: 'Admin', konsole: 'Konsole' };
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <div class="krumen"><a href="${BASE}plugins/">Plugins</a> / ${esc(p.name)}</div>
    <div class="plugin-kopf"><span class="plugin-symbol" aria-hidden="true">${initialen(p.name)}</span><h1>${esc(p.name)}</h1></div>
    <p class="lede">${esc(p.beschreibung)}</p>
    <dl class="specs">
      <div><dt>Version</dt><dd>${esc(p.version)}</dd></div>
      <div><dt>Plattform</dt><dd>${esc(p.plattform)}</dd></div>
      <div><dt>Bereich</dt><dd>${esc(k.plugin_kategorien[p.kategorie] || p.kategorie)}</dd></div>
      <div><dt>Befehle</dt><dd>${p.befehle.length}</dd></div>
    </dl>
    ${p.status === 'doku' ? `<div class="hinweis"><span aria-hidden="true">⏳</span><span>${esc(p.status_text)}</span></div>` : ''}
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:16px">
      <a class="btn ${p.status === 'doku' ? 'aus' : ''}" href="${REPO}/releases" aria-disabled="${p.status === 'doku'}">.jar herunterladen</a>
      <a class="btn zwei" href="${REPO}/tree/main/plugins/eigene/${p.id}">Auf GitHub ansehen</a>
    </div>
  </div></section>
  <section class="tafel"><div class="wrap">
    <div class="zwei-spalten">
      <div class="feld"><h2>Funktionen</h2><ul class="funktionen">${p.funktionen.map((f) => `<li>${esc(f)}</li>`).join('')}</ul></div>
      <div class="feld"><h2>Änderungen</h2>${p.changelog.map((c) => `<h3 style="margin-top:14px">${esc(c.version)} <span class="eyebrow">${esc(c.datum)}</span></h3><ul class="funktionen">${c.punkte.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>`).join('')}</div>
    </div>
    <h2 style="margin:28px 0 12px">Befehle</h2>
    <div class="tabelle-huelle"><table><thead><tr><th>Befehl</th><th>Was er macht</th><th>Wer</th></tr></thead><tbody>
      ${p.befehle.map((b) => `<tr><td><code>${esc(b.befehl)}</code></td><td>${esc(b.text)}</td><td>${wer[b.wer] || b.wer}</td></tr>`).join('')}
    </tbody></table></div>
    ${p.config.length ? `<h2 style="margin:28px 0 12px">Einstellungen in der config.yml</h2>
    <div class="tabelle-huelle"><table><thead><tr><th>Schlüssel</th><th>Standard</th><th>Bedeutung</th></tr></thead><tbody>
      ${p.config.map((c) => `<tr><td><code>${esc(c.schluessel)}</code></td><td><code>${esc(c.standard)}</code></td><td>${esc(c.text)}</td></tr>`).join('')}
    </tbody></table></div>` : ''}
  </div></section>`;
}

async function anleitungSeite(id) {
  const k = await katalog();
  const d = k.docs.find((x) => x.id === id);
  if (!d) return nichtGefunden();
  const html = await (await fetch(`${BASE}data/seiten/doc-${id}.html`)).text();
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <div class="krumen"><a href="${BASE}anleitungen/">Anleitungen</a> / ${esc(d.titel)}</div>
    <h1>${esc(d.titel)}</h1><p class="lede">${esc(d.kurz)}</p></div></section>
    <section class="tafel"><div class="wrap"><article class="prosa">${html}</article></div></section>`;
  main.querySelectorAll('.prosa a[href^="http"]').forEach((a) => { a.target = '_blank'; a.rel = 'noopener'; });
}

function nichtGefunden() {
  main.innerHTML = `<section class="detail-kopf"><div class="wrap"><h1>Nicht gefunden</h1><p class="lede">Diese Seite gibt es nicht. <a href="${BASE}">Zur Startseite</a></p></div></section>`;
}

/* ---------- Bauplan-Detail ---------- */
async function bauSeite(id, tab) {
  const k = await katalog();
  const kb = k.builds.find((b) => b.id === id);
  if (!kb) return nichtGefunden();
  const d = await ladeBau(id);
  const tabs = [['anleitung', 'Anleitung'], ['teile', 'Teileliste'], ['ebenen', 'Ebenen'], ['downloads', 'Downloads']];
  tab = tabs.some((t) => t[0] === tab) ? tab : 'anleitung';
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <div class="krumen"><a href="${BASE}bauplaene/">Baupläne</a> / ${esc(k.kategorien[d.kategorie] || '')}</div>
    <h1>${esc(d.titel)}</h1>
    <p class="lede">${esc(d.beschreibung)}</p>
    <dl class="specs">
      <div><dt>Schwierigkeit</dt><dd>${punkte(d.schwierigkeit)}</dd></div>
      <div><dt>Blöcke</dt><dd>${fmt(kb.bloecke)}</dd></div>
      <div><dt>Schritte</dt><dd>${kb.schritte}</dd></div>
      <div><dt>Grundfläche</dt><dd>${esc(d.grundflaeche)}</dd></div>
      <div><dt>Höhe</dt><dd>${d.model.size.y} Ebenen</dd></div>
      <div><dt>Bauzeit</dt><dd>${stunden(d.bauzeit_stunden)}</dd></div>
      <div><dt>Edition</dt><dd>${(d.edition || []).map((e) => (e === 'java' ? 'Java' : 'Bedrock')).join(' · ')}</dd></div>
    </dl>
    ${d.status === 'entwurf' ? `<div class="hinweis"><span aria-hidden="true">⚠️</span><span><b>Entwurf:</b> ${esc(d.hinweis || '')}</span></div>` : ''}
    <div class="reiter" role="tablist">${tabs.map(([t, n]) => `<button role="tab" aria-selected="${t === tab}" data-tab="${t}">${n}</button>`).join('')}</div>
  </div></section>
  <section class="tafel"><div class="wrap" id="tafel"></div></section>`;
  main.querySelectorAll('.reiter button').forEach((b) => b.addEventListener('click', () => {
    history.replaceState(null, '', `${BASE}bau/${id}/` + (b.dataset.tab === 'anleitung' ? '' : '#' + b.dataset.tab));
    main.querySelectorAll('.reiter button').forEach((x) => x.setAttribute('aria-selected', x === b));
    zeigeTab(b.dataset.tab);
  }));
  const P = prepare(d.model, { schnitt: d.ansicht?.schnitt });
  const pal = P.pal;
  const tafel = main.querySelector('#tafel');
  const zaehlt = (p) => !(p.flags || []).some((f) => ['vorhanden', 'kein-block', 'zweiter-teil'].includes(f));
  function zeigeTab(t) {
    redrawers = []; keyHandler = null;
    if (t === 'anleitung') anleitungTab(tafel, d, P);
    if (t === 'teile') teileTab(tafel, d, pal);
    if (t === 'ebenen') ebenenTab(tafel, d, P);
    if (t === 'downloads') downloadTab(tafel, d);
  }
  zeigeTab(tab);

  function anleitungTab(el, d, P) {
    const S = d.schritte, n = S.length;
    const stepOf = schrittKarte(P, S);
    const keyDone = 'erledigt.' + d.id;
    const done = new Set(store.get(keyDone, []));
    let cur = Math.min(store.get('schritt.' + d.id, 0), n - 1), rot = 0, alles = false;
    el.innerHTML = `<div class="lego">
      <div class="buehne">
        <div class="nummer" id="nr" aria-live="polite"></div>
        <div class="werkzeug">
          <button class="rund" id="rl" aria-label="Ansicht nach links drehen">⟲</button>
          <button class="rund" id="rr" aria-label="Ansicht nach rechts drehen">⟳</button>
          <button class="rund" id="all" aria-pressed="false" aria-label="Ganzes Bauwerk zeigen">◎</button>
        </div>
        <canvas id="cv" aria-label="3D-Ansicht des aktuellen Bauschritts"></canvas>
        <div class="blick" id="blick"></div>
      </div>
      <div class="seite">
        <div class="teile-kasten" id="teile"></div>
        <div class="steuer">
          <button class="btn zwei" id="zurueck" aria-label="Vorheriger Schritt">← Zurück</button>
          <button class="btn" id="weiter" aria-label="Nächster Schritt">Weiter →</button>
        </div>
        <input class="leiste" type="range" id="leiste" min="1" max="${n}" aria-label="Schritt wählen">
        <label class="erledigt"><input type="checkbox" id="ok"> Schritt erledigt</label>
        <div><div class="fortschritt"><i id="balken"></i></div><div class="eyebrow" id="stand" style="margin-top:6px"></div></div>
        <div class="abschnitt-info" id="ab"></div>
      </div>
    </div>
    ${d.tipps?.length ? `<h2 style="margin:30px 0 12px">Tipps</h2><div class="raster">${d.tipps.map((t) => `<div class="tipp"><b>${esc(t.titel)}</b>${esc(t.text)}</div>`).join('')}</div>` : ''}`;
    const cv = el.querySelector('#cv');
    const paint = () => {
      const w = cv.parentElement.clientWidth - 2;
      const h = Math.max(320, Math.min(window.innerHeight * .66, 600));
      draw(cv, P, { width: w, maxHeight: h, rot, fit: true, padTop: 70, ...farben(), ground: null,
        state: (i, x, y, z) => {
          if (alles) return 2;
          const s = stepOf[P.at(x, y, z)];
          if (s < 0) return 1;
          return s < cur ? 1 : s === cur ? 3 : 0;
        } });
      el.querySelector('#blick').textContent = `Blick von ${VIEWS[rot]}`;
    };
    const update = () => {
      const s = S[cur];
      store.set('schritt.' + d.id, cur);
      el.querySelector('#nr').innerHTML = `${cur + 1}<small>von ${n}</small>`;
      const zahl = new Map();
      for (let j = 3; j < s.c.length; j += 4) zahl.set(s.c[j], (zahl.get(s.c[j]) || 0) + 1);
      const teile = [...zahl].filter(([i]) => zaehlt(pal[i]) || (pal[i].flags || []).includes('kein-block')).sort((a, b) => b[1] - a[1]);
      const summe = teile.filter(([i]) => zaehlt(pal[i])).reduce((a, [, c]) => a + c, 0);
      el.querySelector('#teile').innerHTML = `<h3>Neue Teile in diesem Schritt <span>${summe} Blöcke</span></h3>
        <div class="teile">${teile.map(([i, c]) => `<div class="teil" title="${esc(pal[i].name)}"><img src="${partIcon(pal[i])}" alt=""><b>×${c}</b><span>${esc(pal[i].name.replace(/ \((unten|oben)\)/, ''))}</span></div>`).join('')}</div>`;
      const ab = d.abschnitte[s.a] || {};
      const ebene = s.y[0] === s.y[1] ? `Ebene ${s.y[0]}` : `Ebenen ${s.y[0]} bis ${s.y[1]}`;
      el.querySelector('#ab').innerHTML = `<span class="eyebrow">${ebene}</span><h3 style="margin-top:4px">${esc(ab.name || '')}</h3><p>${esc(ab.text || '')}</p>`;
      el.querySelector('#leiste').value = cur + 1;
      el.querySelector('#ok').checked = done.has(cur);
      el.querySelector('#zurueck').disabled = cur === 0;
      el.querySelector('#weiter').disabled = cur === n - 1;
      el.querySelector('#balken').style.width = (done.size / n * 100) + '%';
      el.querySelector('#stand').textContent = `${done.size} von ${n} Schritten erledigt`;
      paint();
    };
    const go = (k2) => { cur = Math.max(0, Math.min(n - 1, k2)); update(); };
    el.querySelector('#zurueck').onclick = () => go(cur - 1);
    el.querySelector('#weiter').onclick = () => go(cur + 1);
    el.querySelector('#leiste').oninput = (e) => go(+e.target.value - 1);
    el.querySelector('#rl').onclick = () => { rot = (rot + 3) % 4; paint(); };
    el.querySelector('#rr').onclick = () => { rot = (rot + 1) % 4; paint(); };
    el.querySelector('#all').onclick = (e) => { alles = !alles; e.currentTarget.setAttribute('aria-pressed', alles); paint(); };
    el.querySelector('#ok').onchange = (e) => {
      e.target.checked ? done.add(cur) : done.delete(cur);
      store.set(keyDone, [...done]); update();
      if (e.target.checked && cur < n - 1) setTimeout(() => go(cur + 1), 250);
    };
    keyHandler = (e) => {
      if (/input|textarea|select/i.test(document.activeElement?.tagName) && document.activeElement.type !== 'range') return;
      if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1); }
    };
    // Wischen auf dem Handy
    let sx = null;
    cv.addEventListener('touchstart', (e) => { sx = e.touches[0].clientX; }, { passive: true });
    cv.addEventListener('touchend', (e) => { if (sx === null) return; const dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) go(cur + (dx < 0 ? 1 : -1)); sx = null; });
    onRedraw(paint);
    update();
  }

  function teileTab(el, d, pal) {
    const gesamt = d.teileliste.reduce((a, t) => a + t.n, 0);
    el.innerHTML = `<div class="zwei-spalten">
      <div><h2 style="margin-bottom:12px">Gesamt-Teileliste</h2>
        <div class="tabelle-huelle"><table><thead><tr><th>Block</th><th class="zahl">Anzahl</th><th class="zahl">Stacks</th></tr></thead><tbody>
        ${d.teileliste.map((t) => { const p = pal[t.i]; return `<tr><td><div class="block-zelle"><img src="${partIcon(p, 30)}" alt=""><div>${esc(p.name.replace(/ \((unten)\)/, ''))}<small>${esc((p.block || '').replace(/\[.*$/, ''))}</small></div></div></td><td class="zahl">${fmt(t.n)}</td><td class="zahl">${stacks(t.n)}</td></tr>`; }).join('')}
        <tr><td><b>Summe</b></td><td class="zahl"><b>${fmt(gesamt)}</b></td><td class="zahl">${stacks(gesamt)}</td></tr>
        </tbody></table></div></div>
      <div><h2 style="margin-bottom:12px">Was deine Farmen liefern müssen</h2>
        <div class="tabelle-huelle"><table><thead><tr><th>Rohstoff</th><th class="zahl">Menge</th></tr></thead><tbody>
        ${(d.rohstoffe || []).map((r) => `<tr><td><b>${esc(r.name)}</b><div style="font-size:.85rem;color:var(--ink-soft)">${esc(r.quelle)} · ${esc(r.hinweis)}</div></td><td class="zahl">${fmt(r.menge)}</td></tr>`).join('')}
        </tbody></table></div>
        ${d.schmelzvorgaenge ? `<div class="tipp" style="margin-top:14px"><b>Ofen-Arbeit</b>${fmt(d.schmelzvorgaenge)} Schmelzvorgänge, also rund ${fmt(Math.ceil(d.schmelzvorgaenge / 20))} getrocknete Seetangblöcke oder ${fmt(Math.ceil(d.schmelzvorgaenge / 8))} Kohle.</div>` : ''}
        <h2 style="margin:26px 0 12px">Bauabschnitte</h2>
        ${d.abschnitte.map((a) => `<div class="abschnitt-info" style="margin-bottom:8px"><span class="eyebrow">${a.von === a.bis ? 'Ebene ' + a.von : 'Ebenen ' + a.von + ' bis ' + a.bis}</span><h3 style="margin-top:4px">${esc(a.name)}</h3><p>${esc(a.text)}</p></div>`).join('')}
      </div></div>`;
  }

  function ebenenTab(el, d, P) {
    const { X, Y, Z, pal, grid, at } = P;
    let y = 0, hover = null;
    el.innerHTML = `<div class="ebenen">
      <div class="raster-huelle">
        <div class="steuer" style="margin-bottom:12px"><button class="rund" id="ab" aria-label="Eine Ebene tiefer">−</button>
          <b id="yl" style="font:800 1.4rem var(--f-display);min-width:6ch;text-align:center"></b>
          <button class="rund" id="auf" aria-label="Eine Ebene höher">+</button>
          <input class="leiste" type="range" id="ys" min="0" max="${Y - 1}" aria-label="Ebene"></div>
        <canvas id="gc" aria-label="Draufsicht der Ebene, Norden ist oben"></canvas>
        <div class="ablesen" id="les">Zeige auf einen Block, um Name und Position zu sehen. Norden ist oben, 0 ist die Mitte.</div>
      </div>
      <div class="feld"><h3 style="margin-bottom:10px">In dieser Ebene</h3><ul class="legende" id="leg"></ul></div></div>`;
    const cv = el.querySelector('#gc');
    let geo = null;
    const paint = () => {
      const avail = Math.min(cv.parentElement.clientWidth - 28, 720);
      const cs = Math.max(6, Math.floor((avail - 28) / X));
      const pad = 26, W = pad + cs * X + 4, H = pad + cs * Z + 4, dpr = window.devicePixelRatio || 1;
      cv.width = W * dpr; cv.height = H * dpr; cv.style.width = W + 'px'; cv.style.height = H + 'px';
      const g = cv.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0);
      geo = { pad, cs };
      g.fillStyle = cssv('--sheet-2'); g.fillRect(0, 0, W, H);
      g.fillStyle = cssv('--sheet'); g.fillRect(pad, pad, cs * X, cs * Z);
      if (y > 0) {
        g.fillStyle = cssv('--ink'); g.globalAlpha = .1;
        for (let z = 0; z < Z; z++) for (let x = 0; x < X; x++) if (grid[at(x, y - 1, z)] >= 0) g.fillRect(pad + x * cs, pad + z * cs, cs, cs);
        g.globalAlpha = 1;
      }
      g.strokeStyle = cssv('--line'); g.lineWidth = 1;
      for (let i = 0; i <= Math.max(X, Z); i++) {
        if (i <= X) { g.beginPath(); g.moveTo(pad + i * cs + .5, pad); g.lineTo(pad + i * cs + .5, pad + Z * cs); g.stroke(); }
        if (i <= Z) { g.beginPath(); g.moveTo(pad, pad + i * cs + .5); g.lineTo(pad + X * cs, pad + i * cs + .5); g.stroke(); }
      }
      const counts = new Map();
      for (let z = 0; z < Z; z++) for (let x = 0; x < X; x++) {
        const i = grid[at(x, y, z)]; if (i < 0) continue;
        const p = pal[i]; const small = /thin|pane|panel|plate|mob/.test(p.shape);
        const ins = small ? Math.max(1, Math.round(cs * .22)) : 1;
        g.globalAlpha = p.context ? .3 : 1; g.fillStyle = p.color;
        g.fillRect(pad + x * cs + ins, pad + z * cs + ins, cs - ins * 2 + 1, cs - ins * 2 + 1);
        g.globalAlpha = 1;
        if (zaehlt(p)) counts.set(i, (counts.get(i) || 0) + 1);
      }
      const cx = (X - 1) / 2, cz = (Z - 1) / 2;
      g.fillStyle = cssv('--ink-mute'); g.font = `10px ${cssv('--f-mono')}`; g.textAlign = 'center'; g.textBaseline = 'middle';
      for (let i = 0; i < X; i++) { const r = Math.round(i - cx); if (r % 5 === 0 && Math.abs(i - cx - r) < .01) g.fillText(r > 0 ? '+' + r : r, pad + (i + .5) * cs, 12); }
      g.textAlign = 'right';
      for (let i = 0; i < Z; i++) { const r = Math.round(i - cz); if (r % 5 === 0 && Math.abs(i - cz - r) < .01) g.fillText(r > 0 ? '+' + r : r, pad - 4, pad + (i + .5) * cs); }
      g.textAlign = 'left'; g.fillStyle = cssv('--ink'); g.font = `bold 11px ${cssv('--f-mono')}`; g.fillText('N ↑', 2, 10);
      if (hover) { g.strokeStyle = cssv('--hl'); g.lineWidth = 2; g.strokeRect(pad + hover.x * cs + 1, pad + hover.z * cs + 1, cs - 2, cs - 2); }
      el.querySelector('#yl').textContent = `Ebene ${y}`;
      el.querySelector('#ys').value = y;
      const items = [...counts].sort((a, b) => b[1] - a[1]);
      el.querySelector('#leg').innerHTML = items.length ? items.map(([i, c]) => `<li><img src="${partIcon(pal[i], 24)}" alt=""><span>${esc(pal[i].name.replace(/ \((unten)\)/, ''))}</span><b>${c}</b></li>`).join('')
        + `<li style="border-top:1px solid var(--line);padding-top:6px"><span></span><b>Summe</b><b>${items.reduce((a, [, c]) => a + c, 0)}</b></li>` : '<li>Keine Blöcke in dieser Ebene.</li>';
    };
    const setY = (v) => { y = Math.max(0, Math.min(Y - 1, v)); hover = null; paint(); };
    el.querySelector('#ab').onclick = () => setY(y - 1);
    el.querySelector('#auf').onclick = () => setY(y + 1);
    el.querySelector('#ys').oninput = (e) => setY(+e.target.value);
    cv.addEventListener('pointermove', (e) => {
      const r = cv.getBoundingClientRect(); const x = Math.floor((e.clientX - r.left - geo.pad) / geo.cs), z = Math.floor((e.clientY - r.top - geo.pad) / geo.cs);
      hover = x >= 0 && z >= 0 && x < X && z < Z ? { x, z } : null; paint();
      const les = el.querySelector('#les');
      if (!hover) return;
      const i = grid[at(x, y, z)]; const sg = (v) => (v > 0 ? '+' + v : v);
      les.innerHTML = `<b>${i < 0 ? 'Luft (frei lassen)' : esc(pal[i].name)}</b><br>X ${sg(Math.round(x - (X - 1) / 2))} · Y ${y} · Z ${sg(Math.round(z - (Z - 1) / 2))}${i >= 0 && pal[i].block ? ` · <code>${esc(pal[i].block)}</code>` : ''}`;
    });
    onRedraw(paint);
    paint();
  }

  function downloadTab(el, d) {
    const info = {
      litematic: ['Litematica', 'Für Java mit der Mod Litematica: Der Bauplan erscheint als Geisterblöcke im Spiel. Datei in den Ordner .minecraft/schematics legen.'],
      schem: ['WorldEdit', 'Für WorldEdit oder FastAsyncWorldEdit auf dem Server: in den Ordner plugins/WorldEdit/schematics legen, dann //schem load.'],
      csv: ['Teileliste', 'Alle Blöcke mit Anzahl und Stacks, öffnet sich in Excel, LibreOffice oder Google Tabellen.'],
    };
    el.innerHTML = `${d.downloads.length ? `<div class="dl-raster">${d.downloads.map((x) => `<div class="dl"><span class="eyebrow">${info[x.art][0]}</span><span class="endung">.${x.art}</span><p>${info[x.art][1]}</p><a class="btn" href="${BASE}downloads/${d.id}/${x.datei}" download>Herunterladen <span style="font-weight:400;opacity:.75">${(x.groesse / 1024).toFixed(x.groesse < 10240 ? 1 : 0)} KB</span></a></div>`).join('')}</div>` : '<div class="leer">Downloads werden beim nächsten Aufbau der Seite erzeugt.</div>'}
      ${d.status === 'entwurf' ? `<div class="hinweis" style="margin-top:18px"><span aria-hidden="true">⚠️</span><span>Dieser Bauplan ist ein Entwurf: Die Richtung von Treppen, Türen und Trichtern stimmt in den Dateien eventuell noch nicht. Nach dem Einfügen kurz prüfen.</span></div>` : ''}
      <p style="margin-top:18px;color:var(--ink-soft)">Quelle des Bauplans auf GitHub: <a href="${REPO}/tree/main/builds/${d.id}">builds/${d.id}</a></p>`;
  }
}

/* ---------- Router ---------- */
let keyHandler = null;
document.addEventListener('keydown', (e) => keyHandler && keyHandler(e));
const TITEL = 'Savox Bauwerkstatt';
async function route() {
  redrawers = []; keyHandler = null;
  // alte Links der Form #/bau/... auf echte Adressen umleiten
  if (location.hash.startsWith('#/')) {
    const alt = location.hash.slice(2).split('/').filter(Boolean);
    const tab = alt[0] === 'bau' && alt[2] ? '#' + alt[2] : '';
    history.replaceState(null, '', BASE + (alt.length ? alt.slice(0, alt[0] === 'bau' ? 2 : 2).join('/') + '/' : '') + tab);
  }
  let pfad = decodeURIComponent(location.pathname);
  if (pfad.startsWith(BASE)) pfad = pfad.slice(BASE.length);
  const [a, b] = pfad.split('/').filter(Boolean);
  const c = location.hash.replace(/^#/, '') || undefined;
  const nav = { bau: 'bauplaene', bauplaene: 'bauplaene', plugins: 'plugins', plugin: 'plugins', anleitungen: 'anleitungen', anleitung: 'anleitungen', wuensche: 'wuensche' }[a] || '';
  document.querySelectorAll('[data-nav]').forEach((l) => {
    if (l.dataset.nav === nav) l.setAttribute('aria-current', 'page'); else l.removeAttribute('aria-current');
  });
  try {
    if (!a) await startSeite();
    else if (a === 'bauplaene') await bauplaeneSeite();
    else if (a === 'plugins') await pluginsSeite();
    else if (a === 'anleitungen') await anleitungenSeite();
    else if (a === 'wuensche') await wuenscheSeite();
    else if (a === 'bau') await bauSeite(b, c);
    else if (a === 'plugin') await pluginSeite(b);
    else if (a === 'anleitung') await anleitungSeite(b);
    else nichtGefunden();
  } catch (err) {
    console.error(err);
    main.innerHTML = `<section class="detail-kopf"><div class="wrap"><h1>Das hat nicht geklappt</h1><p class="lede">Die Daten konnten nicht geladen werden. Lade die Seite neu oder versuch es später noch einmal.</p></div></section>`;
  }
  const h1 = main.querySelector('h1');
  if (!erstAufruf) document.title = h1 && a ? `${h1.textContent} · ${TITEL}` : TITEL;
  erstAufruf = false;
}
let erstAufruf = true;   // beim ersten Laden bleibt der vorgerenderte Seitentitel
// interne Links ohne Neuladen öffnen
document.addEventListener('click', (e) => {
  const l = e.target.closest('a[href]');
  if (!l || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  if (l.target || l.hasAttribute('download')) return;
  const url = new URL(l.href, location.href);
  if (url.origin !== location.origin || !url.pathname.startsWith(BASE)) return;
  if (/\.(xml|txt|json|png|svg|litematic|schem|csv)$/.test(url.pathname)) return;
  if (url.pathname === location.pathname && url.hash) return;   // Sprungmarken auf derselben Seite
  e.preventDefault();
  history.pushState(null, '', url.pathname + url.search + url.hash);
  route().then(() => window.scrollTo(0, 0));
});
window.addEventListener('popstate', route);
route();
