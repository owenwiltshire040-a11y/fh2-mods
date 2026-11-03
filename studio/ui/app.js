// FH2 Car Studio front end: projects, setup, and the step-by-step car editor around a three.js viewer.
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';

const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const HUB_Y = 0.156, AXLE_MID = 0.0867;
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

async function api(url, opts = {}) {
  const r = await fetch(url, opts); let j = null;
  try { j = await r.json(); } catch (e) { throw new Error(`${url}: HTTP ${r.status}`); }
  if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`);
  return j;
}
const post = (url, body, raw = false) => api(url, {method: 'POST', body: raw ? body : JSON.stringify(body ?? {}), headers: raw ? {} : {'Content-Type': 'application/json'}});
let toastT;
function toast(msg, err = false) { const t = $('#toast'); t.textContent = msg; t.className = err ? 'err' : ''; clearTimeout(toastT); toastT = setTimeout(() => t.className = 'hidden', err ? 9000 : 3500); }

// ---------------------------------------------------------------- frames (same maths as studio/analyze.py)
const AX = {'+x': [1, 0, 0], '-x': [-1, 0, 0], '+y': [0, 1, 0], '-y': [0, -1, 0], '+z': [0, 0, 1], '-z': [0, 0, -1]};
function orientMatrix(front, up) {
  const f = new THREE.Vector3(...AX[front]), u = new THREE.Vector3(...AX[up]), r = new THREE.Vector3().crossVectors(f, u);
  return new THREE.Matrix4().set(r.x, r.y, r.z, 0, u.x, u.y, u.z, 0, f.x, f.y, f.z, 0, 0, 0, 0, 1);
}
function fh2Params(P) { const W = P.wheels, s = P.real_wheelbase / (W.zf - W.zr); return {s, off: new THREE.Vector3(0, HUB_Y - W.yc * s, AXLE_MID - (W.zf + W.zr) / 2 * s)}; }

// ---------------------------------------------------------------- viewer
class Viewer {
  constructor(el) {
    this.el = el; const r = this.r = new THREE.WebGLRenderer({antialias: true}); r.setPixelRatio(Math.min(devicePixelRatio, 2));
    r.outputColorSpace = THREE.SRGBColorSpace; r.toneMapping = THREE.ACESFilmicToneMapping; r.setClearColor(0x000000, 0); el.appendChild(r.domElement);
    this.scene = new THREE.Scene(); this.scene.environment = new THREE.PMREMGenerator(r).fromScene(new RoomEnvironment(), 0.04).texture;
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x404040, 1.0));
    const sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(-3, 6, 4); this.scene.add(sun);
    this.cam = new THREE.PerspectiveCamera(35, 1, 0.01, 500); this.cam.position.set(-6, 3, 6);
    this.ctl = new OrbitControls(this.cam, r.domElement); this.ctl.enableDamping = true;
    this.holder = new THREE.Group(); this.holder.matrixAutoUpdate = false; this.scene.add(this.holder);
    this.over = new THREE.Group(); this.scene.add(this.over);
    this.grid = new THREE.GridHelper(20, 40, 0x555555, 0x2a2a2a); this.scene.add(this.grid);
    this.hot = new Set(); this.onPick = null;
    new ResizeObserver(() => this.resize()).observe(el); this.resize();
    let down = null;
    r.domElement.addEventListener('pointerdown', e => down = [e.clientX, e.clientY]);
    r.domElement.addEventListener('pointerup', e => { if (down && Math.hypot(e.clientX - down[0], e.clientY - down[1]) < 4) this.pick(e); down = null; });
    const loop = () => { this.ctl.update(); r.render(this.scene, this.cam); requestAnimationFrame(loop); }; loop();
  }
  resize() { const w = this.el.clientWidth || 600, h = this.el.clientHeight || 400; this.r.setSize(w, h); this.cam.aspect = w / h; this.cam.updateProjectionMatrix(); }
  async load(url) {
    if (this.url === url) return; this.url = url;
    const g = await new GLTFLoader().loadAsync(url);
    this.holder.clear(); this.model = g.scene; this.holder.add(g.scene); this.meshes = [];
    g.scene.traverse(o => {
      if (!o.isMesh) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      o.material = mats.map(m => { const c = m.clone(); c.side = THREE.DoubleSide; c.userData.e0 = c.emissive ? c.emissive.clone() : null; return c; });
      if (o.material.length === 1) o.material = o.material[0];
      this.meshes.push(o);
    });
    this.highlight(this.hot);
  }
  setMatrix(m) { this.holder.matrix.copy(m); this.holder.updateMatrixWorld(true); }
  bbox() { return new THREE.Box3().setFromObject(this.holder); }
  frameView(kind = 'three') {
    const b = this.bbox(); if (b.isEmpty()) return; const c = b.getCenter(new THREE.Vector3()), sz = b.getSize(new THREE.Vector3()), d = sz.length() * 1.15;
    const dirs = {front: [0, 0.15, 1], side: [-1, 0.12, 0], top: [0, 1, 0.001], three: [-0.8, 0.45, 0.9], rear: [0, 0.2, -1]};
    const v = new THREE.Vector3(...dirs[kind]).normalize();
    this.cam.position.copy(c).addScaledVector(v, d); this.ctl.target.copy(c); this.cam.near = d / 200; this.cam.far = d * 20; this.cam.updateProjectionMatrix();
    this.grid.position.y = b.min.y; this.grid.scale.setScalar(Math.max(sz.x, sz.z) / 8);
  }
  highlight(names) {
    this.hot = names instanceof Set ? names : new Set(names || []);
    for (const o of this.meshes || []) for (const m of (Array.isArray(o.material) ? o.material : [o.material])) {
      if (!m.emissive) continue;
      if (this.hot.has(m.name)) { m.emissive.setRGB(0.9, 0.45, 0.05); m.emissiveIntensity = 1; } else if (m.userData.e0) m.emissive.copy(m.userData.e0);
    }
  }
  pick(e) {
    if (!this.onPick || !this.meshes) return;
    const rc = new THREE.Raycaster(), b = this.r.domElement.getBoundingClientRect();
    rc.setFromCamera(new THREE.Vector2((e.clientX - b.left) / b.width * 2 - 1, -(e.clientY - b.top) / b.height * 2 + 1), this.cam);
    const hit = rc.intersectObjects(this.meshes, false)[0]; if (!hit) return;
    const m = Array.isArray(hit.object.material) ? hit.object.material[hit.face.materialIndex] : hit.object.material;
    this.onPick(m.name, hit.point);
  }
}

// ---------------------------------------------------------------- app state
let L = null, P = null, A = null, V = null, step = 'model', saveT = null, jobPoll = null;
const STEPS = ['model', 'wheels', 'materials', 'lights', 'driver', 'car', 'build'];

function show(page) { for (const p of ['home', 'setup', 'editor']) $('#' + p).classList.toggle('hidden', p !== page); }
function route() {
  const h = location.hash.slice(1); clearInterval(jobPoll);
  if (h === 'setup') { show('setup'); loadSetup(); }
  else if (h.startsWith('car/')) { const [, slug, st] = h.split('/'); openProject(slug, st); }
  else { show('home'); loadHome(); }
}
window.addEventListener('hashchange', route);
$$('#topnav button').forEach(b => b.onclick = () => location.hash = b.dataset.go === 'home' ? '' : b.dataset.go);
$('#home-link').onclick = () => location.hash = '';

// ---------------------------------------------------------------- home
async function loadHome() {
  const [list, st] = await Promise.all([api('/api/projects'), api('/api/setup')]);
  const bad = st.items.filter(i => !i.ok);
  $('#setup-banner').classList.toggle('hidden', !bad.length);
  $('#setup-banner').innerHTML = `Setup isn't finished (${bad.map(i => esc(i.name)).join('; ')}). <a href="#setup" style="color:var(--accent)">Open Setup</a>`;
  $('#project-list').innerHTML = list.length ? list.map(p => `<div class="pcard" data-slug="${esc(p.slug)}">
      <div class="img">${p.built ? `<img src="/cars/${esc(p.slug)}/build/thumb.png?${Date.now()}" alt="">` : 'not built yet'}</div>
      <div class="t"><b>${esc(p.name)}</b><span class="muted small">${p.installed ? 'installed ' + esc(p.installed) : 'created ' + esc(p.created || '')}</span></div></div>`).join('')
    : '<p class="muted">No studio cars yet.</p>';
  $$('.pcard').forEach(c => c.onclick = () => location.hash = 'car/' + c.dataset.slug);
}
$('#new-go').onclick = async () => {
  const f = $('#new-file').files[0], name = $('#new-name').value.trim();
  if (!name) return toast('Give the car a name first', true); if (!f) return toast('Choose a .glb file', true);
  $('#new-go').disabled = true; $('#new-go').textContent = 'Reading model…';
  try { const r = await post('/api/projects?name=' + encodeURIComponent(name), await f.arrayBuffer(), true); location.hash = 'car/' + r.slug + '/model'; }
  catch (e) { toast(e.message, true); } finally { $('#new-go').disabled = false; $('#new-go').textContent = 'Create'; }
};

