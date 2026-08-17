'use strict';
/* eslint-env browser */

/* ==========================================================================
   MAHORAGA — ADAPTIVE CHESS AGENT (FRONTEND ENGINE)
   ========================================================================== */

/* ================= PIECE VECTOR ARTWORK ================= */
const PIECE_ART = {
  K: '<g fill="none" fill-rule="evenodd" stroke="#000" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><path stroke-linejoin="miter" d="M22.5 11.63V6M20 8h5"/><path fill="#fff" stroke-linecap="butt" stroke-linejoin="miter" d="M22.5 25s4.5-7.5 3-10.5c0 0-1-2.5-3-2.5s-3 2.5-3 2.5c-1.5 3 3 10.5 3 10.5"/><path fill="#fff" d="M12.5 37c5.5 3.5 14.5 3.5 20 0v-7s9-4.5 6-10.5c-4-6.5-13.5-3.5-16 4V27v-3.5c-2.5-7.5-12-10.5-16-4-3 6 6 10.5 6 10.5v7"/><path d="M12.5 30c5.5-3 14.5-3 20 0m-20 3.5c5.5-3 14.5-3 20 0m-20 3.5c5.5-3 14.5-3 20 0"/></g>',
  Q: '<g style="fill:#ffffff;stroke:#000000;stroke-width:1.5;stroke-linejoin:round"><path d="M 9,26 C 17.5,24.5 30,24.5 36,26 L 38.5,13.5 L 31,25 L 30.7,10.9 L 25.5,24.5 L 22.5,10 L 19.5,24.5 L 14.3,10.9 L 14,25 L 6.5,13.5 L 9,26 z"/><path d="M 9,26 C 9,28 10.5,28 11.5,30 C 12.5,31.5 12.5,31 12,33.5 C 10.5,34.5 11,36 11,36 C 9.5,37.5 11,38.5 11,38.5 C 17.5,39.5 27.5,39.5 34,38.5 C 34,38.5 35.5,37.5 34,36 C 34,36 34.5,34.5 33,33.5 C 32.5,31 32.5,31.5 33.5,30 C 34.5,28 36,28 36,26 C 27.5,24.5 17.5,24.5 9,26 z"/><path d="M 11.5,30 C 15,29 30,29 33.5,30" style="fill:none"/><path d="M 12,33.5 C 18,32.5 27,32.5 33,33.5" style="fill:none"/><circle cx="6" cy="12" r="2"/><circle cx="14" cy="9" r="2"/><circle cx="22.5" cy="8" r="2"/><circle cx="31" cy="9" r="2"/><circle cx="39" cy="12" r="2"/></g>',
  R: '<g style="opacity:1; fill:#ffffff; fill-opacity:1; fill-rule:evenodd; stroke:#000000; stroke-width:1.5; stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4; stroke-dasharray:none; stroke-opacity:1;" transform="translate(0,0.3)"><path d="M 9,39 L 36,39 L 36,36 L 9,36 L 9,39 z " style="stroke-linecap:butt;"/><path d="M 12,36 L 12,32 L 33,32 L 33,36 L 12,36 z " style="stroke-linecap:butt;"/><path d="M 11,14 L 11,9 L 15,9 L 15,11 L 20,11 L 20,9 L 25,9 L 25,11 L 30,11 L 30,9 L 34,9 L 34,14" style="stroke-linecap:butt;"/><path d="M 34,14 L 31,17 L 14,17 L 11,14"/><path d="M 31,17 L 31,29.5 L 14,29.5 L 14,17" style="stroke-linecap:butt; stroke-linejoin:miter;"/><path d="M 31,29.5 L 32.5,32 L 12.5,32 L 14,29.5"/><path d="M 11,14 L 34,14" style="fill:none; stroke:#000000; stroke-linejoin:miter;"/></g>',
  B: '<g style="opacity:1; fill:none; fill-rule:evenodd; fill-opacity:1; stroke:#000000; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round; stroke-miterlimit:4; stroke-dasharray:none; stroke-opacity:1;" transform="translate(0,0.6)"><g style="fill:#ffffff; stroke:#000000; stroke-linecap:butt;"><path d="M 9,36 C 12.39,35.03 19.11,36.43 22.5,34 C 25.89,36.43 32.61,35.03 36,36 C 36,36 37.65,36.54 39,38 C 38.32,38.97 37.35,38.99 36,38.5 C 32.61,37.53 25.89,38.96 22.5,37.5 C 19.11,38.96 12.39,37.53 9,38.5 C 7.65,38.99 6.68,38.97 6,38 C 7.35,36.54 9,36 9,36 z"/><path d="M 15,32 C 17.5,34.5 27.5,34.5 30,32 C 30.5,30.5 30,30 30,30 C 30,27.5 27.5,26 27.5,26 C 33,24.5 33.5,14.5 22.5,10.5 C 11.5,14.5 12,24.5 17.5,26 C 17.5,26 15,27.5 15,30 C 15,30 14.5,30.5 15,32 z"/><path d="M 25 8 A 2.5 2.5 0 1 1  20,8 A 2.5 2.5 0 1 1  25 8 z"/></g><path d="M 17.5,26 L 27.5,26 M 15,30 L 30,30 M 22.5,15.5 L 22.5,20.5 M 20,18 L 25,18" style="fill:none; stroke:#000000; stroke-linejoin:miter;"/></g>',
  N: '<g style="opacity:1; fill:none; fill-opacity:1; fill-rule:evenodd; stroke:#000000; stroke-width:1.5; stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4; stroke-dasharray:none; stroke-opacity:1;" transform="translate(0,0.3)"><path d="M 22,10 C 32.5,11 38.5,18 38,39 L 15,39 C 15,30 25,32.5 23,18" style="fill:#ffffff; stroke:#000000;"/><path d="M 24,18 C 24.38,20.91 18.45,25.37 16,27 C 13,29 13.18,31.34 11,31 C 9.958,30.06 12.41,27.96 11,28 C 10,28 11.19,29.23 10,30 C 9,30 5.997,31 6,26 C 6,24 12,14 12,14 C 12,14 13.89,12.1 14,10.5 C 13.27,9.506 13.5,8.5 13.5,7.5 C 14.5,6.5 16.5,10 16.5,10 L 18.5,10 C 18.5,10 19.28,8.008 21,7 C 22,7 22,10 22,10" style="fill:#ffffff; stroke:#000000;"/><path d="M 9.5 25.5 A 0.5 0.5 0 1 1 8.5,25.5 A 0.5 0.5 0 1 1 9.5 25.5 z" style="fill:#000000; stroke:#000000;"/><path d="M 15 15.5 A 0.5 1.5 0 1 1  14,15.5 A 0.5 1.5 0 1 1  15 15.5 z" transform="matrix(0.866,0.5,-0.5,0.866,9.693,-5.173)" style="fill:#000000; stroke:#000000;"/></g>',
  P: '<path d="m 22.5,9 c -2.21,0 -4,1.79 -4,4 0,0.89 0.29,1.71 0.78,2.38 C 17.33,16.5 16,18.59 16,21 c 0,2.03 0.94,3.84 2.41,5.03 C 15.41,27.09 11,31.58 11,39.5 H 34 C 34,31.58 29.59,27.09 26.59,26.03 28.06,24.84 29,23.03 29,21 29,18.59 27.67,16.5 25.72,15.38 26.21,14.71 26.5,13.89 26.5,13 c 0,-2.21 -1.79,-4 -4,-4 z" style="opacity:1; fill:#ffffff; fill-opacity:1; fill-rule:nonzero; stroke:#000000; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:miter; stroke-miterlimit:4; stroke-dasharray:none; stroke-opacity:1;"/>'
};

