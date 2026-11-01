import { prepare, draw, partIcon, shapeOf, VIEWS } from './render.js';

const REPO = 'https://github.com/Savox76/minecraft-tools';
const BASE = document.querySelector('meta[name="site-base"]')?.content || '/';
const V = '__VERSION__';   // beim Bauen ersetzt, damit nach einem Update keine alten Daten aus dem Zwischenspeicher kommen
const main = document.getElementById('inhalt');
const esc = (t) => String(t ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const cssv = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const store = {
  get(k, d) { try { const v = localStorage.getItem('bw.' + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem('bw.' + k, JSON.stringify(v)); } catch { /* privat */ } },
};
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- Sprache ---------- */
const relPfad = () => { const p = decodeURIComponent(location.pathname); return p.startsWith(BASE) ? p.slice(BASE.length) : p.replace(/^\//, ''); };
const L = /^en(\/|$)/.test(relPfad()) ? 'en' : 'de';
const SEG = {
  de: { liste: 'bauplaene', bau: 'bau', plugins: 'plugins', plugin: 'plugin', anleitungen: 'anleitungen', anleitung: 'anleitung', wuensche: 'wuensche', geplant: 'geplant' },
  en: { liste: 'builds', bau: 'build', plugins: 'plugins', plugin: 'plugin', anleitungen: 'guides', anleitung: 'guide', wuensche: 'wishes', geplant: 'planned' },
};
const url = (art = 'start', id = null, lang = L) => BASE + (lang === 'en' ? 'en/' : '') + (art === 'start' ? '' : SEG[lang][art] + '/' + (id ? id + '/' : ''));
const de = L === 'de';
const tr = (d, e) => (de ? d : e);
const lo = (o, k) => (!de && o?.en && o.en[k] != null ? o.en[k] : o?.[k]);
const bn = (p) => (de ? p.name : p.name_en || p.name).replace(/ \((unten|oben|bottom|lower)\)$/, '');
const fmt = (n) => Number(n).toLocaleString(de ? 'de-DE' : 'en-US');
const stacks = (n) => { const s = Math.floor(n / 64), r = n % 64, st = tr('St.', 'st.'); return s ? `${s} ${st}${r ? ' + ' + r : ''}` : `${r}`; };
const ebeneText = (a, b) => (a === b ? tr(`Ebene ${a}`, `Layer ${a}`) : tr(`Ebenen ${a} bis ${b}`, `Layers ${a} to ${b}`));

/* ---------- Thema: automatisch, hell oder dunkel ---------- */
function liesThema() {
  try { const v = localStorage.getItem('bw.thema') || ''; return /hell|light/.test(v) ? 'hell' : /dunkel|dark/.test(v) ? 'dunkel' : 'auto'; } catch { return 'auto'; }
}
function setzeThema(t) {
  if (t === 'auto') delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = t === 'hell' ? 'light' : 'dark';
  try { t === 'auto' ? localStorage.removeItem('bw.thema') : localStorage.setItem('bw.thema', t); } catch { /* privat */ }
  document.querySelectorAll('[data-thema]').forEach((b) => b.setAttribute('aria-checked', b.dataset.thema === t));
  redrawAll();
}
document.querySelectorAll('[data-thema]').forEach((b) => b.addEventListener('click', () => setzeThema(b.dataset.thema)));
document.querySelectorAll('.thema-wahl').forEach((gruppe) => gruppe.addEventListener('keydown', (e) => {
  if (!['ArrowLeft', 'ArrowRight'].includes(e.key)) return;
  const k = ['auto', 'hell', 'dunkel'], i = (k.indexOf(liesThema()) + (e.key === 'ArrowRight' ? 1 : 2)) % 3;
  setzeThema(k[i]); gruppe.querySelector(`[data-thema="${k[i]}"]`).focus();
}));
setTimeout(() => setzeThema(liesThema()));
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => redrawAll());

/* ---------- Daten ---------- */
let KAT = null;
const builds = new Map();
async function katalog() {
  if (!KAT) KAT = await (await fetch(`${BASE}data/katalog.json?v=${V}`)).json();
  return KAT;
}
async function ladeBau(id) {
  if (!builds.has(id)) builds.set(id, fetch(`${BASE}data/builds/${id}.json?v=${V}`).then((r) => r.json()));
  return builds.get(id);
}
const farben = () => ({ fadeTo: cssv('--sheet'), highlight: cssv('--hl'), ground: cssv('--sheet-2'), gridLine: cssv('--line') });

/* ---------- Neu zeichnen bei Größe/Thema ---------- */
let redrawers = [];
function onRedraw(fn) { redrawers.push(fn); }
function redrawAll() { redrawers.forEach((f) => f()); }
let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(redrawAll, 150); });

/* ---------- Bausteine ---------- */
const punkte = (n) => { const t = tr(`Schwierigkeit ${n} von 5`, `Difficulty ${n} of 5`); return `<span class="punkte" title="${t}" aria-label="${t}">${[1, 2, 3, 4, 5].map((i) => `<i class="${i <= n ? 'an' : ''}"></i>`).join('')}</span>`; };
const editionen = (e) => (e || []).map((x) => `<span class="marker ${x}">${x === 'java' ? 'Java' : 'Bedrock'}</span>`).join('');
const stunden = (b) => (b && b.length ? tr(`${b[0]}–${b[1]} Std.`, `${b[0]}–${b[1]} h`) : '');
const initialen = (n) => (n.match(/[A-ZÄÖÜ]/g) || [n[0]]).slice(0, 2).join('');
const pkat = (k, id) => (de ? k.plugin_kategorien : k.plugin_kategorien_en || k.plugin_kategorien)[id] || id;
const kats = (k) => (de ? k.kategorien : k.kategorien_en || k.kategorien);

// Plugin-Angaben bei Bauplänen und Ideen: benötigt, empfohlen oder optional
const STUFE = { benoetigt: tr('Benötigt', 'Required'), empfohlen: tr('Empfohlen', 'Recommended'), optional: tr('Optional', 'Optional') };
function pluginRef(k, id) {
  const e = (k.plugins || []).find((p) => p.id === id);
  if (e) return { name: e.name, href: url('plugin', id), eigen: true };
  const f = (k.fremd || []).find((p) => p.id === id);
  return f ? { name: f.name, href: f.link || null, eigen: false, autor: f.autor, anleitung: f.anleitung } : { name: id, href: null };
}
const pluginLink = (r) => (r.href ? `<a href="${esc(r.href)}"${r.eigen ? '' : ' target="_blank" rel="noopener"'}>${esc(r.name)}</a>` : esc(r.name));
// Kasten „Plugins“ auf der Bauplan-Seite
function pluginKasten(k, liste) {
  if (!liste || !liste.length) {
    return `<div class="plugin-bedarf leer-plugin"><h3>${tr('Plugins', 'Plugins')}</h3><p>${tr('Kein Plugin nötig. Läuft in reinem Minecraft (Vanilla), im Einzelspieler und auf jedem Server.', 'No plugin needed. Works in plain Minecraft (vanilla), in singleplayer and on any server.')}</p></div>`;
  }
  return `<div class="plugin-bedarf"><h3>${tr('Plugins für diesen Bauplan', 'Plugins for this build')}</h3>${liste.map((x) => {
    const r = pluginRef(k, x.id);
    const her = r.eigen ? tr('Eigenes Plugin', 'Our plugin') : (r.autor ? tr(`von ${r.autor}`, `by ${r.autor}`) : tr('Plugin eines anderen Entwicklers', 'Plugin by another developer'));
    return `<div class="pb-eintrag"><div class="pb-kopf"><span class="marker stufe-${x.stufe}">${STUFE[x.stufe]}</span><b>${pluginLink(r)}</b><span class="eyebrow">${esc(her)}</span></div>
      ${x.grund ? `<p>${esc(lo(x, 'grund'))}</p>` : ''}${r.anleitung ? `<a class="pb-mehr" href="${url('anleitung', r.anleitung)}">${tr('Anleitung dazu', 'Guide')}</a>` : ''}</div>`;
  }).join('')}</div>`;
}

function bauKarte(b) {
  const titel = lo(b, 'titel');
  return `<a class="karte" href="${url('bau', b.id)}" data-thumb="${b.id}">
    <div class="bild"><canvas role="img" aria-label="${esc(tr(`Minecraft-Bauplan ${titel}, fertiges Bauwerk`, `Minecraft build ${titel}, finished`))}"></canvas></div>
    <div class="text">
      <div class="chips">${editionen(b.edition)}${(b.plugins || []).some((x) => x.stufe === 'benoetigt') ? `<span class="marker stufe-benoetigt">${tr('Plugin nötig', 'Plugin needed')}</span>` : ''}${b.status === 'entwurf' ? `<span class="marker entwurf">${tr('Entwurf', 'Draft')}</span>` : ''}</div>
      <h3>${esc(titel)}</h3>
      <p>${esc(lo(b, 'beschreibung'))}</p>
      <div class="fakten">${punkte(b.schwierigkeit)}<span><b>${fmt(b.bloecke)}</b> ${tr('Blöcke', 'blocks')}</span><span><b>${b.schritte}</b> ${tr('Schritte', 'steps')}</span><span>${stunden(b.bauzeit_stunden)}</span></div>
    </div></a>`;
}
function pluginKarte(p) {
  return `<a class="karte plugin-karte" href="${url('plugin', p.id)}">
    <div class="text">
      <div class="plugin-kopf"><span class="plugin-symbol" aria-hidden="true">${initialen(p.name)}</span>
        <div><h3>${esc(p.name)}</h3><span class="marker">v${esc(p.version)}</span></div></div>
      <p>${esc(lo(p, 'kurz'))}</p>
      <div class="fakten"><span class="marker">${esc(pkat(KAT, p.kategorie))}</span><span class="marker">${p.befehle.length} ${tr('Befehle', 'commands')}</span>${p.status === 'doku' ? `<span class="marker entwurf">${tr('Download folgt', 'Download soon')}</span>` : ''}</div>
    </div></a>`;
}
const docLink = (d) => `<a class="liste-link" href="${url('anleitung', d.id)}"><div><h3>${esc(lo(d, 'titel'))}</h3><p>${esc(lo(d, 'kurz'))}</p></div><span class="pfeil" aria-hidden="true">→</span></a>`;

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
  const villa = tr('Villa am Wasser', 'Villa by the Water');
  main.innerHTML = `
  <section class="held"><div class="wrap">
    <div>
      <h1>${tr('Block für Block. Schritt für Schritt.', 'Block by block. Step by step.')}</h1>
      <p class="lede">${tr('Jeder Bauplan zeigt pro Schritt genau, welche Blöcke du brauchst und wo sie hinkommen. Dazu Plugins für deinen eigenen Server. Alles kostenlos und einzeln zum Herunterladen.',
        'Every build plan shows for each step exactly which blocks you need and where they go. Plus plugins for your own server. All free and downloadable one by one.')}</p>
      <div class="knoepfe"><a class="btn" href="${url('liste')}">${tr('Baupläne ansehen', 'Browse builds')}</a><a class="btn zwei" href="${url('geplant')}">${tr('Was als Nächstes kommt', 'What comes next')}</a></div>
      <p class="bestand">${tr(`Schon da: <b>${k.builds.length} Baupläne</b> mit ${fmt(sum)} Blöcken, <b>${k.plugins.length} Plugins</b> und <b>${k.docs.length} Anleitungen</b>. In Planung: ${k.ideen_anzahl || ''} weitere Ideen.`,
        `Available now: <b>${k.builds.length} builds</b> with ${fmt(sum)} blocks, <b>${k.plugins.length} plugins</b> and <b>${k.docs.length} guides</b>. Planned: ${k.ideen_anzahl || ''} more ideas.`)}</p>
    </div>
    <figure class="heft bauplan" style="margin:0">
      <div class="heft-kopf"><div class="heft-nr" id="held-nr" aria-live="off">1<small></small></div><div class="heft-teile" id="held-teile" aria-label="${tr('Teile in diesem Schritt', 'Parts in this step')}"></div></div>
      <div class="heft-buehne"><canvas id="held-cv" aria-label="${tr(`Animation: ${villa} wird Schritt für Schritt gebaut`, `Animation: ${villa} being built step by step`)}"></canvas></div>
      <figcaption class="heft-fuss"><span id="held-text">${villa}</span><a href="${url('bau', 'villa-am-wasser')}">${tr('Diesen Bauplan öffnen', 'Open this build')}</a></figcaption>
      <div class="heft-balken" aria-hidden="true"><i id="held-balken"></i></div>
    </figure>
  </div></section>
  <section class="abschnitt"><div class="wrap">
    <div class="abschnitt-kopf"><div><h2>${tr('Baupläne', 'Builds')}</h2><p>${tr('Türme, Villen und Farmen. Jeder Plan mit Bauschritten, Teileliste und Dateien für Litematica und WorldEdit.', 'Towers, villas and farms. Every plan with build steps, a parts list and files for Litematica and WorldEdit.')}</p></div><a class="btn zwei klein" href="${url('liste')}">${tr('Alle Baupläne', 'All builds')}</a></div>
    <div class="raster">${k.builds.map(bauKarte).join('')}</div>
  </div></section>
  <section class="abschnitt"><div class="wrap">
    <div class="abschnitt-kopf"><div><h2>${tr('Eigene Plugins für Paper', 'Our plugins for Paper')}</h2><p>${tr('Shop, Lager, Arbeiter, Admin-Schutz und mehr. Entwickelt für einen fairen Server, auf dem keiner anderen schaden kann.', 'Shop, storage, workers, admin protection and more. Made for a fair server where nobody can harm others.')}</p></div><a class="btn zwei klein" href="${url('plugins')}">${tr('Alle Plugins', 'All plugins')}</a></div>
    <div class="raster">${k.plugins.slice(0, 4).map(pluginKarte).join('')}</div>
  </div></section>
  <section class="abschnitt"><div class="wrap zwei-spalten">
    <div><div class="abschnitt-kopf"><div><h2>${tr('Anleitungen', 'Guides')}</h2><p>${tr('Server-Wissen, das beim Bauen hilft.', 'Server know-how that helps with building.')}</p></div></div>${k.docs.map(docLink).join('')}</div>
    <div><div class="abschnitt-kopf"><div><h2>${tr('Was soll als Nächstes kommen?', 'What should come next?')}</h2><p>${tr('Wünsch dir ein Bauwerk. Die meistgewünschten werden zuerst gebaut.', 'Request a build. The most requested ones are made first.')}</p></div></div>
      ${wunschListe(k, 4)}<div style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="${url('wuensche')}">${tr('Bauplan wünschen', 'Request a build')}</a><a class="btn zwei" href="${url('geplant')}">${tr(`${k.ideen_anzahl || ''} geplante Ideen`, `${k.ideen_anzahl || ''} planned ideas`)}</a></div></div>
  </div></section>`;
  watchThumbs(main);
  heldAnimation();
}