// ---------------------------------------------------------------- setup
async function loadSetup() { renderSetup(await api('/api/setup')); }
function renderSetup(st) {
  $('#setup-items').innerHTML = st.items.map(i => `<div class="setup-item"><div class="dot ${i.ok ? 'ok' : ''}"></div>
    <div><b>${esc(i.name)}</b><div class="muted small">${esc(i.detail)}</div></div>
    <div>${i.ok && i.id !== 'mods' ? '<span class="muted small">ready</span>' : `<button data-fix="${i.id}">${esc(i.fix)}</button>`}</div>
    ${i.path && (!i.ok || i.id === 'mods') ? `<div class="path"><input data-path="${i.id}" placeholder="full path (drag the file into Terminal to see it), or leave empty to search" value="${i.id === 'mods' ? esc(st.settings.mods_dir) : ''}"></div>` : ''}</div>`).join('');
  $$('[data-fix]').forEach(b => b.onclick = async () => {
    const id = b.dataset.fix, inp = document.querySelector(`[data-path="${id}"]`); b.disabled = true; b.textContent = 'Working…';
    try { const r = await post('/api/setup/fix', {id, path: inp && inp.value.trim() || null}); $('#setup-log').textContent = r.log; $('#setup-log').classList.remove('hidden'); renderSetup({items: r.items, settings: (await api('/api/setup')).settings}); toast('Done'); }
    catch (e) { toast(e.message, true); b.disabled = false; b.textContent = 'Retry'; }
  });
}

