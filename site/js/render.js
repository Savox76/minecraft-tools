// Isometrische Block-Darstellung auf Canvas, ohne Bibliotheken.
// Eigene Farben statt Minecraft-Texturen (Texturen gehören Mojang).

export const shapeOf = (n) =>
  /Dorfbewohner/.test(n) ? 'mob' :
  /Redstonestaub|Seerosenblatt/.test(n) ? 'flat' :
  /Komparator|Verstärker/.test(n) ? 'low' :
  /Karotten|Kartoffeln/.test(n) ? 'crop' :
  /Bett/.test(n) ? 'bed' :
  /Falltür/.test(n) ? 'plate' :
  /zauntor|tür/i.test(n) ? 'panel' :
  /zaun|mauer|eisengitter|blitzableiter|laterne|leiter|fackel|bambus/i.test(n) ? 'thin' :
  /Glasscheibe/.test(n) ? 'pane' :
  /Stufe/.test(n) ? 'slab' :
  /^Glas$/.test(n) ? 'glass' :
  /Wasser|Meer/.test(n) ? 'water' : 'full';

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
  const pal = model.palette.map((p) => ({
    ...p, shape: shapeOf(p.name), rgb: rgb(p.color),
    context: (p.flags || []).includes('vorhanden'),
  }));
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

// Zeichnet das Modell. state(i, x, y, z) liefert pro Block: 0 = ausblenden, 1 = blass, 2 = normal, 3 = neu (hervorgehoben)
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
  const highlights = [];
  for (const [u, v, y, i, s] of list) {
    const p = pal[i], shp = p.shape;
    let u0 = u, u1 = u + 1, v0 = v, v1 = v + 1, y0 = y, y1 = y + 1, al = 1;
    if (shp === 'thin') { u0 += .32; u1 -= .32; v0 += .32; v1 -= .32; }
    if (shp === 'slab') y1 = y + .5;
    if (shp === 'bed') y1 = y + .56;
    if (shp === 'flat') y1 = y + .07;
    if (shp === 'low') y1 = y + .14;
    if (shp === 'crop') { y1 = y + .45; u0 += .12; u1 -= .12; v0 += .12; v1 -= .12; }
    if (shp === 'mob') { y1 = y + 1.85; u0 += .26; u1 -= .26; v0 += .26; v1 -= .26; }
    if (shp === 'glass') al = .42;
    if (shp === 'water') { al = .7; y1 = y + .88; }
    if (shp === 'pane' || shp === 'panel') {
      const wall = (b) => b && pal[b.i].shape !== 'water';
      const au = wall(look(u - 1, v, y)) || wall(look(u + 1, v, y));
      const av = wall(look(u, v - 1, y)) || wall(look(u, v + 1, y));
      const t = shp === 'pane' ? .44 : .4;
      if (au && !av) { v0 += t; v1 -= t; } else if (av && !au) { u0 += t; u1 -= t; } else { u0 += t; u1 -= t; v0 += t; v1 -= t; }
      if (shp === 'pane') al = .6;
    }
    if (shp === 'plate') {
      const full = (b) => b && pal[b.i].shape === 'full';
      if (full(look(u - 1, v, y))) u1 = u + .18; else if (full(look(u + 1, v, y))) u0 = u + .82;
      else if (full(look(u, v - 1, y))) v1 = v + .18; else if (full(look(u, v + 1, y))) v0 = v + .82;
      else { u0 += .4; u1 -= .4; v0 += .4; v1 -= .4; }
    }
    const isFull = shp === 'full' || shp === 'glass' || shp === 'water';
    const hides = (b) => b && (pal[b.i].shape === 'full' || (pal[b.i].shape === shp && (shp === 'glass' || shp === 'water')));
    const top = !(isFull && shp !== 'water' && hides(look(u, v, y + 1)));
    const sU = !(isFull && hides(look(u + 1, v, y)));
    const sV = !(isFull && hides(look(u, v + 1, y)));
    let col = p.rgb;
    if (s === 1 || p.context) { col = mix(col, bg, .62); if (al < 1) al *= .6; }
    if (sV) poly([Pt(u0, v1, y1), Pt(u1, v1, y1), Pt(u1, v1, y0), Pt(u0, v1, y0)], css(col, .64, al));
    if (sU) poly([Pt(u1, v0, y1), Pt(u1, v1, y1), Pt(u1, v1, y0), Pt(u1, v0, y0)], css(col, .8, al));
    if (top) poly([Pt(u0, v0, y1), Pt(u1, v0, y1), Pt(u1, v1, y1), Pt(u0, v1, y1)], css(col, 1, al));
    if (edges && shp === 'full' && top && s !== 1) {
      g.strokeStyle = 'rgba(0,0,0,.14)'; g.lineWidth = .6;
      const t = [Pt(u0, v0, y1), Pt(u1, v0, y1), Pt(u1, v1, y1), Pt(u0, v1, y1)];
      g.beginPath(); g.moveTo(...t[0]); t.slice(1).forEach((q) => g.lineTo(...q)); g.closePath(); g.stroke();
    }
    if (s === 3) highlights.push([u0, u1, v0, v1, y0, y1]);
  }
  // Neue Teile umranden (über allem, damit man sie immer findet)
  if (highlights.length && o.highlight) {
    g.strokeStyle = o.highlight; g.lineWidth = Math.max(1.2, Math.min(2.4, a / 5)); g.lineJoin = 'round';
    for (const [u0, u1, v0, v1, y0, y1] of highlights) {
      const pts = [Pt(u0, v0, y1), Pt(u1, v0, y1), Pt(u1, v0, y0), Pt(u1, v1, y0), Pt(u0, v1, y0), Pt(u0, v1, y1)];
      g.beginPath(); g.moveTo(...pts[0]); pts.slice(1).forEach((q) => g.lineTo(...q)); g.closePath(); g.stroke();
    }
  }
  return { cw, ch };
}

// Kleines Bauteil-Bild für Teilelisten (wie die Teile-Kästen in einem Bauheft)
const iconCache = new Map();
export function partIcon(p, size = 44) {
  const key = p.color + p.shape + size;
  if (iconCache.has(key)) return iconCache.get(key);
  const cv = document.createElement('canvas');
  const P = {
    X: 1, Y: 1, Z: 1, pal: [{ ...p, context: false }], grid: new Int16Array([0]), at: () => 0, hidden: null,
  };
  if (p.shape === 'mob') { P.Y = 2; P.grid = new Int16Array([0, -1]); P.at = (x, y) => y; }
  draw(cv, P, { width: size, maxHeight: size });
  const url = cv.toDataURL();
  iconCache.set(key, url);
  return url;
}