const BLACK_ART = {};
for (const key of Object.keys(PIECE_ART)) {
  BLACK_ART[key] = PIECE_ART[key]
    .replace(/#ffffff/gi, '#141414')
    .replace(/#fff/gi, '#141414')
    .replace(/fill:#fff/gi, 'fill:#141414')
    .replace(/stroke:#000000/gi, 'stroke:#ffffff')
    .replace(/stroke="#000"/gi, 'stroke="#ffffff"');
}

const PIECE_VALUES = { P: 1, N: 3, B: 3, R: 5, Q: 9, K: 0 };
const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

/* ================= STATE ================= */
const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

let playerId = null;
try { playerId = localStorage.getItem('mahoragaPlayerId') || null; } catch (err) {}

let soundEnabled = true;
try {
  const savedSound = localStorage.getItem('mahoragaSound');
  if (savedSound !== null) soundEnabled = savedSound === 'true';
} catch (err) {}

let showCoords = true;

let gameId = null;
let moves = [];
let result = '*';
let humanColor = 'white';
let bottom = 'w';
let fen = START_FEN;
let liveFen = START_FEN;
let viewIndex = 0;
let busy = false;
let selected = null;
let selectedPiece = null;
let legalTargets = {};
let suppressClick = false;
let drag = null;
let wheelRotation = 0;
let currentSkillLevel = null;
let currentGameMahoragaElo = null;

/* ================= WEB AUDIO SYNTHESIZER ================= */
let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (AudioCtx) audioCtx = new AudioCtx();
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

function playSfx(type) {
  if (!soundEnabled) return;
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const t = ctx.currentTime;

    if (type === 'move') {
      // Crisp mechanical snap
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(220, t);
      osc.frequency.exponentialRampToValueAtTime(70, t + 0.06);
      gain.gain.setValueAtTime(0.3, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.06);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t);
      osc.stop(t + 0.06);
    } else if (type === 'capture') {
      // Deeper thud with noise
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(140, t);
      osc.frequency.exponentialRampToValueAtTime(40, t + 0.12);
      gain.gain.setValueAtTime(0.5, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t);
      osc.stop(t + 0.12);
    } else if (type === 'check') {
      // Resonant warning chime
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();
      osc1.type = 'sine';
      osc2.type = 'triangle';
      osc1.frequency.setValueAtTime(587.33, t); // D5
      osc2.frequency.setValueAtTime(880, t);    // A5
      gain.gain.setValueAtTime(0.35, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.35);
      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(ctx.destination);
      osc1.start(t);
      osc2.start(t);
      osc1.stop(t + 0.35);
      osc2.stop(t + 0.35);
    } else if (type === 'mate') {
      // Low domain expansion drone + harmonic chords
      [110, 164.81, 220, 329.63].forEach((f, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(f, t + idx * 0.08);
        gain.gain.setValueAtTime(0.2, t + idx * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 1.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t + idx * 0.08);
        osc.stop(t + 1.2);
      });
    } else if (type === 'wheel') {
      // Ratchet click
      for (let i = 0; i < 3; i++) {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(600 + i * 150, t + i * 0.04);
        gain.gain.setValueAtTime(0.15, t + i * 0.04);
        gain.gain.exponentialRampToValueAtTime(0.001, t + i * 0.04 + 0.02);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t + i * 0.04);
        osc.stop(t + i * 0.04 + 0.02);
      }
    } else if (type === 'click') {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(800, t);
      gain.gain.setValueAtTime(0.1, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.02);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t);
      osc.stop(t + 0.02);
    }
  } catch (err) {
    console.warn('Audio playback error:', err);
  }
}

/* ================= TOAST NOTIFICATIONS ================= */
function showToast(message, duration = 3000) {
  const container = $('#toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'hud-toast';
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-6px)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 260);
  }, duration);
}

/* ================= CHESS BOARD MODEL HELPERS ================= */
function parseFen(value) {
  const rows = value.split(' ')[0].split('/');
  return rows.map(row => {
    const a = [];
    for (const ch of row) {
      if (+ch) { for (let i = 0; i < +ch; i++) a.push(''); }
      else a.push(ch);
    }
    return a;
  });
}

function parseFenFlat(value) {
  const flat = [];
  for (const row of value.split(' ')[0].split('/')) {
    for (const ch of row) {
      if (+ch) { for (let i = 0; i < +ch; i++) flat.push(''); }
      else flat.push(ch);
    }
  }
  return flat;
}

function fenTurn(value) { return value.split(' ')[1]; }
function squareName(r, c) { return 'abcdefgh'[c] + (8 - r); }
function indexFor(s) { const file = s.charCodeAt(0) - 97, rank = Number(s[1]); return (8 - rank) * 8 + file; }