// ---------------------------------------------------------------- editor
async function openProject(slug, st) {
  show('editor');
  if (!V) V = new Viewer($('#viewer'));
  if (!L) L = await api('/api/lists').catch(e => { toast('Game lists unavailable: ' + e.message, true); return {makes: [], countries: [], sounds: [], buckets: []}; });
  if (!P || P.slug !== slug) {
    const r = await api('/api/project/' + slug); P = r.project; A = r.analysis; V.url = null;
    await V.load(`/cars/${slug}/src/model.glb`);
  }
  $('#ed-name').textContent = P.name;
  $$('#steps li').forEach(li => li.onclick = () => location.hash = `car/${P.slug}/${li.dataset.step}`);
  goStep(STEPS.includes(st) ? st : 'model');
}
function save(now = false) {
  clearTimeout(saveT); $('#savestate').textContent = 'saving…';
  const f = () => post(`/api/project/${P.slug}/save`, P).then(() => $('#savestate').textContent = 'saved').catch(e => { $('#savestate').textContent = 'not saved!'; toast(e.message, true); });
  if (now) return f(); saveT = setTimeout(f, 500);
}
const needGeo = () => !P.geometry;
async function ensureGeometry(force = false) {
  if (!force && P.geometry && P._geoKey === geoKey()) return;
  await save(true); $('#viewer-hint').textContent = 'converting the model…';
  const r = await post(`/api/project/${P.slug}/geometry`); P = r.project; P._geoKey = geoKey(); $('#viewer-hint').textContent = '';
}
const geoKey = () => JSON.stringify([P.orient, P.wheels, P.real_wheelbase]);

function setFrame(mode) {
  if (mode === 'built') { V.setMatrix(new THREE.Matrix4()); V.frame = mode; return; }   // the built car's preview glb is already in FH2 space
  const M = orientMatrix(P.orient.front, P.orient.up);
  if (mode === 'fh2') { const {s, off} = fh2Params(P); M.premultiply(new THREE.Matrix4().makeScale(s, s, s)).premultiply(new THREE.Matrix4().makeTranslation(off.x, off.y, off.z)); }
  V.setMatrix(M); V.frame = mode;
}
function navButtons() {
  const i = STEPS.indexOf(step);
  return `<div class="nav">${i > 0 ? `<button data-nav="${STEPS[i - 1]}">← Back</button>` : '<span></span>'}${i < STEPS.length - 1 ? `<button class="primary" data-nav="${STEPS[i + 1]}">Next →</button>` : ''}</div>`;
}
function wireNav() { $$('[data-nav]').forEach(b => b.onclick = async () => { b.disabled = true; try { await leaveStep(step); location.hash = `car/${P.slug}/${b.dataset.nav}`; } catch (e) { toast(e.message, true); b.disabled = false; } }); }
async function leaveStep(s) { if (s === 'wheels' || s === 'model') { await ensureGeometry(); } else await save(true); }

async function goStep(s) {
  if (['materials', 'lights', 'driver', 'car', 'build'].includes(s) && needGeo()) { try { await ensureGeometry(true); } catch (e) { toast(e.message, true); s = 'wheels'; } }
  step = s; $$('#steps li').forEach(li => { li.classList.toggle('active', li.dataset.step === s); });
  V.over.clear(); V.highlight([]); V.onPick = null; $('#viewer-hint').textContent = '';
  if (V.url !== `/cars/${P.slug}/src/model.glb`) await V.load(`/cars/${P.slug}/src/model.glb`);
  ({model: stepModel, wheels: stepWheels, materials: stepMaterials, lights: stepLights, driver: stepDriver, car: stepCar, build: stepBuild})[s]();
}
$$('#viewer-tools button').forEach(b => b.onclick = () => V.frameView(b.dataset.view));

// ---- 1 model
function stepModel() {
  setFrame('oriented'); V.frameView('three');
  const c = P.credits, o = P.orient;
  $('#panel').innerHTML = `<h2>Model</h2><p class="muted">${A.tris.toLocaleString()} triangles, ${A.materials.length} materials.</p>
    <h3>Which way is it facing?</h3><p class="small muted">The car's nose must point at you in the <b>Front</b> view, wheels on the grid.</p>
    <div class="field"><span>Nose points along</span><select id="o-front">${['+z', '-z', '+x', '-x'].map(a => `<option ${a === o.front ? 'selected' : ''}>${a}</option>`).join('')}</select></div>
    <div class="field"><span>Up is</span><select id="o-up">${['+y', '+z', '-z', '-y'].map(a => `<option ${a === o.up ? 'selected' : ''}>${a}</option>`).join('')}</select></div>
    <h3>Credits (shown in the mod)</h3>
    <div class="grid2"><label>Model title<input id="c-title" value="${esc(c.title)}"></label><label>Author<input id="c-author" value="${esc(c.author)}"></label>
    <label>Licence<input id="c-lic" value="${esc(c.licence)}" placeholder="e.g. CC BY 4.0"></label><label>Link<input id="c-url" value="${esc(c.url)}"></label></div>
    <p class="small muted">Check the licence allows what you do with it. Personal-use mods only.</p>
    <h3>Name</h3><div class="field"><span>Mod / folder name</span><input id="p-name" value="${esc(P.name)}"></div>${navButtons()}`;
  const upd = async () => {
    const f = $('#o-front').value, u = $('#o-up').value;
    if (f[1] === u[1]) return toast('Front and up must be different axes', true);
    const changed = f !== P.orient.front || u !== P.orient.up; P.orient = {front: f, up: u}; setFrame('oriented'); V.frameView('front');
    if (changed) { await save(true); const r = await post(`/api/project/${P.slug}/guesswheels`); P.wheels = r.project.wheels; P.wheels_found = r.project.wheels_found; }
  };
  $('#o-front').onchange = upd; $('#o-up').onchange = upd;
  for (const [id, k] of [['c-title', 'title'], ['c-author', 'author'], ['c-lic', 'licence'], ['c-url', 'url']]) $('#' + id).oninput = e => { P.credits[k] = e.target.value; save(); };
  $('#p-name').oninput = e => { P.name = e.target.value; $('#ed-name').textContent = P.name; save(); };
  wireNav();
}