async function heldAnimation() {
  const d = await ladeBau('villa-am-wasser');
  const cv = document.getElementById('held-cv'); if (!cv) return;
  const P = prepare(d.model);
  const stepOf = schrittKarte(P, d.schritte);
  const n = d.schritte.length;
  let cur = reduced ? n : 0, timer = null;
  const zaehlt = (p) => !(p.flags || []).some((f) => ['vorhanden', 'kein-block', 'zweiter-teil'].includes(f));
  const nr = document.getElementById('held-nr'), teile = document.getElementById('held-teile');
  const balken = document.getElementById('held-balken'), txt = document.getElementById('held-text');
  const name = lo(d, 'titel');
  const paint = () => {
    if (!cv.isConnected) { clearTimeout(timer); return; }
    const w = cv.parentElement.clientWidth;
    draw(cv, P, { width: w, maxHeight: Math.min(440, w * .78), rot: 0, ...farben(), fadeTo: cssv('--plan'), ground: null,
      state: (i, x, y, z) => { const s = stepOf[P.at(x, y, z)]; if (s < 0) return 2; return s < cur ? 2 : s === cur ? 3 : 0; } });
  };
  const anzeigen = () => {
    const fertig = cur >= n;
    nr.innerHTML = fertig ? `${n}<small>${tr('Schritte, fertig', 'steps, done')}</small>` : `${cur + 1}<small>${tr('von', 'of')} ${n}</small>`;
    balken.style.width = `${Math.min(100, (cur + (fertig ? 0 : 1)) / n * 100)}%`;
    txt.textContent = name;
    if (fertig) { teile.innerHTML = ''; teile.hidden = true; return; }
    teile.hidden = false;
    const s = d.schritte[cur], zahl = new Map();
    for (let j = 3; j < s.c.length; j += 4) if (zaehlt(P.pal[s.c[j]])) zahl.set(s.c[j], (zahl.get(s.c[j]) || 0) + 1);
    teile.innerHTML = [...zahl].sort((a, b) => b[1] - a[1]).slice(0, 4)
      .map(([i, c]) => `<div title="${esc(bn(P.pal[i]))}"><img src="${partIcon(P.pal[i], 30)}" alt="${esc(bn(P.pal[i]))}"><b>×${c}</b></div>`).join('');
  };
  const tick = () => {
    cur++; if (cur > n + 12) cur = 0;
    paint(); if (cur <= n) anzeigen();
    timer = setTimeout(tick, cur === 0 ? 700 : cur >= n ? 180 : 420);
  };
  paint(); anzeigen(); onRedraw(paint);
  if (!reduced) timer = setTimeout(tick, 900);
}