function visualMove(position, uci) {
  const parts = position.split(' '), flat = parseFenFlat(position);
  const from = indexFor(uci.slice(0, 2)), to = indexFor(uci.slice(2, 4));
  const piece = flat[from];
  const enPassant = (piece === 'P' || piece === 'p') && uci[0] !== uci[2] && !flat[to] && uci.length === 4;

  flat[to] = uci[4] ? (piece === piece.toUpperCase() ? uci[4].toUpperCase() : uci[4].toLowerCase()) : piece;
  flat[from] = '';

  if (enPassant) flat[indexFor(uci[2] + uci[1])] = '';
  if (piece === 'K' && uci === 'e1g1') { flat[indexFor('f1')] = flat[indexFor('h1')]; flat[indexFor('h1')] = ''; }
  if (piece === 'K' && uci === 'e1c1') { flat[indexFor('d1')] = flat[indexFor('a1')]; flat[indexFor('a1')] = ''; }
  if (piece === 'k' && uci === 'e8g8') { flat[indexFor('f8')] = flat[indexFor('h8')]; flat[indexFor('h8')] = ''; }
  if (piece === 'k' && uci === 'e8c8') { flat[indexFor('d8')] = flat[indexFor('a8')]; flat[indexFor('a8')] = ''; }

  let placement = '';
  for (let r = 0; r < 8; r++) {
    let empty = 0;
    for (let c = 0; c < 8; c++) {
      const p = flat[r * 8 + c];
      if (p) {
        if (empty) { placement += empty; empty = 0; }
        placement += p;
      } else empty++;
    }
    if (empty) placement += empty;
    if (r < 7) placement += '/';
  }
  parts[0] = placement;
  parts[1] = parts[1] === 'w' ? 'b' : 'w';
  return parts.join(' ');
}

function isSquareAttacked(board, r, c, byColor) {
  for (let rr = 0; rr < 8; rr++) {
    for (let cc = 0; cc < 8; cc++) {
      const p = board[rr][cc];
      if (!p) continue;
      const pc = p.toUpperCase(), isWhite = p === p.toUpperCase();
      if ((isWhite ? 1 : 0) !== (byColor === 'w' ? 1 : 0)) continue;
      if (pc === 'P') {
        const dir = isWhite ? 1 : -1;
        if (r === rr + dir && (c === cc + 1 || c === cc - 1)) return true;
        continue;
      }
      if (pc === 'N') {
        if ((Math.abs(r - rr) === 2 && Math.abs(c - cc) === 1) || (Math.abs(r - rr) === 1 && Math.abs(c - cc) === 2)) return true;
        continue;
      }
      if (pc === 'K') {
        if (Math.abs(r - rr) <= 1 && Math.abs(c - cc) <= 1) return true;
        continue;
      }
      const dr = Math.sign(r - rr), dc = Math.sign(c - cc);
      if (dr === 0 && dc === 0) continue;
      if (pc === 'B' && (dr === 0 || dc === 0)) continue;
      if (pc === 'R' && (dr !== 0 && dc !== 0)) continue;
      let cr = rr + dr, cc2 = cc + dc;
      while (cr >= 0 && cr < 8 && cc2 >= 0 && cc2 < 8) {
        if (cr === r && cc2 === c) return true;
        if (board[cr][cc2]) break;
        cr += dr; cc2 += dc;
      }
    }
  }
  return false;
}

function checkInfo() {
  const board = parseFen(fen), turn = fenTurn(fen);
  const opp = turn === 'w' ? 'b' : 'w', target = turn === 'w' ? 'K' : 'k';
  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      if (board[r][c] === target && isSquareAttacked(board, r, c, opp)) {
        return { check: true, king: [r, c], kingSquare: squareName(r, c) };
      }
    }
  }
  return { check: false };
}

function pieceClasses(piece) {
  if (!piece) return '';
  const up = piece.toUpperCase();
  if (!PIECE_ART[up]) return '';
  const isWhite = piece === up;
  const art = isWhite ? PIECE_ART[up] : BLACK_ART[up];
  return `<svg viewBox="0 0 45 45" class="piece-svg ${isWhite ? 'white-piece' : 'black-piece'}">${art}</svg>`;
}

function boardFen(ply) {
  return moves.slice(0, ply).reduce((f, uci) => visualMove(f, uci), START_FEN);
}

function gameOver() { return result !== '*' && result !== ''; }
function myTurn() { return humanColor === 'white' ? 'w' : 'b'; }
function humanToMove() { return fenTurn(fen) === myTurn() && !gameOver(); }
function isLive() { return viewIndex === moves.length; }
function clearLegal() { legalTargets = {}; }
function pieceAt(name) { return parseFen(fen)[indexFor(name) >> 3][indexFor(name) & 7]; }

/* ================= CAPTURED PIECES TRACKER ================= */
function updateCapturedPieces() {
  const initialCounts = { P: 8, N: 2, B: 2, R: 2, Q: 1, p: 8, n: 2, b: 2, r: 2, q: 1 };
  const currentFlat = parseFenFlat(fen);

  const currentCounts = { P: 0, N: 0, B: 0, R: 0, Q: 0, p: 0, n: 0, b: 0, r: 0, q: 0 };
  currentFlat.forEach(p => { if (p && currentCounts[p] !== undefined) currentCounts[p]++; });

  const capturedWhite = []; // Black captured these white pieces
  const capturedBlack = []; // White captured these black pieces

  let whiteScore = 0;
  let blackScore = 0;

  ['Q', 'R', 'B', 'N', 'P'].forEach(p => {
    const lost = initialCounts[p] - currentCounts[p];
    for (let i = 0; i < lost; i++) capturedWhite.push(p);
  });

  ['q', 'r', 'b', 'n', 'p'].forEach(p => {
    const lost = initialCounts[p] - currentCounts[p];
    for (let i = 0; i < lost; i++) capturedBlack.push(p.toUpperCase());
  });

  currentFlat.forEach(p => {
    if (!p) return;
    const up = p.toUpperCase();
    const val = PIECE_VALUES[up] || 0;
    if (p === up) whiteScore += val;
    else blackScore += val;
  });

  const humanIsWhite = humanColor === 'white';
  const humanCaptured = humanIsWhite ? capturedBlack : capturedWhite;
  const opponentCaptured = humanIsWhite ? capturedWhite : capturedBlack;

  const humanDiff = humanIsWhite ? (whiteScore - blackScore) : (blackScore - whiteScore);
  const opponentDiff = -humanDiff;

  const renderCapList = (pieces, diff, containerId) => {
    const el = $(containerId);
    if (!el) return;
    let html = '';
    pieces.forEach(p => {
      const art = p === p.toUpperCase() ? PIECE_ART[p] : BLACK_ART[p.toUpperCase()];
      html += `<svg viewBox="0 0 45 45" class="captured-piece-mini">${art}</svg>`;
    });
    if (diff > 0) {
      html += `<span class="captured-diff">+${diff}</span>`;
    }
    el.innerHTML = html;
  };

  renderCapList(opponentCaptured, opponentDiff, '#opponent-captured');
  renderCapList(humanCaptured, humanDiff, '#human-captured');
}