// ---- 2 wheels
function wheelOverlay() {
  V.over.clear(); const W = P.wheels, mat = new THREE.MeshBasicMaterial({color: 0xe8a33d, transparent: true, opacity: 0.35, depthTest: false});
  const edge = new THREE.LineBasicMaterial({color: 0xffc46b, depthTest: false});
  for (const z of [W.zf, W.zr]) for (const sx of [-1, 1]) {
    const g = new THREE.CylinderGeometry(W.r, W.r, W.r * 0.55, 40); g.rotateZ(Math.PI / 2);
    const m = new THREE.Mesh(g, mat); m.position.set(sx * W.xh, W.yc, z); m.renderOrder = 10; V.over.add(m);
    const e = new THREE.LineSegments(new THREE.EdgesGeometry(g, 30), edge); e.position.copy(m.position); e.renderOrder = 11; V.over.add(e);
  }
  const lo = W.yc - W.r; const ground = new THREE.Mesh(new THREE.PlaneGeometry(50, 50), new THREE.MeshBasicMaterial({color: 0x4fa3e0, transparent: true, opacity: 0.08, side: THREE.DoubleSide}));
  ground.rotation.x = -Math.PI / 2; ground.position.y = lo; V.over.add(ground);
}
function stepWheels() {
  setFrame('oriented'); V.frameView('side'); wheelOverlay();
  const b = V.bbox(), sz = b.getSize(new THREE.Vector3()), W = P.wheels, L_ = Math.max(sz.z, 0.01);
  const sl = (k, label, min, max) => `<div class="slider"><div class="top"><span>${label}</span><b id="v-${k}">${(+W[k]).toFixed(3)}</b></div>
      <input type="range" id="w-${k}" min="${min}" max="${max}" step="${(max - min) / 2000}" value="${W[k]}"></div>`;
  $('#panel').innerHTML = `<h2>Wheels</h2>
    <p class="muted">Line the orange cylinders up with the tyres: use <b>Side</b> for front/rear and height, <b>Front</b> for width. ${P.wheels_found ? 'They were found automatically — check them.' : '<span class="warn">Couldn\'t find the wheels automatically — set them by eye.</span>'}</p>
    ${sl('zf', 'Front axle (fore/aft)', b.min.z, b.max.z)}${sl('zr', 'Rear axle (fore/aft)', b.min.z, b.max.z)}
    ${sl('yc', 'Wheel centre height', b.min.y, b.min.y + sz.y * 0.6)}${sl('r', 'Tyre radius', L_ * 0.02, L_ * 0.2)}${sl('xh', 'Half track (centre to tyre middle)', 0, sz.x * 0.6)}
    <button id="w-guess" class="small">Detect again</button>
    <h3>Real size</h3>
    <div class="field"><span>Real wheelbase (m)</span><input type="number" step="0.001" id="w-wb" value="${P.real_wheelbase}"></div>
    <p class="small muted">From the car's spec sheet — this sets the model's scale (now ×<span id="w-scale"></span>).</p>
    <h3>Wheel position in the arches</h3>
    <div class="field"><span>Track from</span><select id="w-track"><option value="auto">the arches (cars)</option><option value="tyres">these cylinders (lorries, no arches)</option></select></div>
    <div class="field"><span>Tyre stick-out past the arch (m)</span><input type="number" step="0.01" id="w-lip" value="${P.lip_gap}"></div>
    <p class="small muted">0.04 suits most cars; wheels hiding under the arches in game → raise it (the Omoda needed 0.08).</p>${navButtons()}`;
  const upd = () => { for (const k of ['zf', 'zr', 'yc', 'r', 'xh']) $('#v-' + k).textContent = (+P.wheels[k]).toFixed(3); $('#w-scale').textContent = (P.real_wheelbase / (P.wheels.zf - P.wheels.zr)).toFixed(4); wheelOverlay(); save(); };
  for (const k of ['zf', 'zr', 'yc', 'r', 'xh']) $('#w-' + k).oninput = e => { P.wheels[k] = +e.target.value; upd(); };
  $('#w-wb').oninput = e => { P.real_wheelbase = +e.target.value || P.real_wheelbase; upd(); };
  $('#w-track').value = P.track_mode; $('#w-track').onchange = e => { P.track_mode = e.target.value; save(); };
  $('#w-lip').oninput = e => { P.lip_gap = +e.target.value; save(); };
  $('#w-guess').onclick = async () => { await save(true); const r = await post(`/api/project/${P.slug}/guesswheels`); P.wheels = r.project.wheels; P.wheels_found = r.project.wheels_found; stepWheels(); };
  upd(); wireNav();
}

