// Isometrische Block-Darstellung auf Canvas, ohne Bibliotheken.
// Eigene Farben statt Minecraft-Texturen (Texturen gehören Mojang).
// Die Formen kommen aus den Block-Zuständen (facing, half, type, open ...), genau wie in tools/vorschau.py.

// Ältere Modelle ohne Minecraft-ID: Form aus dem deutschen Namen raten
export const shapeOf = (n) =>
  /Dorfbewohner/.test(n) ? 'mob' :
  /Redstonestaub|Seerosenblatt|Teppich|Blütenblätter/.test(n) ? 'flat' :
  /Komparator|Verstärker/.test(n) ? 'thinplate' :
  /Karotten|Kartoffeln/.test(n) ? 'plant' :
  /Bett/.test(n) ? 'bed' :
  /Falltür/.test(n) ? 'trapdoor' :
  /zauntor/i.test(n) ? 'gate' :
  /tür/i.test(n) ? 'door' :
  /zaun/i.test(n) ? 'fence' :
  /mauer/i.test(n) ? 'wall' :
  /eisengitter|Glasscheibe/i.test(n) ? 'pane' :
  /blitzableiter|leiter|fackel|bambus/i.test(n) ? 'rod' :
  /laterne/i.test(n) ? 'lantern' :
  /Stufe/.test(n) ? 'slab' :
  /^Glas$/.test(n) ? 'glass' :
  /Wasser|Meer/.test(n) ? 'water' : 'full';

// 'minecraft:oak_stairs[facing=east,half=top]' -> ['oak_stairs', {facing: 'east', half: 'top'}]
export function readBlock(s) {
  const m = /^(?:[a-z_]+:)?([a-z0-9_]+)(?:\[(.*)\])?/.exec(s || '');
  if (!m) return ['', {}];
  const st = {};
  if (m[2]) for (const t of m[2].split(',')) { const [k, v] = t.split('='); if (v !== undefined) st[k.trim()] = v.trim(); }
  return [m[1], st];
}
const PLANTS = new Set(['short_grass', 'grass', 'fern', 'dead_bush', 'poppy', 'dandelion', 'cornflower', 'oxeye_daisy', 'allium',
  'azure_bluet', 'blue_orchid', 'lily_of_the_valley', 'sweet_berry_bush', 'wheat', 'carrots', 'potatoes', 'beetroots', 'kelp',
  'seagrass', 'sugar_cane']);
export function shapeOfBlock(bid, name) {
  if (!bid) return shapeOf(name);
  if (bid === 'water' || bid === 'bubble_column') return 'water';
  if (bid === 'glass' || bid === 'tinted_glass' || (bid.endsWith('_stained_glass'))) return 'glass';
  for (const [suf, f] of [['_stairs', 'stairs'], ['_slab', 'slab'], ['_trapdoor', 'trapdoor'], ['_door', 'door'], ['_pane', 'pane'],
    ['_fence_gate', 'gate'], ['_fence', 'fence'], ['_wall', 'wall'], ['_carpet', 'flat'], ['_pressure_plate', 'plate'], ['_bed', 'bed'], ['_button', 'button']]) {
    if (bid.endsWith(suf) && !(suf === '_wall' && bid.endsWith('_wall_sign'))) return f;
  }
  if (bid === 'iron_bars') return 'pane';
  if (bid.startsWith('potted_') || bid === 'flower_pot') return 'pot';
  if (bid === 'lantern' || bid === 'soul_lantern') return 'lantern';
  if (['end_rod', 'lightning_rod', 'chain', 'bamboo', 'ladder'].includes(bid) || bid.endsWith('torch')) return 'rod';
  if (bid === 'campfire' || bid === 'soul_campfire') return 'campfire';
  if (bid === 'daylight_detector') return 'detector';
  if (bid === 'brewing_stand') return 'stand';
  if (['lily_pad', 'redstone_wire', 'pink_petals', 'moss_carpet', 'snow'].includes(bid)) return 'flat';
  if (PLANTS.has(bid) || bid.endsWith('_tulip') || bid.endsWith('_sapling')) return 'plant';
  if (['lectern', 'enchanting_table', 'stonecutter'].includes(bid)) return 'low';
  if (bid === 'comparator' || bid === 'repeater') return 'thinplate';
  if (bid === 'villager') return 'mob';
  return 'full';
}
const CONNECTS = new Set(['full', 'glass', 'pane', 'fence', 'wall', 'stairs', 'gate']);
const TURN = { north: 'east', east: 'south', south: 'west', west: 'north' };
const turn = (f, n) => { for (let k = 0; k < n; k++) f = TURN[f] || f; return f; };
const PLANT = [92, 140, 58], FLAME = [255, 170, 60];