/* ================= BOARD RENDERING ================= */
function render() {
  const board = parseFen(fen);
  const grid = $('#board');
  if (!grid) return;

  const ck = gameOver() ? null : checkInfo();
  const ckSquare = ck && ck.check ? ck.king : null;

  grid.innerHTML = '';
  for (let d = 0; d < 64; d++) {
    const dr = Math.floor(d / 8), dc = d % 8;
    const r = bottom === 'w' ? dr : 7 - dr;
    const name = squareName(r, dc), piece = board[r][dc];

    const el = document.createElement('button');
    el.classList.add('square', (r + dc) % 2 ? 'dark' : 'light');
    el.dataset.square = name;

    let inner = '';
    if (showCoords) {
      if (dc === 0) inner += `<span class="coord rank">${8 - r}</span>`;
      if (dr === 7) inner += `<span class="coord file">${'abcdefgh'[dc]}</span>`;
    }
    inner += pieceClasses(piece);
    el.innerHTML = inner;

    if (selected === name) el.classList.add('selected');
    if (legalTargets[name] !== undefined) el.classList.add(legalTargets[name] ? 'legal-capture' : 'legal');
    if (ckSquare && ckSquare[0] === r && ckSquare[1] === dc) el.classList.add('check');

    const isHumanPiece = piece && piece.length === 1 && (piece === piece.toUpperCase()) === (humanColor === 'white');
    const interactive = humanToMove() && isLive() && !busy && isHumanPiece;

    el.draggable = false;
    el.onclick = () => clickSquare(name, piece);
    if (interactive) {
      el.addEventListener('pointerdown', ev => pointerDown(ev, name), { passive: false });
    }
    grid.append(el);
  }

  const last = viewIndex > 0 ? moves[viewIndex - 1] : null;
  if (last) {
    const from = document.querySelector(`[data-square="${last.slice(0, 2)}"]`);
    const to = document.querySelector(`[data-square="${last.slice(2, 4)}"]`);
    if (from) from.classList.add('last-move');
    if (to) to.classList.add('last-move');
  }

  // Update Turn Indicators
  const currentTurn = fenTurn(fen);
  const isHumanTurn = currentTurn === myTurn();
  const humanTurnDot = $('#human-turn-dot');
  const oppTurnDot = $('#opponent-turn-dot');
  const humanStatusInd = $('#human-status-indicator');
  const oppStatusInd = $('#opponent-status-indicator');

  if (humanTurnDot) humanTurnDot.classList.toggle('active', isHumanTurn && !gameOver());
  if (oppTurnDot) oppTurnDot.classList.toggle('active', !isHumanTurn && !gameOver());

  if (humanStatusInd) humanStatusInd.textContent = isHumanTurn && !gameOver() ? 'YOUR TURN' : '';
  if (oppStatusInd) oppStatusInd.textContent = !isHumanTurn && !gameOver() ? 'ANALYZING...' : '';

  updateCapturedPieces();
}

/* ================= POINTER DRAG & DROP ================= */
function pointerDown(ev, name) {
  if (!((ev.buttons !== undefined ? ev.buttons : 1) & 1) && ev.pointerType === 'mouse') return;
  const piece = pieceAt(name);
  if (!piece || piece.length !== 1) return;
  if (typeof ev.pointerId !== 'undefined' && ev.target.setPointerCapture) {
    try { ev.target.setPointerCapture(ev.pointerId); } catch (e) {}
  }
  drag = { x: ev.clientX, y: ev.clientY, moved: false, from: name, piece, ghost: null };
  ev.target.addEventListener('pointermove', onPointerMove, { passive: false });
  ev.target.addEventListener('pointerup', onPointerUp, { once: true });
}

function onPointerMove(ev) {
  if (!drag) return;
  ev.preventDefault();
  const dx = ev.clientX - drag.x, dy = ev.clientY - drag.y;
  if (!drag.moved && Math.hypot(dx, dy) > 6) {
    drag.moved = true;
    const boardEl = $('#board');
    const size = boardEl ? boardEl.getBoundingClientRect() : { width: 48, height: 48 };
    drag.ghost = document.createElement('div');
    drag.ghost.className = 'move-ghost';
    drag.ghost.style.width = (size.width / 8) + 'px';
    drag.ghost.style.height = (size.height / 8) + 'px';
    drag.ghost.innerHTML = pieceClasses(drag.piece);
    document.body.appendChild(drag.ghost);
  }
  if (drag.moved && drag.ghost) {
    drag.ghost.style.left = (ev.clientX) + 'px';
    drag.ghost.style.top = (ev.clientY) + 'px';
  }
}

async function onPointerUp(ev) {
  if (!drag) return;
  const g = drag.ghost;
  if (g) try { g.remove(); } catch (err) {}
  if (drag.moved) {
    suppressClick = true;
    const hit = document.elementFromPoint(ev.clientX, ev.clientY);
    const sq = hit && hit.closest('.square');
    const target = sq && sq.dataset.square;
    const from = drag.from, piece = drag.piece;
    drag = null;
    try {
      const map = await legalMovesFor(from);
      if (target && target !== from && map[target] !== undefined) {
        clearLegal(); selected = null; selectedPiece = null;
        playMove(from + target + (piece === 'P' && target[1] === (piece === piece.toUpperCase() ? '8' : '1') ? 'q' : ''));
      } else {
        clearLegal(); selected = null; selectedPiece = null; render();
      }
    } catch (err) {
      clearLegal(); selected = null; selectedPiece = null; render();
      console.warn(err);
    }
  } else {
    drag = null;
  }
}

function submitMove(selectedName, targetName, piece) {
  let uci = selectedName + targetName;
  const isWhite = piece === piece.toUpperCase();
  if (piece === 'P' && ((isWhite && targetName[1] === '8') || (!isWhite && targetName[1] === '1'))) uci += 'q';
  clearLegal(); selected = null; selectedPiece = null;
  playMove(uci);
}

/* ================= CLICK SELECT ================= */
async function clickSquare(name, piece) {
  if (suppressClick) { suppressClick = false; return; }
  if (busy) return;
  if (!gameId) { showToast('Summon a new battle from the menu to start.'); return; }
  if (gameOver()) { showToast('Battle ended — summon a new one.'); return; }
  if (!isLive()) { showToast('Viewing past move — click LIVE to resume.'); return; }
  if (fenTurn(fen) !== myTurn()) { showToast('Mahoraga is analyzing...'); return; }

  if (selected) {
    if (selected === name) { clearLegal(); selected = null; selectedPiece = null; render(); return; }
    if (legalTargets[name] !== undefined) { submitMove(selected, name, selectedPiece); return; }
    if (piece && piece.length === 1 && (piece === piece.toUpperCase()) === (humanColor === 'white')) {
      selectPiece(name, piece); return;
    }
    return;
  }
  if (piece && piece.length === 1 && (piece === piece.toUpperCase()) === (humanColor === 'white')) {
    selectPiece(name, piece);
  }
}