// ---- 3 materials
const ROLES = [['paint', 'Paint (car colour)'], ['chrome', 'Chrome / metal'], ['black', 'Black trim'], ['glass', 'Glass'], ['colour', 'Own colour'], ['texture', 'Texture'], ['drop', 'Leave out']];
function stepMaterials() {
  setFrame('fh2'); V.frameView('three');
  const cnt = P.geometry.counts, byName = Object.fromEntries(A.materials.map(m => [m.name, m]));
  const body = A.materials.filter(m => cnt[m.name]), wheel = Object.keys(cnt).filter(k => k.startsWith('RIM_'));
  const row = m => { const v = P.materials[m.name]; return `<div class="matrow" data-m="${esc(m.name)}"><div class="sw" style="background:${v.role === 'colour' ? v.colour : m.colour}"></div>
      <div class="nm" title="${esc(m.name)}">${esc(m.name)}<small>${cnt[m.name].toLocaleString()}</small></div>
      <select data-role="${esc(m.name)}">${ROLES.filter(([r]) => r !== 'texture' || m.textured).map(([r, t]) => `<option value="${r}" ${v.role === r ? 'selected' : ''}>${t}</option>`).join('')}</select>
      ${v.role === 'colour' ? `<div class="extra">colour <input type="color" data-col="${esc(m.name)}" value="${v.colour}"></div>` : ''}</div>`; };
  const wrow = k => `<div class="matrow" data-m="${esc(k.slice(4))}"><div class="sw" style="background:${byName[k.slice(4)]?.colour || '#888'}"></div>
      <div class="nm">${esc(k.slice(4))}<small>${cnt[k].toLocaleString()}</small></div>
      <select data-wm="${esc(k)}">${[['silver', 'Rim (bright)'], ['black', 'Rim (dark)'], ['drop', 'Leave out (tyre/brake)']].map(([r, t]) => `<option value="${r}" ${P.wheel_materials[k] === r ? 'selected' : ''}>${t}</option>`).join('')}</select></div>`;
  $('#panel').innerHTML = `<h2>Materials</h2><p class="muted">What each of the model's materials becomes in the game. Hover a row to light it up in orange; click the model to find a part.</p>
    <h3>Body</h3>${body.map(row).join('')}
    <h3>Wheels</h3><p class="small muted">The game draws its own tyres; the rim is rebuilt from these.</p>${wheel.length ? wheel.map(wrow).join('') : '<p class="warn">No wheel geometry inside the cylinders — check the Wheels step.</p>'}
    <h3>Shading</h3><label style="flex-direction:row;gap:8px;align-items:center"><input type="checkbox" id="m-one" ${P.one_sided ? 'checked' : ''}> Single-sided body (like the game's cars; untick if panels go see-through)</label>
    ${navButtons()}`;
  $$('[data-role]').forEach(s => s.onchange = e => { P.materials[s.dataset.role].role = e.target.value; save(); stepMaterials(); });
  $$('[data-col]').forEach(s => s.oninput = e => { P.materials[s.dataset.col].colour = e.target.value; s.closest('.matrow').querySelector('.sw').style.background = e.target.value; save(); });
  $$('[data-wm]').forEach(s => s.onchange = e => { P.wheel_materials[s.dataset.wm] = e.target.value; save(); });
  $('#m-one').onchange = e => { P.one_sided = e.target.checked; save(); };
  $$('.matrow').forEach(r => { r.onmouseenter = () => V.highlight([r.dataset.m]); r.onmouseleave = () => V.highlight([]); });
  V.onPick = name => { const r = document.querySelector(`.matrow[data-m="${CSS.escape(name)}"]`); if (!r) return; $$('.matrow.hot').forEach(x => x.classList.remove('hot')); r.classList.add('hot'); r.scrollIntoView({block: 'center', behavior: 'smooth'}); V.highlight([name]); };
  wireNav();
}

// ---- 4 lights
const LAMPS = [['head', 'Headlights', 'front'], ['drl', 'Daytime running lights', 'front'], ['turn_f', 'Front indicators', 'front'],
               ['tail', 'Tail + brake lights', 'rear'], ['reverse', 'Reverse lights', 'rear'], ['turn_r', 'Rear indicators', 'rear'], ['chmsl', 'Third brake light', 'rear']];
function stepLights() {
  setFrame('fh2'); V.frameView('three');
  let active = P._activeLamp || 'head';
  const mats = A.materials.filter(m => P.geometry.counts[m.name]).map(m => m.name);
  const draw = () => {
    $('#panel').innerHTML = `<h2>Lights</h2><p class="muted">Pick each lamp's materials. Only the part of a material in the front half (headlights, indicators) or rear half (the rest) is used, so one material can serve both ends. Pick a lamp, then click the model to add/remove a material.</p>
      ${LAMPS.map(([k, t, end]) => { const sel = P.lights[k] || []; return `<div class="card" data-lamp="${k}" style="padding:8px 10px;margin:8px 0;${k === active ? 'border-color:var(--accent)' : ''}">
        <div class="row" style="justify-content:space-between;align-items:center"><b>${t}</b><span class="small muted">${end}</span></div>
        <div class="chips">${sel.map(m => `<span class="chip on" data-rm="${esc(m)}" title="remove">${esc(m)} ✕</span>`).join('') || '<span class="small muted">none</span>'}</div>
        <select data-add="${k}"><option value="">+ add material…</option>${mats.filter(m => !sel.includes(m)).map(m => `<option>${esc(m)}</option>`).join('')}</select></div>`; }).join('')}
      <p class="small muted">Lamps light up by day and night; the brake lights also come on when braking. A car without some of these is fine.</p>${navButtons()}`;
    $$('[data-lamp]').forEach(c => c.onclick = e => { if (e.target.closest('select,.chip')) return; active = P._activeLamp = c.dataset.lamp; draw(); });
    $$('[data-add]').forEach(s => s.onchange = e => { const k = s.dataset.add; if (!e.target.value) return; (P.lights[k] = P.lights[k] || []).push(e.target.value); active = P._activeLamp = k; save(); draw(); });
    $$('[data-rm]').forEach(c => c.onclick = () => { const k = c.closest('[data-lamp]').dataset.lamp; P.lights[k] = P.lights[k].filter(m => m !== c.dataset.rm); save(); draw(); });
    V.highlight(P.lights[active] || []); wireNav();
  };
  V.onPick = name => { if (!mats.includes(name)) return; const l = P.lights[active] = P.lights[active] || []; const i = l.indexOf(name); if (i >= 0) l.splice(i, 1); else l.push(name); save(); draw(); };
  draw();
}