function schrittKarte(P, schritte) {
  const m = new Int32Array(P.X * P.Y * P.Z).fill(-1);
  schritte.forEach((s, k) => { for (let j = 0; j < s.c.length; j += 4) m[P.at(s.c[j], s.c[j + 1], s.c[j + 2])] = k; });
  return m;
}

async function bauplaeneSeite() {
  const k = await katalog();
  const K = kats(k);
  const aktiv = store.get('filter', 'alle');
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <h1>${tr('Baupläne', 'Builds')}</h1>
    <p class="lede">${tr('Jeden Bauplan gibt es als Schritt-für-Schritt-Anleitung im Browser, als Litematica- und WorldEdit-Datei und als Teileliste.', 'Every build comes as step-by-step instructions in the browser, as a Litematica and WorldEdit file and as a parts list.')}</p>
    <div class="chips" style="margin-top:18px" role="group" aria-label="${tr('Kategorie filtern', 'Filter by category')}">
      ${[['alle', tr('Alle', 'All')], ...Object.entries(K)].map(([id, n]) => `<button class="chip" data-f="${id}" aria-pressed="${id === aktiv}">${esc(n)}</button>`).join('')}
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
  zeige(K[aktiv] || aktiv === 'alle' ? aktiv : 'alle');
}

function fremdKarte(p) {
  return `<div class="karte plugin-karte fremd"><div class="text">
      <div class="plugin-kopf"><span class="plugin-symbol" aria-hidden="true">${initialen(p.name)}</span>
        <div><h3>${esc(p.name)}</h3>${p.autor ? `<span class="eyebrow">${tr('von', 'by')} ${esc(p.autor)}</span>` : ''}</div></div>
      <p>${esc(lo(p, 'zweck'))}</p>
      ${p.einsatz ? `<p class="einsatz"><b>${tr('Auf dem Server:', 'On the server:')}</b> ${esc(lo(p, 'einsatz'))}</p>` : ''}
      ${(() => { const bs = (KAT?.builds || []).filter((b) => (b.plugins || []).some((x) => x.id === p.id)); return bs.length ? `<p class="einsatz"><b>${tr('Für Baupläne:', 'For builds:')}</b> ${bs.map((b) => `<a href="${url('bau', b.id)}">${esc(lo(b, 'titel'))}</a>`).join(', ')}</p>` : ''; })()}
      <div class="fakten"><span class="marker ${p.status === 'empfohlen' ? '' : 'ok'}">${p.status === 'empfohlen' ? tr('Empfohlen', 'Recommended') : tr('Im Einsatz', 'In use')}</span>
        ${p.anleitung ? `<a class="marker" href="${url('anleitung', esc(p.anleitung))}">${tr('Anleitung', 'Guide')}</a>` : ''}
        ${p.link ? `<a class="marker" href="${esc(p.link)}" target="_blank" rel="noopener">${tr('Download-Seite', 'Download page')}</a>` : ''}</div>
    </div></div>`;
}

async function pluginsSeite() {
  const k = await katalog();
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <h1>Plugins</h1>
    <p class="lede">${tr('Eigene Plugins für einen fairen Server mit Coins, Lager und Arbeitern, dazu die bewährten Plugins anderer Entwickler, die auf dem Server laufen.', 'Our own plugins for a fair server with coins, storage and workers, plus the proven plugins by other developers that run on the server.')}</p></div></section>
    <section class="abschnitt" style="padding-top:8px"><div class="wrap">
      <div class="abschnitt-kopf"><div><h2>${tr('Eigene Plugins', 'Our plugins')}</h2><p>${tr('Von Savox entwickelt. Die Dokumentation ist komplett, Quellcode und Downloads folgen.', 'Developed by Savox. The documentation is complete, source code and downloads will follow.')}</p></div></div>
      <div class="raster">${k.plugins.map(pluginKarte).join('')}</div></div></section>
    ${k.fremd?.length ? `<section class="abschnitt"><div class="wrap">
      <div class="abschnitt-kopf"><div><h2>${tr('Plugins anderer Entwickler', 'Plugins by other developers')}</h2><p>${tr('Bewährte Plugins, die es schon gibt. Heruntergeladen wird immer von der offiziellen Seite des Entwicklers.', 'Proven plugins that already exist. Always download them from the developer’s official page.')}</p></div></div>
      <div class="raster">${k.fremd.map(fremdKarte).join('')}</div></div></section>` : ''}`;
}

async function anleitungenSeite() {
  const k = await katalog();
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <h1>${tr('Anleitungen', 'Guides')}</h1>
    <p class="lede">${tr('Hilfen rund um deinen Server: Farmen ohne Spieler laufen lassen, Aktionen nachvollziehen und mehr.', 'Help for your server: keep farms running without players, trace player actions and more.')}</p></div></section>
    <section class="abschnitt" style="padding-top:8px"><div class="wrap" style="max-width:820px">${k.docs.map(docLink).join('')}</div></section>`;
}

function wunschListe(k, max = 99) {
  const w = (k.wuensche || []).slice().sort((a, b) => b.stimmen - a.stimmen).slice(0, max);
  if (!w.length) return `<div class="leer">${tr('Noch keine offenen Wünsche. Sei der Erste!', 'No open wishes yet. Be the first!')}</div>`;
  return w.map((x) => `<a class="wunsch" href="${esc(x.url)}"><span class="stimmen" title="${tr('Stimmen', 'Votes')}">${x.stimmen}</span><div><b>${esc(x.titel)}</b><div class="eyebrow">#${x.nr} · ${x.art === 'plugin' ? tr('Plugin-Wunsch', 'Plugin request') : tr('Bauwunsch', 'Build request')}</div></div></a>`).join('');
}