async function legalMovesFor(from) {
  const data = await api(`/games/${gameId}/legal-moves`);
  const map = {};
  for (const m of data.moves) if (m.uci.startsWith(from)) map[m.to] = !!m.capture;
  return map;
}

async function selectPiece(name, piece) {
  selected = name; selectedPiece = piece; clearLegal(); render();
  playSfx('click');
  try {
    legalTargets = await legalMovesFor(selected); render();
  } catch (err) {
    clearLegal(); render();
    console.warn(err);
  }
}

async function animateMove(uci) {
  const from = $(`.square[data-square="${uci.slice(0, 2)}"]`);
  const to = $(`.square[data-square="${uci.slice(2, 4)}"]`);
  const piece = from && from.querySelector('.piece-svg');
  if (!from || !to || !piece || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const a = from.getBoundingClientRect(), b = to.getBoundingClientRect();
  const ghost = document.createElement('div');
  ghost.className = 'moving-piece';
  ghost.style.width = a.width + 'px'; ghost.style.height = a.height + 'px';
  ghost.style.left = a.left + 'px'; ghost.style.top = a.top + 'px';
  ghost.appendChild(piece.cloneNode(true));
  document.body.appendChild(ghost);
  piece.style.visibility = 'hidden';
  try {
    await Promise.race([
      ghost.animate([
        { transform: 'translate(0,0) scale(1)' },
        { transform: `translate(${b.left - a.left}px,${b.top - a.top}px) scale(1.05)` }
      ], { duration: 250, easing: 'cubic-bezier(.2,.8,.25,1)' }).finished.catch(() => {}),
      new Promise(resolve => setTimeout(resolve, 600))
    ]);
  } finally {
    ghost.remove();
    piece.style.visibility = 'visible';
  }
}

/* ================= MAKE A MOVE ================= */
async function playMove(uci) {
  if (busy) return;
  const prevFen = fen, midFen = visualMove(prevFen, uci);
  const fromName = uci.slice(0, 2), toName = uci.slice(2, 4);
  const isCapture = !!pieceAt(toName);

  selected = null; selectedPiece = null; clearLegal();
  busy = true;

  try {
    await animateMove(uci);
    playSfx(isCapture ? 'capture' : 'move');
    fen = midFen; render();

    const data = await api(`/games/${gameId}/move`, { method: 'POST', body: JSON.stringify({ move: uci }) });

    if (data.mahoraga_move) {
      const mahoTo = data.mahoraga_move.slice(2, 4);
      const mahoCapture = !!parseFen(fen)[indexFor(mahoTo) >> 3][indexFor(mahoTo) & 7];
      await animateMove(data.mahoraga_move);
      playSfx(mahoCapture ? 'capture' : 'move');
    }

    liveFen = data.fen;
    moves = data.moves;
    result = data.result;
    viewIndex = data.moves.length;
    fen = liveFen;

    render();
    renderMoves();

    if (result !== '*') {
      playSfx('mate');
      showMate(result);
    } else {
      const ck = checkInfo();
      if (ck.check) {
        playSfx('check');
        showToast('CHECK — SOUL THREATENED', 2500);
      }
    }

    if (data.mahoraga_elo !== undefined && data.mahoraga_elo !== null) {
      currentGameMahoragaElo = data.mahoraga_elo;
    }

    if (data.message && /learned/i.test(data.message)) {
      playSfx('wheel');
      showToast(data.message.toUpperCase(), 4000);
    }

    refreshProfile();
  } catch (e) {
    fen = prevFen; render();
    flashInvalid(fromName, toName);
    showToast(e.message || 'Illegal move.');
  } finally {
    busy = false;
  }
}

function flashInvalid(from, to) {
  [from, to].forEach(n => {
    const el = $(`.square[data-square="${n}"]`);
    if (el) el.classList.add('invalid');
  });
  setTimeout(render, 500);
}

function showMate(res) {
  const isDraw = res === '1/2-1/2';
  const won = res === '1-0' ? (humanColor === 'white') : (res === '0-1');
  let title = 'CHECKMATE';
  let sub = won ? 'You defeated the Shikigami.' : 'Mahoraga adapted and prevailed.';

  if (isDraw) {
    title = 'RITUAL DRAW';
    sub = 'The battle concluded with neither side fallen.';
  }

  $('#mate-title').textContent = title;
  $('#mate-sub').textContent = sub;
  $('#mate-stats').textContent = `Total Plies: ${moves.length} | Outcome: ${res}`;
  $('#mate-overlay').hidden = false;
}

/* ================= GAME LIFECYCLE ================= */
function setSide(side) {
  if (busy || (gameId && !gameOver())) return;
  humanColor = side;
  bottom = side === 'white' ? 'w' : 'b';
  $$('.side-choice-btn').forEach(b => b.classList.toggle('active', b.dataset.side === side));
  const tag = $('#human-color-tag');
  if (tag) tag.textContent = side.toUpperCase();
  render();
}

async function ensurePlayer() {
  if (playerId) return;
  const data = await api('/players', { method: 'POST', body: JSON.stringify({ estimated_strength: 200 }) });
  playerId = data.player_id;
  try { localStorage.setItem('mahoragaPlayerId', playerId); } catch (err) {}
}

function clearPlayer() {
  playerId = null;
  try { localStorage.removeItem('mahoragaPlayerId'); } catch (err) {}
}

async function startBattle() {
  const skillVal = currentSkillLevel ? Number(currentSkillLevel) : null;
  return api('/games', {
    method: 'POST',
    body: JSON.stringify({
      player_id: playerId,
      skill_level: skillVal,
      human_color: humanColor
    })
  });
}

async function newGame() {
  if (busy) return;
  closeDrawer();
  try {
    busy = true;
    showToast('COMMENCING SUMMON RITUAL...', 2000);
    playSfx('wheel');

    let data;
    try {
      await ensurePlayer();
      data = await startBattle();
    } catch (e) {
      if (!/player not found/i.test(e.message)) throw e;
      clearPlayer();
      await ensurePlayer();
      data = await startBattle();
    }

    gameId = data.game_id;
    moves = data.moves;
    result = '*';
    liveFen = data.fen;
    viewIndex = data.moves.length;
    selected = null;
    selectedPiece = null;
    clearLegal();
    $('#mate-overlay').hidden = true;

    const first = data.mahoraga_move, wasBlack = humanColor === 'black';
    if (wasBlack && first) {
      fen = START_FEN;
      render();
      await animateMove(first);
      playSfx('move');
    }

    if (data.mahoraga_elo !== undefined && data.mahoraga_elo !== null) {
      currentGameMahoragaElo = data.mahoraga_elo;
    }

    fen = liveFen;
    render();
    renderMoves();
    refreshProfile();

    showToast(wasBlack
      ? `RITUAL COMMENCED — MAHORAGA OPENED WITH ${first}`
      : 'RITUAL COMMENCED — YOU PLAY WHITE', 3000);

  } catch (e) {
    showToast(`Summoning failed: ${e.message}`);
  } finally {
    busy = false;
  }
}

/* ================= MOVE HISTORY TAB ================= */
function renderMoves() {
  const tbody = $('#moves-body');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (!moves.length) {
    tbody.innerHTML = '<tr class="empty-row"><td colspan="3" class="hint-text">The battle scroll is unwritten.</td></tr>';
    updateNavButtons();
    return;
  }

  const numPairs = Math.ceil(moves.length / 2);
  for (let i = 0; i < numPairs; i++) {
    const whiteIdx = i * 2;
    const blackIdx = i * 2 + 1;
    const whiteUci = moves[whiteIdx];
    const blackUci = moves[blackIdx];

    const tr = document.createElement('tr');

    const tdNum = document.createElement('td');
    tdNum.className = 'move-num-cell';
    tdNum.textContent = `${i + 1}.`;
    tr.appendChild(tdNum);

    const tdWhite = document.createElement('td');
    tdWhite.className = 'move-cell';
    tdWhite.textContent = whiteUci;
    if (viewIndex === whiteIdx + 1) tdWhite.classList.add('active-ply');
    tdWhite.onclick = () => setView(whiteIdx + 1);
    tr.appendChild(tdWhite);

    const tdBlack = document.createElement('td');
    tdBlack.className = 'move-cell';
    tdBlack.textContent = blackUci || '';
    if (blackUci && viewIndex === blackIdx + 1) tdBlack.classList.add('active-ply');
    if (blackUci) tdBlack.onclick = () => setView(blackIdx + 1);
    tr.appendChild(tdBlack);

    tbody.appendChild(tr);
  }

  updateNavButtons();

  // Scroll to active move
  const activeEl = tbody.querySelector('.active-ply');
  if (activeEl) {
    activeEl.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }
}

function updateNavButtons() {
  const first = $('#nav-first'), prev = $('#nav-prev'), next = $('#nav-next'), last = $('#nav-last'), live = $('#nav-live');
  if (first) first.disabled = viewIndex <= 0;
  if (prev) prev.disabled = viewIndex <= 0;
  if (next) next.disabled = viewIndex >= moves.length;
  if (last) last.disabled = viewIndex >= moves.length;
  if (live) live.disabled = viewIndex >= moves.length;
}

function setView(i) {
  if (!moves.length) return;
  viewIndex = Math.max(0, Math.min(moves.length, i));
  fen = (viewIndex === moves.length) ? liveFen : boardFen(viewIndex);
  clearLegal(); selected = null;
  render();
  renderMoves();
}

/* ================= 8-HANDLED MAHORAGA WHEEL (SVG RENDERER) ================= */
function renderWheel(wheelData) {
  const cats = [
    'Openings', 'Tactics', 'King safety', 'Development',
    'Endgames', 'Time mgmt', 'Structure', 'Psychology'
  ];

  const cx = 130, cy = 130;
  const rimRadius = 72;
  const innerRim = 60;
  const spokeLength = 104;
  const nodeRadius = 11;
  const hubRadius = 34;

  let spokesSvg = '';
  let nodesSvg = '';
  let gearTeethSvg = '';

  wheelRotation += 22.5;

  // Outer teeth / tick notches
  for (let t = 0; t < 32; t++) {
    const a = t * (360 / 32) * Math.PI / 180;
    const x1 = cx + (innerRim + 1) * Math.cos(a), y1 = cy + (innerRim + 1) * Math.sin(a);
    const x2 = cx + (rimRadius - 2) * Math.cos(a), y2 = cy + (rimRadius - 2) * Math.sin(a);
    gearTeethSvg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="rgba(255,255,255,0.15)" stroke-width="1.2"/>`;
  }

  for (let i = 0; i < 8; i++) {
    const angle = i * 45;
    const rad = (angle - 90) * Math.PI / 180;
    const cos = Math.cos(rad), sin = Math.sin(rad);

    const name = cats[i];
    const val = Math.max(0, Math.min(1, wheelData[name] || 0));

    const xNode = cx + spokeLength * cos;
    const yNode = cy + spokeLength * sin;

    // Spoke Line
    const spokeStroke = val > 0.05 ? '#ffffff' : '#333333';
    const spokeWidth = val > 0.05 ? 3.5 : 2;
    spokesSvg += `<line x1="${cx + (hubRadius - 2) * cos}" y1="${cy + (hubRadius - 2) * sin}" x2="${xNode}" y2="${yNode}" stroke="${spokeStroke}" stroke-width="${spokeWidth}" opacity="${(0.4 + 0.6 * val).toFixed(2)}"/>`;

    // Outer Sphere / Node
    const nodeFill = val > 0.5 ? '#ffffff' : (val > 0.05 ? '#777777' : '#141414');
    const nodeStroke = '#ffffff';
    nodesSvg += `
      <g class="wheel-node-group" data-category="${name}">
        <circle cx="${xNode}" cy="${yNode}" r="${nodeRadius}" fill="${nodeFill}" stroke="${nodeStroke}" stroke-width="2"/>
        ${val > 0 ? `<circle cx="${xNode}" cy="${yNode}" r="${nodeRadius + 4}" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-dasharray="2 2" opacity="${val}"/>` : ''}
      </g>
    `;
  }

  const avgCoverage = cats.reduce((s, k) => s + (wheelData[k] || 0), 0) / cats.length;
  const pctStr = Math.round(avgCoverage * 100);

  const svg = `
    <svg viewBox="0 0 260 260" class="wheel-svg">
      <defs>
        <filter id="wheel-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
      </defs>

      <!-- Outer Boundary Orbit -->
      <circle cx="${cx}" cy="${cy}" r="${spokeLength}" fill="none" stroke="#222222" stroke-width="1" stroke-dasharray="4 4"/>

      <!-- Main Rotating Rotor Group -->
      <g class="wheel-rotor" style="transform: rotate(${wheelRotation}deg);">
        <!-- Wheel Rims & Gear Track -->
        <circle cx="${cx}" cy="${cy}" r="${rimRadius}" fill="none" stroke="#ffffff" stroke-width="3" filter="url(#wheel-glow)"/>
        <circle cx="${cx}" cy="${cy}" r="${innerRim}" fill="none" stroke="#555555" stroke-width="1.5"/>
        ${gearTeethSvg}

        <!-- Spokes -->
        ${spokesSvg}

        <!-- 8 Outer Sphere Handles -->
        ${nodesSvg}
      </g>

      <!-- Center Hub (Stationary HUD) -->
      <circle cx="${cx}" cy="${cy}" r="${hubRadius}" fill="#080808" stroke="#ffffff" stroke-width="2.5"/>
      <circle cx="${cx}" cy="${cy}" r="${hubRadius - 5}" fill="#000000" stroke="#333333" stroke-width="1"/>
      <text x="${cx}" y="${cy - 4}" text-anchor="middle" dominant-baseline="middle" fill="#ffffff" font-family="JetBrains Mono" font-weight="700" font-size="14">${pctStr}%</text>
      <text x="${cx}" y="${cy + 12}" text-anchor="middle" dominant-baseline="middle" fill="#888888" font-family="JetBrains Mono" font-weight="600" font-size="7.5" letter-spacing="0.1em">HARMONY</text>
    </svg>
  `;

  const container = $('#wheel-container');
  if (container) container.innerHTML = svg;
}

/* ================= PROFILE & ADAPTATION REFRESH ================= */
async function refreshProfile() {
  if (!playerId) return;
  try {
    const [profile, wheel, weaknesses, adapt, eventsData] = await Promise.all([
      api(`/players/${playerId}/profile`),
      api(`/players/${playerId}/wheel`),
      api(`/players/${playerId}/weaknesses`),
      api(`/players/${playerId}/adaptation-status`),
      api(`/adaptation/events?player_id=${playerId}&limit=15`)
    ]);

    // Topbar Chips & Opponent Badges
    const effectiveElo = (currentSkillLevel !== null)
      ? currentSkillLevel
      : (currentGameMahoragaElo !== null ? currentGameMahoragaElo : profile.estimated_strength);

    const eloBadge = $('#mahoraga-elo');
    if (eloBadge) {
      const modeStr = currentSkillLevel !== null ? `${effectiveElo} (Fixed)` : `${effectiveElo}`;
      eloBadge.textContent = `${modeStr} (${profile.games_played}G ${profile.record.mahoraga_wins}W/${profile.record.player_wins}L)`;
    }

    const adaptChip = $('#adaptation-status');
    if (adaptChip) {
      adaptChip.textContent = adapt.fully_adapted
        ? 'FULLY ADAPTED'
        : `ADAPTING ${Math.round(adapt.adapted_coverage * 100)}%`;
    }

    // Opponent / Human Card Badges
    const oppEloBadge = $('#opponent-elo-badge');
    if (oppEloBadge) oppEloBadge.textContent = `(${effectiveElo})`;

    const playerRecBadge = $('#player-record-badge');
    if (playerRecBadge) playerRecBadge.textContent = `${profile.record.player_wins}W / ${profile.record.mahoraga_wins}L`;

    // Wheel Card
    renderWheel(wheel);

    const covEl = $('#metric-coverage');
    if (covEl) covEl.textContent = `${Math.round(adapt.adapted_coverage * 100)}%`;

    const winEl = $('#metric-winrate');
    if (winEl) winEl.textContent = `${Math.round(adapt.trailing_win_rate * 100)}%`;

    const patEl = $('#metric-patterns');
    if (patEl) patEl.textContent = weaknesses.length;

    const statusBadge = $('#wheel-status-badge');
    if (statusBadge) {
      if (adapt.fully_adapted) {
        statusBadge.textContent = 'ADAPTED';
        statusBadge.classList.add('active');
      } else if (weaknesses.length > 0) {
        statusBadge.textContent = 'WATCHING';
        statusBadge.classList.add('active');
      } else {
        statusBadge.textContent = 'STANDBY';
        statusBadge.classList.remove('active');
      }
    }

    // Tab Counts
    const countBadge = $('#weakness-tab-count');
    if (countBadge) countBadge.textContent = weaknesses.length;

    // Render Weaknesses Tab
    renderWeaknessesTab(weaknesses);

    // Render Events Tab
    renderEventsTab(eventsData.events || []);

  } catch (e) {
    if (/player not found/i.test(e.message)) clearPlayer();
    console.warn(e);
  }
}

function renderWeaknessesTab(weaknesses) {
  const container = $('#weaknesses-list');
  if (!container) return;

  if (!weaknesses.length) {
    container.innerHTML = '<p class="empty-hint">No weaknesses recorded yet. Defeat Mahoraga to turn the wheel.</p>';
    return;
  }

  let html = '';
  weaknesses.forEach(w => {
    const isAdapted = w.status === 'adapted';
    const pct = Math.round((w.confidence || 0) * 100);
    const motifs = (w.motifs || []).join(', ') || 'N/A';

    html += `
      <div class="weakness-item">
        <div class="weakness-header">
          <span class="weakness-title">${w.phenomenon.replace(/_/g, ' ')}</span>
          <span class="weakness-status-tag ${isAdapted ? 'adapted' : ''}">${w.status.toUpperCase()}</span>
        </div>
        <div class="weakness-bar-wrap">
          <div class="weakness-bar" style="width: ${pct}%;"></div>
        </div>
        <div class="weakness-meta">
          <span>CONFIDENCE: ${pct}%</span>
          <span>PHASE: ${(w.phase || 'N/A').toUpperCase()}</span>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function renderEventsTab(events) {
  const container = $('#events-feed');
  if (!container) return;

  if (!events.length) {
    container.innerHTML = '<p class="empty-hint">Awaiting adaptation events.</p>';
    return;
  }

  let html = '';
  events.forEach(ev => {
    const time = new Date(ev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    html += `
      <div class="event-log-entry">
        <strong>[${time}] ${ev.phenomenon.replace(/_/g, ' ').toUpperCase()}</strong> (${ev.phase})
        <br><span style="color:#888;">Severity: ${(ev.severity * 100).toFixed(0)}% | Ply: ${ev.ply}</span>
      </div>
    `;
  });

  container.innerHTML = html;
}

/* ================= HTTP API PLUMBING ================= */
async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  const text = await response.text();
  let data;
  try { data = text ? JSON.parse(text) : {}; }
  catch { data = { detail: text }; }
  if (!response.ok) throw new Error((data.detail || 'Request failed').replace(/^(['"])(.*)\1$/, '$2'));
  return data;
}

/* ================= BACKGROUND PARTICLE CANVAS (DOMAIN EXPANSION) ================= */
function initParticleCanvas() {
  const canvas = $('#particle-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];
  const count = 70;

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 1.8 + 0.5,
      speedX: (Math.random() - 0.5) * 0.4,
      speedY: (Math.random() - 0.5) * 0.4,
      alpha: Math.random() * 0.6 + 0.1
    });
  }

  function loop() {
    ctx.clearRect(0, 0, width, height);

    // Subtle central stipple sphere
    const cx = width / 2, cy = height / 2;
    const gradient = ctx.createRadialGradient(cx, cy, 10, cx, cy, Math.min(width, height) * 0.5);
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.03)');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // Particles
    particles.forEach(p => {
      p.x += p.speedX;
      p.y += p.speedY;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
      ctx.fillRect(p.x, p.y, p.size, p.size);
    });

    requestAnimationFrame(loop);
  }
  loop();
}

/* ================= SETTINGS DRAWER & UI WIRING ================= */
function openDrawer() {
  const drawer = $('#settings-drawer');
  const backdrop = $('#drawer-backdrop');
  if (drawer) drawer.setAttribute('aria-hidden', 'false');
  if (backdrop) backdrop.hidden = false;
  playSfx('click');
}

function closeDrawer() {
  const drawer = $('#settings-drawer');
  const backdrop = $('#drawer-backdrop');
  if (drawer) drawer.setAttribute('aria-hidden', 'true');
  if (backdrop) backdrop.hidden = true;
}

function initEvents() {
  // Menu Drawer
  const menuBtn = $('#menu-toggle');
  if (menuBtn) menuBtn.onclick = openDrawer;

  const closeBtn = $('#drawer-close');
  if (closeBtn) closeBtn.onclick = closeDrawer;

  const backdrop = $('#drawer-backdrop');
  if (backdrop) backdrop.onclick = closeDrawer;

  // New Game Buttons
  const drawerNew = $('#drawer-new-game');
  if (drawerNew) drawerNew.onclick = newGame;

  const mateNew = $('#mate-new-btn');
  if (mateNew) mateNew.onclick = newGame;

  // Side Selector
  $$('.side-choice-btn').forEach(btn => {
    btn.onclick = () => setSide(btn.dataset.side);
  });

  // Difficulty Select
  const skillSelect = $('#skill-level-select');
  if (skillSelect) {
    skillSelect.onchange = (e) => {
      currentSkillLevel = e.target.value === 'auto' ? null : parseInt(e.target.value, 10);
      currentGameMahoragaElo = currentSkillLevel;
      refreshProfile();
      showToast(currentSkillLevel !== null ? `MAHORAGA ELO SET TO ${currentSkillLevel}` : 'ADAPTIVE MODE (AUTO-ADJUSTING ELO)');
    };
  }

  // Toggles
  const soundCheck = $('#check-sound');
  const soundToggleBtn = $('#sound-toggle');
  const soundOnIcon = $('#sound-on-icon');
  const soundOffIcon = $('#sound-off-icon');

  function updateSoundUI() {
    if (soundCheck) soundCheck.checked = soundEnabled;
    if (soundOnIcon) soundOnIcon.style.display = soundEnabled ? 'block' : 'none';
    if (soundOffIcon) soundOffIcon.style.display = soundEnabled ? 'none' : 'block';
    try { localStorage.setItem('mahoragaSound', soundEnabled ? 'true' : 'false'); } catch (e) {}
  }

  if (soundCheck) {
    soundCheck.onchange = (e) => {
      soundEnabled = e.target.checked;
      updateSoundUI();
    };
  }

  if (soundToggleBtn) {
    soundToggleBtn.onclick = () => {
      soundEnabled = !soundEnabled;
      updateSoundUI();
      if (soundEnabled) playSfx('click');
    };
  }
  updateSoundUI();

  const coordsCheck = $('#check-coords');
  if (coordsCheck) {
    coordsCheck.onchange = (e) => {
      showCoords = e.target.checked;
      render();
    };
  }

  // Reset Player
  const resetBtn = $('#btn-reset-player');
  if (resetBtn) {
    resetBtn.onclick = () => {
      if (confirm('Purge all learned weaknesses and reset player profile?')) {
        clearPlayer();
        window.location.reload();
      }
    };
  }

  // Action Buttons
  const flipBtn = $('#btn-flip');
  if (flipBtn) {
    flipBtn.onclick = () => {
      bottom = bottom === 'w' ? 'b' : 'w';
      playSfx('click');
      render();
    };
  }

  const resignBtn = $('#btn-resign');
  if (resignBtn) {
    resignBtn.onclick = () => {
      if (gameOver()) return;
      if (confirm('Resign the battle to Mahoraga?')) {
        result = humanColor === 'white' ? '0-1' : '1-0';
        showMate(result);
        showToast('BATTLE RESIGNED — MAHORAGA ADAPTS');
      }
    };
  }

  const drawBtn = $('#btn-draw');
  if (drawBtn) {
    drawBtn.onclick = () => {
      if (gameOver()) return;
      showToast('DRAW CLAIMED — RITUAL CONCLUDED');
      result = '1/2-1/2';
      showMate(result);
    };
  }

  // Tab Switching
  $$('.tab-btn').forEach(btn => {
    btn.onclick = () => {
      const tabName = btn.dataset.tab;
      $$('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
      $$('.tab-pane').forEach(p => p.classList.toggle('active', p.id === `pane-${tabName}`));
      playSfx('click');
    };
  });

  // History Navigation
  const first = $('#nav-first'), prev = $('#nav-prev'), next = $('#nav-next'), last = $('#nav-last'), live = $('#nav-live');
  if (first) first.onclick = () => setView(0);
  if (prev) prev.onclick = () => setView(viewIndex - 1);
  if (next) next.onclick = () => setView(viewIndex + 1);
  if (last) last.onclick = () => setView(moves.length);
  if (live) live.onclick = () => setView(moves.length);
}

/* ================= INITIALIZATION ================= */
try {
  initParticleCanvas();
  initEvents();
  render();
  renderMoves();
  renderWheel({});
  refreshProfile();
} catch (err) {
  console.error('Initialization error:', err);
}