// ---- 5 driver
function driverOverlay() {
  V.over.clear(); const s = P.driver.steer; if (!s) return;
  const st = new THREE.Vector3(...s), hips = st.clone().add(new THREE.Vector3(-0.015, -0.28, -0.43)), eye = hips.clone().add(new THREE.Vector3(0, 0.62, 0));
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.18, 0.02, 10, 40), new THREE.MeshBasicMaterial({color: 0xe8a33d, depthTest: false}));
  ring.position.copy(st); ring.rotation.x = -0.35; ring.renderOrder = 10; V.over.add(ring);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.11, 20, 14), new THREE.MeshBasicMaterial({color: 0x4fa3e0, depthTest: false, transparent: true, opacity: 0.8}));
  head.position.copy(eye); head.renderOrder = 10; V.over.add(head);
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, eye.y - hips.y - 0.12, 16), new THREE.MeshBasicMaterial({color: 0x4fa3e0, depthTest: false, transparent: true, opacity: 0.35}));
  body.position.set(hips.x, (hips.y + eye.y - 0.12) / 2, hips.z); body.renderOrder = 9; V.over.add(body);
}
function stepDriver() {
  setFrame('fh2'); V.frameView('side'); driverOverlay();
  const s = P.driver.steer, b = V.bbox();
  const sl = (i, label, min, max, val) => `<div class="slider"><div class="top"><span>${label}</span><b id="d-v${i}">${val.toFixed(3)}</b></div><input type="range" id="d-${i}" min="${min}" max="${max}" step="0.005" value="${val}"></div>`;
  $('#panel').innerHTML = `<h2>Driver</h2><p class="muted">Put the orange ring where the steering wheel is. The blue figure (hips and head) follows it. Use <b>Side</b> and <b>Top</b>.</p>
    <div class="field"><span>Driving side</span><select id="d-side"><option value="L">Left-hand drive</option><option value="R">Right-hand drive (UK)</option></select></div>
    ${sl(0, 'Steering wheel: distance from the middle', 0, Math.max(b.max.x, 0.5), Math.abs(s[0]))}${sl(1, 'Steering wheel: height', b.min.y, b.max.y, s[1])}${sl(2, 'Steering wheel: fore/aft', b.min.z, b.max.z, s[2])}
    <p class="small muted">The in-game driver uses the Charger's body and animations, scaled to this position.</p>${navButtons()}`;
  $('#d-side').value = s[0] > 0 ? 'R' : 'L';
  const upd = () => { const side = $('#d-side').value === 'R' ? 1 : -1; P.driver.side = $('#d-side').value;
    P.driver.steer = [side * +$('#d-0').value, +$('#d-1').value, +$('#d-2').value]; [0, 1, 2].forEach(i => $('#d-v' + i).textContent = (+$('#d-' + i).value).toFixed(3)); driverOverlay(); save(); };
  ['d-side', 'd-0', 'd-1', 'd-2'].forEach(id => $('#' + id).oninput = upd); $('#d-side').onchange = upd;
  wireNav();
}