// Quader einer Form: [u0, u1, y0, y1, v0, v1, Helligkeit, Farbe?] im Block (0..1); nb(du, dv) = Form des Nachbarn
function boxes(a, st, nb) {
  const f = st.facing || 'north', d = .1875;
  switch (a) {
    case 'water': return [[0, 1, 0, .88, 0, 1, 1]];
    case 'slab': return st.type === 'double' ? [[0, 1, 0, 1, 0, 1, 1]] : st.type === 'top' ? [[0, 1, .5, 1, 0, 1, 1]] : [[0, 1, 0, .5, 0, 1, 1]];
    case 'stairs': {
      const top = st.half === 'top', y0 = top ? 0 : .5, y1 = top ? .5 : 1;
      const back = { north: [0, 1, y0, y1, 0, .5, 1], south: [0, 1, y0, y1, .5, 1, 1], east: [.5, 1, y0, y1, 0, 1, 1], west: [0, .5, y0, y1, 0, 1, 1] }[f];
      return [top ? [0, 1, .5, 1, 0, 1, 1] : [0, 1, 0, .5, 0, 1, 1], back];
    }
    case 'trapdoor':
      if (st.open === 'true') return [{ north: [0, 1, 0, 1, 1 - d, 1, .95], south: [0, 1, 0, 1, 0, d, .95], east: [0, d, 0, 1, 0, 1, .95], west: [1 - d, 1, 0, 1, 0, 1, .95] }[f]];
      return st.half === 'top' ? [[0, 1, 1 - d, 1, 0, 1, .95]] : [[0, 1, 0, d, 0, 1, .95]];
    case 'door': return [{ north: [0, 1, 0, 1, 1 - d, 1, .95], south: [0, 1, 0, 1, 0, d, .95], east: [0, d, 0, 1, 0, 1, .95], west: [1 - d, 1, 0, 1, 0, 1, .95] }[f]];
    case 'pane': case 'fence': case 'wall': {
      const [p0, p1, a0, a1, h0, h1] = a === 'pane' ? [.4375, .5625, .4375, .5625, 0, 1] : a === 'fence' ? [.375, .625, .4375, .5625, .375, .9375] : [.25, .75, .3125, .6875, 0, .875];
      const q = [[p0, p1, 0, 1, p0, p1, 1]];
      if (CONNECTS.has(nb(0, -1))) q.push([a0, a1, h0, h1, 0, p0, 1]);
      if (CONNECTS.has(nb(0, 1))) q.push([a0, a1, h0, h1, p1, 1, 1]);
      if (CONNECTS.has(nb(-1, 0))) q.push([0, p0, h0, h1, a0, a1, 1]);
      if (CONNECTS.has(nb(1, 0))) q.push([p1, 1, h0, h1, a0, a1, 1]);
      return q;
    }
    case 'gate': return f === 'north' || f === 'south' ? [[0, 1, .3, 1, .4375, .5625, 1]] : [[.4375, .5625, .3, 1, 0, 1, 1]];
    case 'flat': return [[0, 1, 0, .0625, 0, 1, 1]];
    case 'plate': return [[.0625, .9375, 0, .0625, .0625, .9375, 1]];
    case 'bed': return [[0, 1, 0, .5625, 0, 1, 1]];
    case 'button': return [[.3125, .6875, 0, .125, .375, .625, 1]];
    case 'pot': return [[.3125, .6875, 0, .375, .3125, .6875, 1], [.38, .62, .375, .95, .38, .62, 1, PLANT]];
    case 'lantern': return st.hanging === 'true' ? [[.3125, .6875, .0625, .5625, .3125, .6875, 1.15], [.47, .53, .5625, 1, .47, .53, .7]] : [[.3125, .6875, 0, .5625, .3125, .6875, 1.15]];
    case 'rod': return [[.4375, .5625, 0, 1, .4375, .5625, 1.1]];
    case 'campfire': return [[0, 1, 0, .4375, 0, 1, 1], [.3, .7, .4375, .8, .3, .7, 1, FLAME]];
    case 'detector': return [[0, 1, 0, .375, 0, 1, 1]];
    case 'stand': return [[.4375, .5625, 0, .875, .4375, .5625, 1], [.125, .875, 0, .125, .125, .875, .9]];
    case 'plant': return [[.2, .8, 0, .8, .2, .8, 1, PLANT]];
    case 'low': return [[0, 1, 0, .875, 0, 1, 1]];
    case 'thinplate': return [[0, 1, 0, .125, 0, 1, 1]];
    case 'mob': return [[.26, .74, 0, 1.85, .26, .74, 1]];
    default: return [[0, 1, 0, 1, 0, 1, 1]];
  }
}