async function wuenscheSeite() {
  const k = await katalog();
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <h1>${tr('Wünsche', 'Wishes')}</h1>
    <p class="lede">${tr('Welches Bauwerk oder Plugin fehlt dir? Reich deinen Wunsch ein und stimm mit 👍 für die Wünsche anderer ab. Die meistgewünschten kommen zuerst dran.', 'Which build or plugin are you missing? Submit your wish and vote for others’ wishes with 👍. The most requested come first.')}</p>
    <div class="knoepfe" style="display:flex;gap:10px;flex-wrap:wrap;margin-top:18px">
      <a class="btn" href="${REPO}/issues/new?template=bauwunsch.yml">${tr('Bauplan wünschen', 'Request a build')}</a>
      <a class="btn zwei" href="${REPO}/issues/new?template=plugin-wunsch.yml">${tr('Plugin wünschen', 'Request a plugin')}</a>
      <a class="btn zwei" href="${REPO}/issues/new?template=fehler.yml">${tr('Fehler melden', 'Report a bug')}</a>
    </div>
    <p style="margin-top:12px;color:var(--ink-mute);font-size:.9rem">${tr('Zum Einreichen und Abstimmen brauchst du ein kostenloses GitHub-Konto. Die Liste unten wird einmal täglich aktualisiert.', 'You need a free GitHub account to submit and vote. The list below is updated once a day.')}</p>
  </div></section>
  <section class="abschnitt" style="padding-top:8px"><div class="wrap" style="max-width:820px">
    <a class="liste-link" href="${url('geplant')}"><div><h3>${tr(`${k.ideen_anzahl || ''} Ideen sind schon geplant`, `${k.ideen_anzahl || ''} ideas are already planned`)}</h3><p>${tr('Schau zuerst dort nach und stimm für eine Idee ab, bevor du einen neuen Wunsch anlegst.', 'Check there first and vote for an idea before creating a new wish.')}</p></div><span class="pfeil" aria-hidden="true">→</span></a>
    <h2 style="margin:22px 0 14px">${tr('Offene Wünsche', 'Open wishes')}</h2>${wunschListe(k)}</div></section>`;
}

async function geplantSeite() {
  const k = await katalog();
  const D = await (await fetch(`${BASE}data/ideen.json?v=${V}`)).json();
  const IDS = D.ideen;
  const GR = { klein: tr('klein', 'small'), mittel: tr('mittel', 'medium'), groß: tr('groß', 'large') };
  const ST = { idee: tr('Idee', 'Idea'), 'in-arbeit': tr('In Arbeit', 'In progress'), verfuegbar: tr('Verfügbar', 'Available') };
  // vorhandene Wünsche zu einer Idee: Titel enthält „Idee #61“
  const stimmen = new Map();
  for (const w of k.wuensche || []) {
    const m = /Idee #(A?\d+)\b/i.exec(w.titel);
    if (m && (!stimmen.has(m[1].toUpperCase()) || stimmen.get(m[1].toUpperCase()).stimmen < w.stimmen)) stimmen.set(m[1].toUpperCase(), w);
  }
  const karte = (i, mitId = true) => {
    const w = stimmen.get(String(i.nr).toUpperCase());
    let aktion;
    if (i.status === 'verfuegbar' && i.bauplan) aktion = `<a class="btn klein" href="${url('bau', i.bauplan)}">${tr('Zum Bauplan', 'View build')}</a>`;
    else if (w) aktion = `<a class="btn zwei klein" href="${esc(w.url)}" target="_blank" rel="noopener">👍 ${w.stimmen} · ${tr('Mitstimmen', 'Vote too')}</a>`;
    else {
      const ziel = `${REPO}/issues/new?template=bauwunsch.yml&title=${encodeURIComponent(`Bauwunsch: Idee #${i.nr} ${i.titel}`)}&bauwerk=${encodeURIComponent(i.titel)}`;
      aktion = `<a class="btn zwei klein" href="${esc(ziel)}" target="_blank" rel="noopener">👍 ${tr('Wünschen', 'Vote')}</a>`;
    }
    return `<article class="idee" data-kat="${i.kategorie}"${mitId ? ` id="idee-${i.nr}"` : ''}>
      <div class="idee-kopf"><span class="idee-nr">Nr. ${i.nr}</span><span class="marker">${esc(GR[i.groesse] || tr('Anleitung', 'Guide'))}</span><span class="marker status-${i.status}">${ST[i.status]}</span></div>
      <h3>${esc(lo(i, 'titel'))}</h3><p>${esc(lo(i, 'text'))}</p>
      ${(i.plugins || []).length ? `<p class="idee-plugins">${tr('Plugin', 'Plugin')}: ${i.plugins.map((x) => `${pluginLink(pluginRef(k, x.id))} <span>(${STUFE[x.stufe].toLowerCase()})</span>`).join(', ')}</p>` : ''}
      <div class="idee-fuss">${aktion}</div></article>`;
  };
  const zahl = (st) => IDS.filter((i) => i.status === st).length;
  const filter = { kat: 'alle', gr: 'alle', q: '' };
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <h1>${tr('Geplant', 'Planned')}</h1>
    <p class="lede">${tr('Alle Ideen für neue Baupläne und Anleitungen: Farmen, Fabriken, Gebäude und Monumente. Stimm mit „Wünschen“ ab, was zuerst gebaut wird.', 'All ideas for new builds and guides: farms, factories, buildings and monuments. Vote with “Vote” for what gets built first.')}</p>
    <div class="ideen-zahlen">
      <div><b>${IDS.filter((i) => i.kategorie !== 'anleitungen').length}</b><span>${tr('Bauplan-Ideen', 'build ideas')}</span></div>
      <div><b>${IDS.filter((i) => i.kategorie === 'anleitungen').length}</b><span>${tr('Anleitungen', 'guides')}</span></div>
      <div><b>${zahl('in-arbeit')}</b><span>${ST['in-arbeit']}</span></div>
      <div><b>${D.umgesetzt || 0}</b><span><a href="${url('liste')}">${tr('schon als Bauplan fertig', 'already finished as builds')}</a></span></div>
    </div>
  </div></section>
  <div class="ideen-filter"><div class="wrap">
    <label class="suche"><span class="sr">${tr('Ideen durchsuchen', 'Search ideas')}</span>
      <input type="search" id="q" placeholder="${tr('Suchen, z. B. Bambus, Burg, Redstone', 'Search, e.g. bamboo, castle, redstone')}" autocomplete="off"></label>
    <div class="chips" role="group" aria-label="${tr('Kategorie', 'Category')}">
      ${[['alle', tr('Alle', 'All')], ...D.kategorien.map((c) => [c.id, lo(c, 'name')])].map(([id, n]) => `<button class="chip" data-kat="${id}" aria-pressed="${id === 'alle'}">${esc(n)}</button>`).join('')}
    </div>
    <div class="chips klein" role="group" aria-label="${tr('Größe', 'Size')}">
      ${[['alle', tr('Jede Größe', 'Any size')], ['klein', GR.klein], ['mittel', GR.mittel], ['groß', GR.groß]].map(([id, n]) => `<button class="chip" data-gr="${id}" aria-pressed="${id === 'alle'}">${esc(n)}</button>`).join('')}
    </div>
  </div></div>
  <section class="abschnitt" style="padding-top:18px"><div class="wrap" id="ideen"></div></section>`;
  const box = main.querySelector('#ideen');
  const passt = (i) => (filter.kat === 'alle' || i.kategorie === filter.kat) && (filter.gr === 'alle' || i.groesse === filter.gr)
    && (!filter.q || `${i.nr} ${lo(i, 'titel')} ${lo(i, 'text')} ${i.titel}`.toLowerCase().includes(filter.q));
  const zeige = () => {
    const teile = [];
    const ohneFilter = filter.kat === 'alle' && filter.gr === 'alle' && !filter.q;
    const empf = IDS.filter((i) => i.empfohlen);
    if (ohneFilter && empf.length) teile.push(`<section class="ideen-gruppe empfohlen"><h2>${tr('Als Nächstes', 'Up next')}</h2><p>${esc((D.empfohlen_text || {})[L] || '')}</p><div class="ideen-raster">${empf.map((i) => karte(i, false)).join('')}</div></section>`);
    for (const c of D.kategorien) {
      const liste = IDS.filter((i) => i.kategorie === c.id && passt(i));
      if (liste.length) teile.push(`<section class="ideen-gruppe" id="kat-${c.id}"><h2>${esc(lo(c, 'name'))} <span class="anzahl">${liste.length}</span></h2><p>${esc(lo(c, 'text'))}</p><div class="ideen-raster">${liste.map((i) => karte(i)).join('')}</div></section>`);
    }
    box.innerHTML = teile.join('') || `<div class="leer">${tr('Nichts gefunden. Wünsch dir die Idee doch einfach!', 'Nothing found. Why not request it?')} <a href="${url('wuensche')}">${tr('Zu den Wünschen', 'Go to wishes')}</a></div>`;
  };
  main.querySelectorAll('[data-kat].chip').forEach((b) => b.addEventListener('click', () => {
    filter.kat = b.dataset.kat; main.querySelectorAll('[data-kat].chip').forEach((x) => x.setAttribute('aria-pressed', x === b)); zeige();
  }));
  main.querySelectorAll('[data-gr]').forEach((b) => b.addEventListener('click', () => {
    filter.gr = b.dataset.gr; main.querySelectorAll('[data-gr]').forEach((x) => x.setAttribute('aria-pressed', x === b)); zeige();
  }));
  let qt; main.querySelector('#q').addEventListener('input', (e) => { clearTimeout(qt); qt = setTimeout(() => { filter.q = e.target.value.trim().toLowerCase(); zeige(); }, 120); });
  zeige();
  if (location.hash.startsWith('#idee-')) document.getElementById(location.hash.slice(1))?.scrollIntoView({ block: 'center' });
}

// Wo wird ein Plugin gebraucht? Baupläne und geplante Ideen
let IDEEN = null;
async function verwendetIn(k, id) {
  if (!IDEEN) IDEEN = fetch(`${BASE}data/ideen.json?v=${V}`).then((r) => r.json()).catch(() => ({ ideen: [] }));
  const D = await IDEEN;
  const bs = k.builds.filter((b) => (b.plugins || []).some((x) => x.id === id));
  const is = D.ideen.filter((i) => (i.plugins || []).some((x) => x.id === id));
  if (!bs.length && !is.length) return '';
  const st = (l) => STUFE[l.find((x) => x.id === id).stufe].toLowerCase();
  return `<h2 style="margin:28px 0 12px">${tr('Wird verwendet in', 'Used in')}</h2><ul class="verwendet">
    ${bs.map((b) => `<li><a href="${url('bau', b.id)}">${esc(lo(b, 'titel'))}</a> <span class="eyebrow">${tr('Bauplan', 'build')} · ${st(b.plugins)}</span></li>`).join('')}
    ${is.map((i) => `<li><a href="${url('geplant')}#idee-${i.nr}">${esc(lo(i, 'titel'))}</a> <span class="eyebrow">${tr('geplant', 'planned')} · Nr. ${i.nr} · ${st(i.plugins)}</span></li>`).join('')}</ul>`;
}