// ---- 6 car details
const CLASS_COL = ['#d6d6d6', '#5cc6f2', '#f5cb3c', '#f08a24', '#e5534b', '#b35df0', '#4cc38a'];
function stepCar() {
  setFrame('fh2'); V.frameView('three');
  const c = P.car, opt = (list, v) => list.map(o => `<option value="${esc(o.id)}" ${String(o.id) === String(v) ? 'selected' : ''}>${esc(o.name)}</option>`).join('');
  const num = (k, label, step = 1) => `<label>${label}<input type="number" step="${step}" data-c="${k}" value="${c[k] ?? ''}"></label>`;
  const sel = (k, label, opts) => `<label>${label}<select data-c="${k}">${opts.map(([v, t]) => `<option value="${v}" ${String(c[k]) === String(v) ? 'selected' : ''}>${t}</option>`).join('')}</select></label>`;
  $('#panel').innerHTML = `<h2>Car details</h2>
    <div class="est" id="est"></div><p class="small muted" id="est-note"></p>
    <h3>Make</h3>
    <div class="field"><span>Make</span><select data-c="make_mode"><option value="existing" ${c.make_mode === 'existing' ? 'selected' : ''}>a make already in the game</option><option value="new" ${c.make_mode === 'new' ? 'selected' : ''}>a new make</option></select></div>
    ${c.make_mode === 'existing' ? `<label>Make<select id="mk">${L.makes.map(m => `<option value="${m.id}" ${+c.make_id === m.id ? 'selected' : ''}>${esc(m.name)}</option>`).join('')}</select></label>`
      : `<div class="grid3"><label>Name<input data-c="make_name" value="${esc(c.make_name)}"></label><label>3-letter code<input data-c="make_code" maxlength="3" value="${esc(c.make_code)}"></label>
         <label>Country<select data-c="make_country">${opt(L.countries, c.make_country)}</select></label></div>
         <div class="row" style="margin-top:6px"><label class="file">Logo (PNG, transparent) <input type="file" id="logo" accept="image/png"></label><button class="small" id="nologo">Use a text logo</button></div>
         <p class="small muted">Without a logo the make's name is written in white as the logo.</p>`}
    <h3>Model</h3>
    <div class="grid2"><label>Model name<input data-c="model_name" value="${esc(c.model_name)}"></label><label>Short name<input data-c="short_name" value="${esc(c.short_name)}"></label>
    ${num('year', 'Year')}${num('price', 'Price (credits)', 500)}</div>
    <label style="margin-top:6px">Autoshow category<select data-c="bucket">${opt(L.buckets, c.bucket)}</select></label>
    <h3>Engine</h3>
    <div class="grid3">${num('hp', 'Power (hp)')}${num('rpm_power', '…at rpm', 100)}${num('redline', 'Rev limit', 100)}${num('nm', 'Torque (Nm)')}${num('rpm_torque', '…at rpm', 100)}${num('displacement_l', 'Litres', 0.1)}
    ${num('cylinders', 'Cylinders')}${sel('layout', 'Layout', [['I', 'Inline'], ['V', 'V'], ['F', 'Flat / boxer'], ['W', 'W'], ['R', 'Rotary']])}
    ${sel('aspiration', 'Induction', [['na', 'Natural'], ['turbo', 'Turbo'], ['twin', 'Twin turbo'], ['super', 'Supercharged']])}${sel('fuel', 'Fuel', [['petrol', 'Petrol'], ['diesel', 'Diesel']])}</div>
    <label style="margin-top:6px">Engine sound (borrowed from a game car)<select data-c="sound">${opt(L.sounds, c.sound)}</select></label>
    <h3>Drivetrain</h3>
    <div class="grid3">${sel('drive', 'Drive', [['FWD', 'Front'], ['RWD', 'Rear'], ['AWD', 'All']])}${sel('engine_pos', 'Engine', [['front', 'Front'], ['mid', 'Mid'], ['rear', 'Rear']])}${sel('transmission', 'Gearbox', [['manual', 'Manual'], ['auto', 'Auto / DCT']])}</div>
    <div class="grid2" style="margin-top:6px"><label>Gear ratios (up to 8)<input id="gears" value="${c.gears.join(', ')}"></label>${num('final_drive', 'Final drive', 0.01)}</div>
    <h3>Body</h3>
    <div class="grid3">${num('mass', 'Weight (kg)', 5)}${num('weight_front', 'Weight on front (0-1)', 0.01)}${num('cd', 'Drag coefficient', 0.01)}${num('width', 'Width, no mirrors (m)', 0.01)}${num('steer_deg', 'Steering lock (°)')}</div>
    <h3>Tyres &amp; brakes</h3>
    <div class="grid3">${num('tyre_fw', 'Front width mm', 5)}${num('tyre_fa', 'Front profile', 5)}${num('rim_in', 'Rims (in, ≤24)')}${num('tyre_rw', 'Rear width mm', 5)}${num('tyre_ra', 'Rear profile', 5)}<span></span>${num('brake_f', 'Front discs mm', 5)}${num('brake_r', 'Rear discs mm', 5)}</div>
    <h3>Performance (blank = estimate)</h3>
    <div class="grid3">${num('t60', '0-60 mph (s)', 0.1)}${num('top_mph', 'Top speed mph')}${sel('class_override', 'Class', [['auto', 'from PI'], ...['D', 'C', 'B', 'A', 'S1', 'S2', 'X'].map(x => [x, x])])}</div>
    <h3>Thumbnail</h3><div class="field"><span>Paint colour for the Autoshow picture</span><input type="color" data-c="paint" value="${c.paint}"></div>
    ${navButtons()}`;
  const coerce = (k, v) => ['make_mode', 'make_name', 'make_code', 'model_name', 'short_name', 'layout', 'aspiration', 'fuel', 'drive', 'engine_pos', 'transmission', 'paint', 'sound', 'class_override'].includes(k) ? v : (v === '' ? null : +v);
  $$('[data-c]').forEach(el => el.oninput = el.onchange = e => {
    const k = el.dataset.c; c[k] = coerce(k, e.target.value); save(); est();
    if (k === 'make_mode') { if (c.make_mode === 'existing' && !c.make_id) pickMake(L.makes[0]); stepCar(); }
  });
  const pickMake = m => { Object.assign(c, {make_id: m.id, make_ref: m.ref, make_name: m.name.replace(/ \(.*$/, ''), make_code: m.code, make_country: m.country, make_icon: m.icon, make_depends: m.depends || null}); save(); };
  if ($('#mk')) $('#mk').onchange = e => pickMake(L.makes.find(m => m.id === +e.target.value));
  $('#gears').oninput = e => { const g = e.target.value.split(/[ ,;]+/).map(Number).filter(x => x > 0); if (g.length) { c.gears = g.slice(0, 8); save(); } };
  if ($('#logo')) $('#logo').onchange = async e => { const f = e.target.files[0]; if (!f) return; await post(`/api/project/${P.slug}/logo`, await f.arrayBuffer(), true); toast('Logo saved'); };
  if ($('#nologo')) $('#nologo').onclick = async () => { await post(`/api/project/${P.slug}/nologo`); toast('Using a text logo'); };
  let estT;
  const est = () => { clearTimeout(estT); estT = setTimeout(async () => {
    try { await save(true); const e = await api(`/api/project/${P.slug}/estimates`);
      $('#est').innerHTML = `<div><b><span class="classbadge" style="background:${CLASS_COL[e.cls]}">${e.cls_name}</span> ${Math.round(e.pi * 1000)}</b><span>class / PI</span></div>
        <div><b>${e.t60}s</b><span>0-60 mph</span></div><div><b>${Math.round(e.top_mph)}</b><span>top speed mph</span></div>`;
      $('#est-note').textContent = `Ratings: speed ${e.ratings[0]}, handling ${e.ratings[1]}, acceleration ${e.ratings[2]}, braking ${e.ratings[3]}, launch ${e.ratings[4]} — estimated from the specs like the game's own cars.`;
    } catch (err) { $('#est').innerHTML = `<p class="warn">${esc(err.message)}</p>`; } }, 400); };
  est(); wireNav();
}