export function rgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
const mix = (a, b, t) => [0, 1, 2].map((i) => Math.round(a[i] + (b[i] - a[i]) * t));
const css = (c, f, al = 1) => `rgba(${Math.round(c[0] * f)},${Math.round(c[1] * f)},${Math.round(c[2] * f)},${al})`;

export const VIEWS = ['Südost', 'Nordost', 'Nordwest', 'Südwest'];

// Bereitet ein Modell für schnelles Zeichnen vor.
export function prepare(model, opts = {}) {
  const X = model.size.x, Y = model.size.y, Z = model.size.z;
  const pal = model.palette.map((p) => {
    const [bid, st] = readBlock(p.block);
    return { ...p, shape: shapeOfBlock(bid, p.name), st, rgb: rgb(p.color), context: (p.flags || []).includes('vorhanden') };
  });
  const keyIdx = {}; pal.forEach((p, i) => (keyIdx[p.key] = i));
  const grid = new Int16Array(X * Y * Z).fill(-1);
  const at = (x, y, z) => x + X * (z + Z * y);
  model.layers.forEach((L, y) => L.forEach((row, z) => {
    for (let x = 0; x < row.length; x++) if (row[x] !== '.') grid[at(x, y, z)] = keyIdx[row[x]];
  }));
  // Schnittansicht (z. B. Keller): Decke und vordere Wände ausblenden
  let hidden = null;
  if (opts.schnitt) hidden = (x, y, z, rot) => {
    const p = pal[grid[at(x, y, z)]];
    if (/\(Decke\)/.test(p.name)) return true;
    if (!/\(Wand\)/.test(p.name)) return false;
    const [u, v] = toUV(x, z, rot, X, Z);
    return u === uvMax(rot, X, Z)[0] || v === uvMax(rot, X, Z)[1];
  };
  return { X, Y, Z, pal, grid, at, hidden };
}

function toUV(x, z, rot, X, Z) {
  // inverse der Drehung aus draw(): liefert u, v für Original-x, z
  switch (rot) {
    case 0: return [x, z];
    case 1: return [Z - 1 - z, x];
    case 2: return [X - 1 - x, Z - 1 - z];
    default: return [z, X - 1 - x];
  }
}
function uvMax(rot, X, Z) { return rot % 2 === 0 ? [X - 1, Z - 1] : [Z - 1, X - 1]; }