async function pluginSeite(id) {
  const k = await katalog();
  const p = k.plugins.find((x) => x.id === id);
  if (!p) return nichtGefunden();
  const wer = { spieler: tr('Spieler', 'Player'), admin: 'Admin', konsole: tr('Konsole', 'Console') };
  const en = !de && p.en ? p.en : {};
  const btext = (b, i) => en.befehle?.[i] ?? b.text;
  const ctext = (c, i) => en.config?.[i] ?? c.text;
  const cpunkte = (c, i) => en.changelog?.[i] ?? c.punkte;
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <div class="krumen"><a href="${url('plugins')}">Plugins</a> / ${esc(p.name)}</div>
    <div class="plugin-kopf"><span class="plugin-symbol" aria-hidden="true">${initialen(p.name)}</span><h1>${esc(p.name)}</h1></div>
    <p class="lede">${esc(lo(p, 'beschreibung'))}</p>
    <dl class="specs">
      <div><dt>Version</dt><dd>${esc(p.version)}</dd></div>
      <div><dt>${tr('Plattform', 'Platform')}</dt><dd>${esc(p.plattform)}</dd></div>
      <div><dt>${tr('Bereich', 'Area')}</dt><dd>${esc(pkat(k, p.kategorie))}</dd></div>
      <div><dt>${tr('Befehle', 'Commands')}</dt><dd>${p.befehle.length}</dd></div>
    </dl>
    ${p.status === 'doku' ? `<div class="hinweis"><span aria-hidden="true">⏳</span><span>${esc(lo(p, 'status_text'))}</span></div>` : ''}
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:16px">
      ${p.status === 'doku' ? `<span class="btn aus" aria-disabled="true">${tr('Download folgt', 'Download coming soon')}</span>` : `<a class="btn" href="${BASE}downloads/plugins/${p.id}.jar" download>${tr('.jar herunterladen', 'Download .jar')}</a>`}
    </div>
  </div></section>
  <section class="tafel"><div class="wrap">
    <div class="zwei-spalten">
      <div class="feld"><h2>${tr('Funktionen', 'Features')}</h2><ul class="funktionen">${lo(p, 'funktionen').map((f) => `<li>${esc(f)}</li>`).join('')}</ul></div>
      <div class="feld"><h2>${tr('Änderungen', 'Changelog')}</h2>${p.changelog.map((c, i) => `<h3 style="margin-top:14px">${esc(c.version)} <span class="eyebrow">${esc(c.datum)}</span></h3><ul class="funktionen">${cpunkte(c, i).map((x) => `<li>${esc(x)}</li>`).join('')}</ul>`).join('')}</div>
    </div>
    <h2 style="margin:28px 0 12px">${tr('Befehle', 'Commands')}</h2>
    <div class="tabelle-huelle"><table><thead><tr><th>${tr('Befehl', 'Command')}</th><th>${tr('Was er macht', 'What it does')}</th><th>${tr('Wer', 'Who')}</th></tr></thead><tbody>
      ${p.befehle.map((b, i) => `<tr><td><code>${esc(b.befehl)}</code></td><td>${esc(btext(b, i))}</td><td>${wer[b.wer] || b.wer}</td></tr>`).join('')}
    </tbody></table></div>
    ${await verwendetIn(k, p.id)}
    ${p.config.length ? `<h2 style="margin:28px 0 12px">${tr('Einstellungen in der config.yml', 'Settings in config.yml')}</h2>
    <div class="tabelle-huelle"><table><thead><tr><th>${tr('Schlüssel', 'Key')}</th><th>${tr('Standard', 'Default')}</th><th>${tr('Bedeutung', 'Meaning')}</th></tr></thead><tbody>
      ${p.config.map((c, i) => `<tr><td><code>${esc(c.schluessel)}</code></td><td><code>${esc(c.standard)}</code></td><td>${esc(ctext(c, i))}</td></tr>`).join('')}
    </tbody></table></div>` : ''}
  </div></section>`;
}

async function anleitungSeite(id) {
  const k = await katalog();
  const d = k.docs.find((x) => x.id === id);
  if (!d) return nichtGefunden();
  const html = await (await fetch(`${BASE}data/seiten/doc-${id}${!de && d.en ? '.en' : ''}.html?v=${V}`)).text();
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <div class="krumen"><a href="${url('anleitungen')}">${tr('Anleitungen', 'Guides')}</a> / ${esc(lo(d, 'titel'))}</div>
    <h1>${esc(lo(d, 'titel'))}</h1><p class="lede">${esc(lo(d, 'kurz'))}</p></div></section>
    <section class="tafel"><div class="wrap"><article class="prosa">${html}</article></div></section>`;
  main.querySelectorAll('.prosa a[href^="http"]').forEach((a) => { a.target = '_blank'; a.rel = 'noopener'; });
}

function nichtGefunden() {
  main.innerHTML = `<section class="detail-kopf"><div class="wrap"><h1>${tr('Nicht gefunden', 'Not found')}</h1><p class="lede">${tr('Diese Seite gibt es nicht.', 'This page does not exist.')} <a href="${url()}">${tr('Zur Startseite', 'Go to the home page')}</a></p></div></section>`;
}

/* ---------- Draufsicht einer Ebene (Norden oben, 0 = Mitte) ---------- */
// sicht(i, x, z) liefert 0 = nicht zeigen, 1 = schon gebaut (blass), 2 = normal, 3 = neu in diesem Schritt
function ebenePlan(cv, P, y, { maxW = 720, sicht = () => 2, hover = null } = {}) {
  const { X, Z, pal, grid, at } = P;
  const avail = Math.min(cv.parentElement.clientWidth - 28, maxW);
  const cs = Math.max(6, Math.floor((avail - 28) / X));
  const pad = 26, W = pad + cs * X + 4, H = pad + cs * Z + 4, dpr = window.devicePixelRatio || 1;
  cv.width = W * dpr; cv.height = H * dpr; cv.style.width = W + 'px'; cv.style.height = H + 'px';
  const g = cv.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.fillStyle = cssv('--sheet-2'); g.fillRect(0, 0, W, H);
  g.fillStyle = cssv('--sheet'); g.fillRect(pad, pad, cs * X, cs * Z);
  if (y > 0) {   // Ebene darunter als Schatten, damit man weiß, worauf man baut
    g.fillStyle = cssv('--ink'); g.globalAlpha = .1;
    for (let z = 0; z < Z; z++) for (let x = 0; x < X; x++) if (grid[at(x, y - 1, z)] >= 0) g.fillRect(pad + x * cs, pad + z * cs, cs, cs);
    g.globalAlpha = 1;
  }
  g.strokeStyle = cssv('--line'); g.lineWidth = 1;
  for (let i = 0; i <= Math.max(X, Z); i++) {
    if (i <= X) { g.beginPath(); g.moveTo(pad + i * cs + .5, pad); g.lineTo(pad + i * cs + .5, pad + Z * cs); g.stroke(); }
    if (i <= Z) { g.beginPath(); g.moveTo(pad, pad + i * cs + .5); g.lineTo(pad + X * cs, pad + i * cs + .5); g.stroke(); }
  }
  const neu = [];
  for (let z = 0; z < Z; z++) for (let x = 0; x < X; x++) {
    const i = grid[at(x, y, z)]; if (i < 0) continue;
    const st = sicht(i, x, z); if (!st) continue;
    const p = pal[i]; const small = /thin|pane|panel|plate|mob/.test(p.shape);
    const ins = small ? Math.max(1, Math.round(cs * .22)) : 1;
    g.globalAlpha = p.context ? .3 : st === 1 ? .38 : 1; g.fillStyle = p.color;
    g.fillRect(pad + x * cs + ins, pad + z * cs + ins, cs - ins * 2 + 1, cs - ins * 2 + 1);
    g.globalAlpha = 1;
    if (st === 3) neu.push([x, z]);
  }
  if (neu.length) {   // neue Blöcke gelb umrandet, wie in der 3D-Ansicht
    g.strokeStyle = cssv('--hl'); g.lineWidth = Math.max(1.5, cs * .14);
    for (const [x, z] of neu) g.strokeRect(pad + x * cs + 1.5, pad + z * cs + 1.5, cs - 3, cs - 3);
  }
  const cx = (X - 1) / 2, cz = (Z - 1) / 2;
  g.fillStyle = cssv('--ink-mute'); g.font = `10px ${cssv('--f-mono')}`; g.textAlign = 'center'; g.textBaseline = 'middle';
  for (let i = 0; i < X; i++) { const r = Math.round(i - cx); if (r % 5 === 0 && Math.abs(i - cx - r) < .01) g.fillText(r > 0 ? '+' + r : r, pad + (i + .5) * cs, 12); }
  g.textAlign = 'right';
  for (let i = 0; i < Z; i++) { const r = Math.round(i - cz); if (r % 5 === 0 && Math.abs(i - cz - r) < .01) g.fillText(r > 0 ? '+' + r : r, pad - 4, pad + (i + .5) * cs); }
  g.textAlign = 'left'; g.fillStyle = cssv('--ink'); g.font = `bold 11px ${cssv('--f-mono')}`; g.fillText('N ↑', 2, 10);
  if (hover) { g.strokeStyle = cssv('--ink'); g.lineWidth = 2; g.strokeRect(pad + hover.x * cs + 1, pad + hover.z * cs + 1, cs - 2, cs - 2); }
  return { pad, cs };
}
// Name und Position des Blocks unter dem Zeiger
function planAblesen(P, y, x, z) {
  const { X, Z, pal, grid, at } = P;
  const i = grid[at(x, y, z)]; const sg = (v) => (v > 0 ? '+' + v : v);
  return `<b>${i < 0 ? tr('Luft (frei lassen)', 'Air (leave empty)') : esc(bn(pal[i]))}</b><br>X ${sg(Math.round(x - (X - 1) / 2))} · Y ${y} · Z ${sg(Math.round(z - (Z - 1) / 2))}${i >= 0 && pal[i].block ? ` · <code>${esc(pal[i].block)}</code>` : ''}`;
}