// ---- 7 build
function stepBuild() {
  setFrame('fh2'); V.frameView('three');
  const cr = P.credits, warn = [];
  if (!cr.author) warn.push('No model author in the credits (Model step).');
  if (!Object.values(P.materials).some(m => m.role === 'paint')) warn.push('No material is set to Paint — the car will have no paintable body.');
  if (!Object.values(P.wheel_materials || {}).some(v => v === 'silver' || v === 'black')) warn.push('No rim materials — the car would keep the Charger\'s rims.');
  $('#panel').innerHTML = `<h2>Build &amp; install</h2>
    ${warn.map(w => `<p class="warn">⚠ ${esc(w)}</p>`).join('')}
    <p class="muted">Builds the car (a minute or two), shows you the result here, renders the Autoshow picture and packs the mod.</p>
    <button class="primary" id="b-go">Build</button> <button id="b-install" disabled>Install into the game</button>
    <div id="b-state" class="small muted" style="margin:8px 0"></div>
    <img id="b-thumb" class="thumbimg hidden" alt="Autoshow thumbnail">
    <h3>Log</h3><pre id="b-log" class="log">—</pre>
    <h3>Testing in game</h3><p class="small muted">Restart the game after installing. If the wheels sit too far in, raise the stick-out on the Wheels step; if one side is see-through, untick single-sided on Materials; then build and install again — your old version is kept in the project's backups folder.</p>
    ${navButtons()}`;
  let since = 0, thumbing = false;
  const poll = async () => {
    const j = await api(`/api/project/${P.slug}/job?since=${since}`); since = j.n;
    if (j.log.length) { const el = $('#b-log'); if (el.textContent === '—') el.textContent = ''; el.textContent += j.log.join('\n') + '\n'; el.scrollTop = 1e9; }
    $('#b-state').textContent = {running: 'Building…', need_thumb: 'Rendering the thumbnail…', done: 'Ready to install ✓', error: 'Failed: ' + (j.error || '')}[j.state] || '';
    $('#b-go').disabled = j.state === 'running' || j.state === 'need_thumb';
    $('#b-install').disabled = j.state !== 'done';
    if (j.state === 'need_thumb' && !thumbing) { thumbing = true; await V.load(j.preview); setFrame('built'); V.frameView('three'); $('#viewer-hint').textContent = 'the built car, as converted for the game'; renderThumb(j.preview); }
    if (j.state === 'done') { $('#b-thumb').src = `/cars/${P.slug}/build/thumb.png?${Date.now()}`; $('#b-thumb').classList.remove('hidden'); }
    if (['done', 'error'].includes(j.state) || !j.state) clearInterval(jobPoll);
  };
  $('#b-go').onclick = async () => {
    try { await save(true); await post(`/api/project/${P.slug}/build`); $('#b-log').textContent = ''; since = 0; thumbing = false; clearInterval(jobPoll); jobPoll = setInterval(poll, 800); }
    catch (e) { toast(e.message, true); }
  };
  $('#b-install').onclick = async () => { try { const r = await post(`/api/project/${P.slug}/install`); toast(r.message); $('#b-state').textContent = r.message; } catch (e) { toast(e.message, true); } };
  clearInterval(jobPoll); jobPoll = setInterval(poll, 800); poll();
  wireNav();
}
function renderThumb(preview) {
  const f = $('#thumbframe'); f.src = `/viewer/thumb.html?f=${encodeURIComponent(preview)}&w=816&h=459&yaw=-50&pitch=10`;
  const t0 = Date.now();
  const wait = setInterval(async () => {
    let doc; try { doc = f.contentDocument; } catch (e) { return; }
    if (Date.now() - t0 > 120000) { clearInterval(wait); toast('Thumbnail render timed out', true); return; }
    if (!doc || doc.title !== 'done') return;
    clearInterval(wait);
    const cv = doc.querySelector('canvas'); cv.toBlob(async b => { try { await post(`/api/project/${P.slug}/thumb`, b, true); } catch (e) { toast(e.message, true); } }, 'image/png');
  }, 300);
}

route();