// Zeichnet das Modell. state(i, x, y, z) liefert pro Block: 0 = ausblenden, 1 = blass, 2 = normal,
// 3 = neu (gelb umrandet), 4 = abbauen (rot umrandet)
export function draw(canvas, P, o) {
  const { X, Y, Z, pal, grid, at } = P;
  const rot = o.rot || 0;
  const U = rot % 2 === 0 ? X : Z, V = rot % 2 === 0 ? Z : X;
  const orig = (u, v) => [[u, v], [v, Z - 1 - u], [X - 1 - u, Z - 1 - v], [X - 1 - v, u]][rot];
  const st = o.state || (() => 2);
  const look = (u, v, y) => {
    if (u < 0 || v < 0 || u >= U || v >= V || y < 0 || y >= Y) return null;
    const [x, z] = orig(u, v);
    const i = grid[at(x, y, z)];
    if (i < 0) return null;
    if (P.hidden && P.hidden(x, y, z, rot)) return null;
    const s = st(i, x, y, z);
    return s ? { i, s } : null;
  };
  // Liste in Zeichenreihenfolge
  const list = [];
  for (let y = 0; y < Y; y++) for (let u = 0; u < U; u++) for (let v = 0; v < V; v++) {
    const b = look(u, v, y); if (b) list.push([u, v, y, b.i, b.s]);
  }
  list.sort((p, q) => (p[0] + p[1] + p[2]) - (q[0] + q[1] + q[2]) || p[2] - q[2]);
  // Größe
  const W = o.width, maxH = o.maxHeight || W;
  const K = 1.15;
  let a, cw, ch, ox, oy;
  const full = Math.max(1, Math.min(W / (U + V + 2), maxH / ((U + V) / 2 + Y * K + 2)));
  if (o.fit && list.length) {
    // Auf die sichtbaren Blöcke zoomen (fester Rahmen W × maxH), höchstens 3-fach
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (const [u, v, y] of list) {
      const sx = u - v, sy = (u + v) / 2;
      x0 = Math.min(x0, sx - 1); x1 = Math.max(x1, sx + 1);
      y0 = Math.min(y0, sy - (y + 1) * K); y1 = Math.max(y1, sy + 1);
    }
    const pt = o.padTop || 0;
    a = Math.max(1, Math.min(W / (x1 - x0 + 2), (maxH - pt) / (y1 - y0 + 2), full * 3));
    cw = Math.floor(W); ch = Math.floor(maxH);
    ox = cw / 2 - ((x0 + x1) / 2) * a; oy = pt + (ch - pt) / 2 - ((y0 + y1) / 2) * a;
  } else {
    a = full;
    cw = Math.ceil((U + V + 2) * a); ch = Math.ceil(((U + V) / 2 + Y * K + 2) * a);
    ox = (V + 1) * a; oy = Y * a * K + a;
  }
  const c = a * K;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = cw * dpr; canvas.height = ch * dpr;
  canvas.style.width = cw + 'px'; canvas.style.height = ch + 'px';
  const g = canvas.getContext('2d');
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, cw, ch);
  const Pt = (u, v, y) => [ox + (u - v) * a, oy + (u + v) * a / 2 - y * c];
  const poly = (pts, fill) => {
    g.beginPath(); g.moveTo(pts[0][0], pts[0][1]);
    for (let k = 1; k < pts.length; k++) g.lineTo(pts[k][0], pts[k][1]);
    g.closePath(); g.fillStyle = fill; g.fill();
  };
  // Boden
  if (o.ground) {
    poly([Pt(0, 0, 0), Pt(U, 0, 0), Pt(U, V, 0), Pt(0, V, 0)], o.ground);
    if (o.gridLine) {
      g.strokeStyle = o.gridLine; g.lineWidth = 1;
      for (let k = 0; k <= Math.max(U, V); k += 5) {
        if (k <= U) { const p1 = Pt(k, 0, 0), p2 = Pt(k, V, 0); g.beginPath(); g.moveTo(...p1); g.lineTo(...p2); g.stroke(); }
        if (k <= V) { const p1 = Pt(0, k, 0), p2 = Pt(U, k, 0); g.beginPath(); g.moveTo(...p1); g.lineTo(...p2); g.stroke(); }
      }
    }
  }
  const bg = o.fadeTo ? rgb(o.fadeTo) : [255, 255, 255];
  const edges = a >= 5;
  const marks = { 3: [], 4: [] };
  const shapeAt = (u, v, y) => { const b = look(u, v, y); return b ? pal[b.i].shape : null; };
  const covers = (n, shp) => n === 'full' || (n === shp && (shp === 'glass' || shp === 'water'));
  for (const [u, v, y, i, s] of list) {
    const p = pal[i], shp = p.shape;
    const stt = rot && p.st.facing ? { ...p.st, facing: turn(p.st.facing, rot) } : p.st;
    let parts = boxes(shp, stt, (du, dv) => shapeAt(u + du, v + dv, y));
    parts = parts.slice().sort((q, r) => (q[0] + q[4] + q[2]) - (r[0] + r[4] + r[2]));
    const al0 = shp === 'glass' ? .42 : shp === 'water' ? .7 : shp === 'pane' && /glass/.test(p.block || p.name) ? .62 : shp === 'pane' && !p.block ? .6 : 1;
    // leichte Farbschwankung pro Block, damit Flächen nicht wie Plastik wirken
    const [ox0, oz0] = orig(u, v);
    const jit = 1 + (((ox0 * 73856093) ^ (y * 19349663) ^ (oz0 * 83492791)) % 9 + 9) % 9 * .011 - .044;
    const fade = s === 1 || p.context;
    let mu0 = 1, mu1 = 0, mv0 = 1, mv1 = 0, my0 = 1, my1 = 0;
    for (const q of parts) {
      const [qu0, qu1, qy0, qy1, qv0, qv1, f0, own] = q;
      let col = own || p.rgb, al = own ? 1 : al0;
      if (fade) { col = mix(col, bg, .62); if (al < 1) al *= .6; }
      const isFullBox = qu0 === 0 && qu1 === 1 && qv0 === 0 && qv1 === 1 && qy0 === 0 && qy1 === 1 && (shp === 'full' || shp === 'glass');
      let top = true, sU = true, sV = true;
      if (isFullBox) { top = !covers(shapeAt(u, v, y + 1), shp); sU = !covers(shapeAt(u + 1, v, y), shp); sV = !covers(shapeAt(u, v + 1, y), shp); }
      if (shp === 'water') { top = !covers(shapeAt(u, v, y + 1), shp); sU = !covers(shapeAt(u + 1, v, y), shp); sV = !covers(shapeAt(u, v + 1, y), shp); }
      const u0 = u + qu0, u1 = u + qu1, v0 = v + qv0, v1 = v + qv1, y0 = y + qy0, y1 = y + qy1, f = f0 * jit;
      if (sV) poly([Pt(u0, v1, y1), Pt(u1, v1, y1), Pt(u1, v1, y0), Pt(u0, v1, y0)], css(col, .66 * f, al));
      if (sU) poly([Pt(u1, v0, y1), Pt(u1, v1, y1), Pt(u1, v1, y0), Pt(u1, v0, y0)], css(col, .82 * f, al));
      if (top) poly([Pt(u0, v0, y1), Pt(u1, v0, y1), Pt(u1, v1, y1), Pt(u0, v1, y1)], css(col, f, al));
      if (edges && isFullBox && shp === 'full' && top && !fade) {
        g.strokeStyle = 'rgba(0,0,0,.14)'; g.lineWidth = .6;
        const t = [Pt(u0, v0, y1), Pt(u1, v0, y1), Pt(u1, v1, y1), Pt(u0, v1, y1)];
        g.beginPath(); g.moveTo(...t[0]); t.slice(1).forEach((r) => g.lineTo(...r)); g.closePath(); g.stroke();
      }
      mu0 = Math.min(mu0, qu0); mu1 = Math.max(mu1, qu1); mv0 = Math.min(mv0, qv0); mv1 = Math.max(mv1, qv1); my0 = Math.min(my0, qy0); my1 = Math.max(my1, qy1);
    }
    if (s === 3 || s === 4) marks[s].push([u + mu0, u + mu1, v + mv0, v + mv1, y + my0, y + Math.min(my1, 1.85)]);
  }
  // Neue Teile (gelb) und Teile zum Abbauen (rot) umranden, über allem, damit man sie immer findet
  for (const [s, color] of [[3, o.highlight], [4, o.highlightWeg || '#d6453d']]) {
    if (!marks[s].length || !color) continue;
    g.strokeStyle = color; g.lineWidth = Math.max(1.2, Math.min(2.4, a / 5)); g.lineJoin = 'round';
    for (const [u0, u1, v0, v1, y0, y1] of marks[s]) {
      const pts = [Pt(u0, v0, y1), Pt(u1, v0, y1), Pt(u1, v0, y0), Pt(u1, v1, y0), Pt(u0, v1, y0), Pt(u0, v1, y1)];
      g.beginPath(); g.moveTo(...pts[0]); pts.slice(1).forEach((q) => g.lineTo(...q)); g.closePath(); g.stroke();
    }
  }
  return { cw, ch };
}

// Kleines Bauteil-Bild für Teilelisten (wie die Teile-Kästen in einem Bauheft)
const iconCache = new Map();
export function partIcon(p, size = 44) {
  const key = p.color + p.shape + (p.block || '') + size;
  if (iconCache.has(key)) return iconCache.get(key);
  const cv = document.createElement('canvas');
  const P = {
    X: 1, Y: 1, Z: 1, pal: [{ ...p, st: p.st || {}, context: false }], grid: new Int16Array([0]), at: () => 0, hidden: null,
  };
  if (p.shape === 'mob') { P.Y = 2; P.grid = new Int16Array([0, -1]); P.at = (x, y) => y; }
  draw(cv, P, { width: size, maxHeight: size });
  const url = cv.toDataURL();
  iconCache.set(key, url);
  return url;
}