/* ---------- Bauplan-Detail ---------- */
async function bauSeite(id, tab) {
  const k = await katalog();
  const kb = k.builds.find((b) => b.id === id);
  if (!kb) return nichtGefunden();
  const d = await ladeBau(id);
  const tabs = [['anleitung', tr('Anleitung', 'Instructions')], ['teile', tr('Teileliste', 'Parts list')], ['ebenen', tr('Ebenen', 'Layers')], ['downloads', 'Downloads']];
  const HASH = { teile: tr('teile', 'parts'), ebenen: tr('ebenen', 'layers'), downloads: 'downloads' };
  tab = Object.keys(HASH).find((x) => HASH[x] === tab || x === tab) || tab;
  tab = tabs.some((t) => t[0] === tab) ? tab : 'anleitung';
  main.innerHTML = `<section class="detail-kopf"><div class="wrap">
    <div class="krumen"><a href="${url('liste')}">${tr('Baupläne', 'Builds')}</a> / ${esc(kats(k)[d.kategorie] || '')}</div>
    <h1>${esc(lo(d, 'titel'))}</h1>
    <p class="lede">${esc(lo(d, 'beschreibung'))}</p>
    <dl class="specs">
      <div><dt>${tr('Schwierigkeit', 'Difficulty')}</dt><dd>${punkte(d.schwierigkeit)}</dd></div>
      <div><dt>${tr('Blöcke', 'Blocks')}</dt><dd>${fmt(kb.bloecke)}</dd></div>
      <div><dt>${tr('Schritte', 'Steps')}</dt><dd>${kb.schritte}</dd></div>
      <div><dt>${tr('Grundfläche', 'Footprint')}</dt><dd>${esc(lo(d, 'grundflaeche'))}</dd></div>
      <div><dt>${tr('Höhe', 'Height')}</dt><dd>${d.model.size.y} ${tr('Ebenen', 'layers')}</dd></div>
      <div><dt>${tr('Bauzeit', 'Build time')}</dt><dd>${stunden(d.bauzeit_stunden)}</dd></div>
      <div><dt>Edition</dt><dd>${(d.edition || []).map((e) => (e === 'java' ? 'Java' : 'Bedrock')).join(' · ')}</dd></div>
      <div><dt>Plugins</dt><dd>${(d.plugins || []).length ? (d.plugins || []).map((x) => `${esc(pluginRef(k, x.id).name)} <small>(${STUFE[x.stufe].toLowerCase()})</small>`).join(', ') : tr('keine nötig', 'none needed')}</dd></div>
    </dl>
    ${d.status === 'entwurf' ? `<div class="hinweis"><span aria-hidden="true">⚠️</span><span><b>${tr('Entwurf', 'Draft')}:</b> ${esc(lo(d, 'hinweis') || '')}</span></div>` : ''}
    ${pluginKasten(k, d.plugins)}
    <div class="reiter" role="tablist">${tabs.map(([t, n]) => `<button role="tab" aria-selected="${t === tab}" data-tab="${t}">${n}</button>`).join('')}</div>
  </div></section>
  <section class="tafel"><div class="wrap" id="tafel"></div></section>`;
  main.querySelectorAll('.reiter button').forEach((b) => b.addEventListener('click', () => {
    history.replaceState(null, '', url('bau', id) + (b.dataset.tab === 'anleitung' ? '' : '#' + HASH[b.dataset.tab]));
    sprachLinks();
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
    el.innerHTML = `<div class="schritt-raster">
      <div class="buehne bauplan">
        <div class="nummer" id="nr" aria-live="polite"></div>
        <div class="werkzeug">
          <button class="rund" id="rl" title="${tr('Nach links drehen', 'Rotate left')}" aria-label="${tr('Modell nach links drehen', 'Rotate model left')}">⟲</button>
          <button class="rund" id="rr" title="${tr('Nach rechts drehen', 'Rotate right')}" aria-label="${tr('Modell nach rechts drehen', 'Rotate model right')}">⟳</button>
          <button class="rund" id="all" aria-pressed="false" title="${tr('Ganzes Bauwerk', 'Whole build')}" aria-label="${tr('Ganzes Bauwerk zeigen', 'Show the whole build')}">◎</button>
        </div>
        <canvas id="cv" class="drehbar" aria-label="${tr('3D-Ansicht des aktuellen Bauschritts, zum Drehen ziehen', '3D view of the current build step, drag to rotate')}"></canvas>
        <div class="blick"><span id="blick"></span><span class="dreh-hinweis">${matchMedia('(pointer: coarse)').matches ? tr('Wischen zum Drehen', 'Swipe to rotate') : tr('Ziehen zum Drehen', 'Drag to rotate')}</span></div>
      </div>
      <div class="plan-kasten">
        <div class="plan-kopf"><h3 id="plan-titel"></h3><span class="eyebrow">${tr('Draufsicht, Norden oben, gelb umrandet ist neu', 'Top view, north up, yellow outline is new')}</span></div>
        <div class="plan-huelle"><canvas id="plan" aria-label="${tr('Draufsicht der Ebene dieses Schritts', 'Top view of this step’s layer')}"></canvas></div>
        <div class="ablesen" id="plan-les">${tr('Zeige oder tippe auf ein Feld für Block und Position.', 'Point at or tap a square for block and position.')}</div>
      </div>
      <div class="seite">
        <div class="teile-kasten" id="teile"></div>
        <div class="steuer">
          <button class="btn zwei" id="zurueck" aria-label="${tr('Vorheriger Schritt', 'Previous step')}">← ${tr('Zurück', 'Back')}</button>
          <button class="btn" id="weiter" aria-label="${tr('Nächster Schritt', 'Next step')}">${tr('Weiter', 'Next')} →</button>
        </div>
        <input class="leiste" type="range" id="leiste" min="1" max="${n}" aria-label="${tr('Schritt wählen', 'Choose step')}">
        <label class="erledigt"><input type="checkbox" id="ok"> ${tr('Schritt erledigt', 'Step done')}</label>
        <div><div class="fortschritt"><i id="balken"></i></div><div class="eyebrow" id="stand" style="margin-top:6px"></div></div>
        <div class="abschnitt-info" id="ab"></div>
      </div>
    </div>
    ${d.tipps?.length ? `<h2 style="margin:30px 0 12px">${tr('Tipps', 'Tips')}</h2><div class="raster">${lo(d, 'tipps').map((t) => `<div class="tipp"><b>${esc(t.titel)}</b>${esc(t.text)}</div>`).join('')}</div>` : ''}`;
    const cv = el.querySelector('#cv'), pc = el.querySelector('#plan');
    const RICHTUNG = [tr('Südost', 'south-east'), tr('Nordost', 'north-east'), tr('Nordwest', 'north-west'), tr('Südwest', 'south-west')];
    let planGeo = null, planHover = null;
    const zustand = (x, y, z) => {
      if (alles) return 2;
      const s = stepOf[P.at(x, y, z)];
      if (s < 0) return 1;
      return s < cur ? 1 : s === cur ? 3 : 0;
    };
    const paint = () => {
      const w = cv.parentElement.clientWidth - 2;
      const h = Math.max(320, Math.min(window.innerHeight * .62, 560));
      draw(cv, P, { width: w, maxHeight: h, rot, fit: true, padTop: 70, ...farben(), fadeTo: cssv('--plan'), ground: null, state: (i, x, y, z) => zustand(x, y, z) });
      el.querySelector('#blick').textContent = tr(`Blick von ${RICHTUNG[rot]}`, `View from the ${RICHTUNG[rot]}`);
      paintPlan();
    };
    const paintPlan = () => {
      const y = S[cur].y[0];
      planGeo = ebenePlan(pc, P, y, { maxW: 760, hover: planHover, sicht: (i, x, z) => {
        const st = stepOf[P.at(x, y, z)];
        if (st < 0) return 2;               // Gelände, schon vorhanden
        return st < cur ? 1 : st === cur ? 3 : 0;
      } });
    };
    pc.addEventListener('pointermove', (e) => {
      const r = pc.getBoundingClientRect();
      const x = Math.floor((e.clientX - r.left - planGeo.pad) / planGeo.cs), z = Math.floor((e.clientY - r.top - planGeo.pad) / planGeo.cs);
      planHover = x >= 0 && z >= 0 && x < P.X && z < P.Z ? { x, z } : null; paintPlan();
      if (planHover) el.querySelector('#plan-les').innerHTML = planAblesen(P, S[cur].y[0], x, z);
    });
    pc.addEventListener('pointerleave', () => { planHover = null; paintPlan(); });
    // Drehen: Knöpfe, Ziehen mit Maus oder Finger (alle 60 px eine Vierteldrehung), Tasten Q und E
    const drehe = (r) => { rot = (rot + r + 4) % 4; paint(); };
    let zieh = null;
    cv.addEventListener('pointerdown', (e) => { zieh = { x: e.clientX, id: e.pointerId }; cv.setPointerCapture(e.pointerId); cv.classList.add('zieht'); });
    cv.addEventListener('pointermove', (e) => {
      if (!zieh || e.pointerId !== zieh.id) return;
      const dx = e.clientX - zieh.x;
      if (Math.abs(dx) >= 60) { drehe(dx > 0 ? 1 : -1); zieh.x = e.clientX; }
    });
    const loslassen = () => { zieh = null; cv.classList.remove('zieht'); };
    cv.addEventListener('pointerup', loslassen); cv.addEventListener('pointercancel', loslassen);
    const update = () => {
      const s = S[cur];
      store.set('schritt.' + d.id, cur);
      el.querySelector('#nr').innerHTML = `${cur + 1}<small>${tr('von', 'of')} ${n}</small>`;
      const zahl = new Map();
      for (let j = 3; j < s.c.length; j += 4) zahl.set(s.c[j], (zahl.get(s.c[j]) || 0) + 1);
      const teile = [...zahl].filter(([i]) => zaehlt(pal[i]) || (pal[i].flags || []).includes('kein-block')).sort((a, b) => b[1] - a[1]);
      const summe = teile.filter(([i]) => zaehlt(pal[i])).reduce((a, [, c]) => a + c, 0);
      el.querySelector('#teile').innerHTML = `<h3>${tr('Neue Teile in diesem Schritt', 'New parts in this step')} <span>${summe} ${tr('Blöcke', 'blocks')}</span></h3>
        <div class="teile">${teile.map(([i, c]) => `<div class="teil" title="${esc(bn(pal[i]))}"><img src="${partIcon(pal[i])}" alt=""><b>×${c}</b><span>${esc(bn(pal[i]))}</span></div>`).join('')}</div>`;
      const ab = (lo(d, 'abschnitte') || [])[s.a] || {};
      const teil = s.t && s.t[1] > 1 ? tr(` · Teil ${s.t[0]} von ${s.t[1]}`, ` · part ${s.t[0]} of ${s.t[1]}`) : '';
      const ebene = ebeneText(s.y[0], s.y[1]) + teil;
      el.querySelector('#plan-titel').textContent = ebene;
      el.querySelector('#ab').innerHTML = `<span class="eyebrow">${ebene}</span><h3 style="margin-top:4px">${esc(ab.name || '')}</h3><p>${esc(ab.text || '')}</p>`;
      el.querySelector('#leiste').value = cur + 1;
      el.querySelector('#ok').checked = done.has(cur);
      el.querySelector('#zurueck').disabled = cur === 0;
      el.querySelector('#weiter').disabled = cur === n - 1;
      el.querySelector('#balken').style.width = (done.size / n * 100) + '%';
      el.querySelector('#stand').textContent = tr(`${done.size} von ${n} Schritten erledigt`, `${done.size} of ${n} steps done`);
      paint();
    };
    const go = (k2) => { cur = Math.max(0, Math.min(n - 1, k2)); update(); };
    el.querySelector('#zurueck').onclick = () => go(cur - 1);
    el.querySelector('#weiter').onclick = () => go(cur + 1);
    el.querySelector('#leiste').oninput = (e) => go(+e.target.value - 1);
    el.querySelector('#rl').onclick = () => drehe(-1);
    el.querySelector('#rr').onclick = () => drehe(1);
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
      if (e.key === 'q' || e.key === 'Q') drehe(-1);
      if (e.key === 'e' || e.key === 'E') drehe(1);
    };
    onRedraw(paint);
    update();
  }

  function teileTab(el, d, pal) {
    const gesamt = d.teileliste.reduce((a, t) => a + t.n, 0);
    el.innerHTML = `<div class="zwei-spalten">
      <div><h2 style="margin-bottom:12px">${tr('Gesamt-Teileliste', 'Complete parts list')}</h2>
        <div class="tabelle-huelle"><table><thead><tr><th>Block</th><th class="zahl">${tr('Anzahl', 'Count')}</th><th class="zahl">Stacks</th></tr></thead><tbody>
        ${d.teileliste.map((t) => { const p = pal[t.i]; return `<tr><td><div class="block-zelle"><img src="${partIcon(p, 30)}" alt=""><div>${esc(bn(p))}<small>${esc((p.block || '').replace(/\[.*$/, ''))}</small></div></div></td><td class="zahl">${fmt(t.n)}</td><td class="zahl">${stacks(t.n)}</td></tr>`; }).join('')}
        <tr><td><b>${tr('Summe', 'Total')}</b></td><td class="zahl"><b>${fmt(gesamt)}</b></td><td class="zahl">${stacks(gesamt)}</td></tr>
        </tbody></table></div></div>
      <div><h2 style="margin-bottom:12px">${tr('Was deine Farmen liefern müssen', 'What your farms need to deliver')}</h2>
        <div class="tabelle-huelle"><table><thead><tr><th>${tr('Rohstoff', 'Material')}</th><th class="zahl">${tr('Menge', 'Amount')}</th></tr></thead><tbody>
        ${(lo(d, 'rohstoffe') || []).map((r, i) => `<tr><td><b>${esc(r.name)}</b><div style="font-size:.85rem;color:var(--ink-soft)">${esc(r.quelle)} · ${esc(r.hinweis)}</div></td><td class="zahl">${fmt(d.rohstoffe[i].menge)}</td></tr>`).join('')}
        </tbody></table></div>
        ${d.schmelzvorgaenge ? `<div class="tipp" style="margin-top:14px"><b>${tr('Ofen-Arbeit', 'Furnace work')}</b>${tr(`${fmt(d.schmelzvorgaenge)} Schmelzvorgänge, also rund ${fmt(Math.ceil(d.schmelzvorgaenge / 20))} getrocknete Seetangblöcke oder ${fmt(Math.ceil(d.schmelzvorgaenge / 8))} Kohle.`, `${fmt(d.schmelzvorgaenge)} smelting operations, about ${fmt(Math.ceil(d.schmelzvorgaenge / 20))} dried kelp blocks or ${fmt(Math.ceil(d.schmelzvorgaenge / 8))} coal.`)}</div>` : ''}
        <h2 style="margin:26px 0 12px">${tr('Bauabschnitte', 'Build sections')}</h2>
        ${(lo(d, 'abschnitte') || []).map((a, i) => `<div class="abschnitt-info" style="margin-bottom:8px"><span class="eyebrow">${ebeneText(d.abschnitte[i].von, d.abschnitte[i].bis)}</span><h3 style="margin-top:4px">${esc(a.name)}</h3><p>${esc(a.text)}</p></div>`).join('')}
      </div></div>`;
  }

  function ebenenTab(el, d, P) {
    const { X, Y, Z, pal, grid, at } = P;
    let y = 0, hover = null;
    el.innerHTML = `<div class="ebenen">
      <div class="raster-huelle">
        <div class="steuer" style="margin-bottom:12px"><button class="rund" id="ab" aria-label="${tr('Eine Ebene tiefer', 'One layer down')}">−</button>
          <b id="yl" style="font:800 1.4rem var(--f-display);min-width:6ch;text-align:center"></b>
          <button class="rund" id="auf" aria-label="${tr('Eine Ebene höher', 'One layer up')}">+</button>
          <input class="leiste" type="range" id="ys" min="0" max="${Y - 1}" aria-label="${tr('Ebene', 'Layer')}"></div>
        <canvas id="gc" aria-label="${tr('Draufsicht der Ebene, Norden ist oben', 'Top view of the layer, north is up')}"></canvas>
        <div class="ablesen" id="les">${tr('Zeige auf einen Block, um Name und Position zu sehen. Norden ist oben, 0 ist die Mitte.', 'Point at a block to see its name and position. North is up, 0 is the centre.')}</div>
      </div>
      <div class="feld"><h3 style="margin-bottom:10px">${tr('In dieser Ebene', 'In this layer')}</h3><ul class="legende" id="leg"></ul></div></div>`;
    const cv = el.querySelector('#gc');
    let geo = null;
    const paint = () => {
      geo = ebenePlan(cv, P, y, { hover });
      const counts = new Map();
      for (let z = 0; z < Z; z++) for (let x = 0; x < X; x++) { const i = grid[at(x, y, z)]; if (i >= 0 && zaehlt(pal[i])) counts.set(i, (counts.get(i) || 0) + 1); }
      el.querySelector('#yl').textContent = tr(`Ebene ${y}`, `Layer ${y}`);
      el.querySelector('#ys').value = y;
      const items = [...counts].sort((a, b) => b[1] - a[1]);
      el.querySelector('#leg').innerHTML = items.length ? items.map(([i, c]) => `<li><img src="${partIcon(pal[i], 24)}" alt=""><span>${esc(bn(pal[i]))}</span><b>${c}</b></li>`).join('')
        + `<li style="border-top:1px solid var(--line);padding-top:6px"><span></span><b>${tr('Summe', 'Total')}</b><b>${items.reduce((a, [, c]) => a + c, 0)}</b></li>` : `<li>${tr('Keine Blöcke in dieser Ebene.', 'No blocks in this layer.')}</li>`;
    };
    const setY = (v) => { y = Math.max(0, Math.min(Y - 1, v)); hover = null; paint(); };
    el.querySelector('#ab').onclick = () => setY(y - 1);
    el.querySelector('#auf').onclick = () => setY(y + 1);
    el.querySelector('#ys').oninput = (e) => setY(+e.target.value);
    cv.addEventListener('pointermove', (e) => {
      const r = cv.getBoundingClientRect(); const x = Math.floor((e.clientX - r.left - geo.pad) / geo.cs), z = Math.floor((e.clientY - r.top - geo.pad) / geo.cs);
      hover = x >= 0 && z >= 0 && x < X && z < Z ? { x, z } : null; paint();
      if (hover) el.querySelector('#les').innerHTML = planAblesen(P, y, x, z);
    });
    onRedraw(paint);
    paint();
  }

  function downloadTab(el, d) {
    const info = {
      litematic: ['Litematica', tr('Für Java mit der Mod Litematica: Der Bauplan erscheint als Geisterblöcke im Spiel. Datei in den Ordner .minecraft/schematics legen.', 'For Java with the Litematica mod: the build appears as ghost blocks in the game. Put the file into the .minecraft/schematics folder.')],
      schem: ['WorldEdit', tr('Für WorldEdit oder FastAsyncWorldEdit auf dem Server: in den Ordner plugins/WorldEdit/schematics legen, dann //schem load.', 'For WorldEdit or FastAsyncWorldEdit on the server: put it into the plugins/WorldEdit/schematics folder, then //schem load.')],
      csv: [tr('Teileliste', 'Parts list'), tr('Alle Blöcke mit Anzahl und Stacks, öffnet sich in Excel, LibreOffice oder Google Tabellen.', 'All blocks with count and stacks, opens in Excel, LibreOffice or Google Sheets.')],
    };
    el.innerHTML = `${d.downloads.length ? `<div class="dl-raster">${d.downloads.map((x) => `<div class="dl"><span class="eyebrow">${info[x.art][0]}</span><span class="endung">.${x.art}</span><p>${info[x.art][1]}</p><a class="btn" href="${BASE}downloads/${d.id}/${x.datei}" download>${tr('Herunterladen', 'Download')} <span style="font-weight:400;opacity:.75">${(x.groesse / 1024).toFixed(x.groesse < 10240 ? 1 : 0)} KB</span></a></div>`).join('')}</div>` : `<div class="leer">${tr('Downloads werden beim nächsten Aufbau der Seite erzeugt.', 'Downloads are generated on the next site build.')}</div>`}
      ${d.status === 'entwurf' ? `<div class="hinweis" style="margin-top:18px"><span aria-hidden="true">⚠️</span><span>${tr('Dieser Bauplan ist ein Entwurf: Die Richtung von Treppen, Türen und Trichtern stimmt in den Dateien eventuell noch nicht. Nach dem Einfügen kurz prüfen.', 'This build is a draft: the direction of stairs, doors and hoppers may not be right in the files yet. Check briefly after pasting.')}</span></div>` : ''}`;
  }
}

/* ---------- Router ---------- */
let keyHandler = null;
document.addEventListener('keydown', (e) => keyHandler && keyHandler(e));
const TITEL = 'Bauwerkstatt';
const ART = {};   // Adress-Teil -> Seitenart, für beide Sprachen
for (const lang of ['de', 'en']) for (const [art, seg] of Object.entries(SEG[lang])) ART[seg] = art;
let aktuell = { art: 'start', id: null };

// Sprachschalter zeigt immer auf dieselbe Seite in der anderen Sprache
function sprachLinks() {
  const HASH_ANDERS = { teile: 'parts', parts: 'teile', ebenen: 'layers', layers: 'ebenen', downloads: 'downloads' };
  const h = location.hash.replace(/^#/, '');
  document.querySelectorAll('[data-lang]').forEach((l) => {
    const lang = l.dataset.lang;
    l.href = url(aktuell.art, aktuell.id, lang) + (h && lang !== L ? '#' + (HASH_ANDERS[h] || h) : h ? '#' + h : '');
  });
}

async function route() {
  redrawers = []; keyHandler = null;
  // alte Links der Form #/bau/... auf echte Adressen umleiten
  if (location.hash.startsWith('#/')) {
    const alt = location.hash.slice(2).split('/').filter(Boolean);
    const tab = alt[0] === 'bau' && alt[2] ? '#' + alt[2] : '';
    history.replaceState(null, '', BASE + (alt.length ? alt.slice(0, 2).join('/') + '/' : '') + tab);
  }
  let teile = relPfad().split('/').filter(Boolean);
  if (teile[0] === 'en') teile = teile.slice(1);
  const art = teile.length ? ART[teile[0]] || 'unbekannt' : 'start';
  const id = teile[1] || null;
  const c = location.hash.replace(/^#/, '') || undefined;
  aktuell = { art, id };
  const nav = { bau: 'liste', liste: 'liste', plugins: 'plugins', plugin: 'plugins', anleitungen: 'anleitungen', anleitung: 'anleitungen', wuensche: 'wuensche', geplant: 'geplant' }[art] || '';
  document.querySelectorAll('[data-nav]').forEach((l) => {
    if (l.dataset.nav === nav) l.setAttribute('aria-current', 'page'); else l.removeAttribute('aria-current');
  });
  sprachLinks();
  try {
    if (art === 'start') await startSeite();
    else if (art === 'liste') await bauplaeneSeite();
    else if (art === 'plugins') await pluginsSeite();
    else if (art === 'anleitungen') await anleitungenSeite();
    else if (art === 'wuensche') await wuenscheSeite();
    else if (art === 'geplant') await geplantSeite();
    else if (art === 'bau') await bauSeite(id, c);
    else if (art === 'plugin') await pluginSeite(id);
    else if (art === 'anleitung') await anleitungSeite(id);
    else nichtGefunden();
  } catch (err) {
    console.error(err);
    main.innerHTML = `<section class="detail-kopf"><div class="wrap"><h1>${tr('Das hat nicht geklappt', 'Something went wrong')}</h1><p class="lede">${tr('Die Daten konnten nicht geladen werden. Lade die Seite neu oder versuch es später noch einmal.', 'The data could not be loaded. Reload the page or try again later.')}</p></div></section>`;
  }
  const h1 = main.querySelector('h1');
  if (!erstAufruf) document.title = h1 && art !== 'start' ? `${h1.textContent} · ${TITEL}` : TITEL;
  erstAufruf = false;
}
let erstAufruf = true;   // beim ersten Laden bleibt der vorgerenderte Seitentitel
// interne Links ohne Neuladen öffnen; ein Sprachwechsel lädt die Seite neu
const istEn = (p) => /^en(\/|$)/.test(p.startsWith(BASE) ? p.slice(BASE.length) : p);
document.addEventListener('click', (e) => {
  const l = e.target.closest('a[href]');
  if (!l || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  if (l.target || l.hasAttribute('download') || l.dataset.lang) return;
  const ziel = new URL(l.href, location.href);
  if (ziel.origin !== location.origin || !ziel.pathname.startsWith(BASE)) return;
  if (/\.(xml|txt|json|png|svg|litematic|schem|csv)$/.test(ziel.pathname)) return;
  if (istEn(decodeURIComponent(ziel.pathname)) !== (L === 'en')) return;
  if (ziel.pathname === location.pathname && ziel.hash) return;   // Sprungmarken auf derselben Seite
  e.preventDefault();
  history.pushState(null, '', ziel.pathname + ziel.search + ziel.hash);
  route().then(() => window.scrollTo(0, 0));
});
document.querySelectorAll('[data-lang]').forEach((l) => l.addEventListener('click', () => { try { localStorage.setItem('bw.sprache', l.dataset.lang); } catch { /* privat */ } }));
window.addEventListener('popstate', route);
route();
