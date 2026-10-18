// lab.js — the Grammar in Numbers laboratory.  Every outcome shown here is
// computed live by gin-core.js, whose results are checked against the Python
// SDK (ginsdk) by `npm test`.  Widgets that show stored experiment data say so
// and name the file.  Every widget has a written text alternative in the page.
import "./gin-core.js";
import "./num-core.js";
const G = globalThis.GIN;
const N = globalThis.NUM;   // research lane THE NUMBER (num-core.js, checked against research/the-number/numlab)

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const WIDGETS = {};
export function mount(el) {
  const name = el.dataset.demo;
  const w = WIDGETS[name];
  if (!w) { el.insertAdjacentHTML("beforeend", `<p class="lab-note">Unknown demo “${esc(name)}”.</p>`); return; }
  const host = document.createElement("div");
  host.className = "lab-panel";
  el.appendChild(host);
  w(host, el.dataset.rel || "");
  el.classList.add("ready");
}
const $ = (host, k) => host.querySelector(`[data-k="${k}"]`);
const DOMAIN_OPTIONS = ["Q", "Z", "N", "Z/7", "Z/6", "binary64", "binary32", "binary16", "Python", "JS Number", "JS BigInt",
  "int32 x86-64", "int32 AArch64", "int32 RISC-V", "int32 C", "int32 Java", "int32 Rust (debug)", "int32 Go"];
const STATUS_CLASS = (s) => ({ value: "ok", special: "warn", "no-solution": "bad", "non-unique": "bad2", undefined: "bad", trap: "bad", exception: "bad" }[s] || "muted");
const REL_TEXT = { agrees: "agrees with exact mathematics", rounded: "is a rounding of the exact value", wrapped: "wrapped around modulo 2³²",
  totalized: "returns a value where mathematics has none (a convention, not a solution)", "special-datum": "returns a special datum (∞ or NaN), not a number",
  signalled: "refuses: trap or exception", undefined: "has undefined behaviour", selected: "selects a quotient (division with remainder) where the exact quotient does not exist",
  "different-selection": "selects a different quotient-with-remainder than the Euclidean one", "overflowed-to-special": "overflows to ±∞", differs: "differs from exact mathematics",
  "not-applicable": "—" };

function treeSvg(t) {
  // simple layered layout
  const nodes = []; let x = 0;
  (function lay(n, d) { const kids = n.children.map((c) => lay(c, d + 1)); const me = { n, d, x: kids.length ? (kids[0].x + kids[kids.length - 1].x) / 2 : x++, kids }; nodes.push(me); return me; })(t, 0);
  const W = Math.max(1, x) * 54 + 20, H = (Math.max(...nodes.map((m) => m.d)) + 1) * 52 + 10;
  const px = (m) => 20 + m.x * 54 + 7, py = (m) => 22 + m.d * 52;
  const edges = nodes.flatMap((m) => m.kids.map((k) => `<line class="edge" x1="${px(m)}" y1="${py(m)}" x2="${px(k)}" y2="${py(k)}"/>`)).join("");
  const dots = nodes.map((m) => `<g><circle class="node${m.n.kind === "num" ? "" : " on"}" cx="${px(m)}" cy="${py(m)}" r="15"/><text x="${px(m)}" y="${py(m) + 4}" text-anchor="middle"${m.n.kind === "num" ? "" : ' style="fill:var(--paper)"'}>${esc(String(m.n.label).slice(0, 6))}</text></g>`).join("");
  return `<svg class="lab-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="parse tree">${edges}${dots}</svg>`;
}

// ===================================================================== the arithmetic laboratory
WIDGETS["arith"] = (host) => {
  host.innerHTML = `
  <div class="lab-row"><label>expression <input data-k="e" value="1 / 0" size="22" spellcheck="false" aria-describedby="arith-help"></label>
  <label>domain <select data-k="d">${DOMAIN_OPTIONS.map((d) => `<option>${esc(d)}</option>`).join("")}</select></label>
  <button data-k="go">Inspect</button></div>
  <p class="lab-note" id="arith-help">Try <button class="chip" data-x="1 + 1">1 + 1</button> <button class="chip" data-x="6 / 3">6 / 3</button> <button class="chip" data-x="0 / 1">0 / 1</button> <button class="chip" data-x="1 / 0">1 / 0</button> <button class="chip" data-x="0 / 0">0 / 0</button> <button class="chip" data-x="1 + 1 - 10₂">1 + 1 − 10₂</button> <button class="chip" data-x="0.1 + 0.2">0.1 + 0.2</button> <button class="chip" data-x="2147483647 + 1">2147483647 + 1</button> <button class="chip" data-x="2 / 4">2 / 4</button> (try ℤ/6). Operators: + − × / // % ^, sqrt( ), gcd( , ); numerals 0b101, 0x1F, 10₂.</p>
  <div class="layers" data-k="layers" aria-live="polite"></div>
  <div class="lab-cmp"><div class="lab-card"><h4>Parse tree</h4><div data-k="tree"></div></div><div class="lab-card"><h4>Representation of the result</h4><div class="lab-out" data-k="rep"></div></div></div>
  <div class="lab-card"><h4>Trace</h4><div class="lab-out" data-k="steps"></div></div>`;
  const run = () => {
    const e = $(host, "e").value, d = $(host, "d").value;
    const r = G.relation(e, d), o = r.selected, m = r.reference;
    const L = (name, ok, text) => `<div class="layer layer-${ok === true ? "ok" : ok === false ? "bad" : "muted"}"><span class="layer-name">${name}</span><span>${text}</span></div>`;
    const stop = o.layer, order = ["syntax", "typing", "semantics", "execution"];
    const state = (l) => (stop === l ? false : stop === null || order.indexOf(l) < order.indexOf(stop) ? true : null);
    const toks = (() => { try { return G.tokenize(e).filter((t) => t.kind !== "end").map((t) => `<code>${esc(t.text)}</code>`).join(" "); } catch { return "—"; } })();
    host.querySelector('[data-k="layers"]').innerHTML =
      L("1 · syntax", state("syntax"), o.status === "syntax-error" ? `not well formed: ${esc(o.reason)}` : `well formed; tokens ${toks}`) +
      L("2 · typing", state("typing"), stop === "typing" ? esc(o.reason) : state("typing") === null ? "not reached" : `every literal names an element of <b>${esc(o.domain)}</b>`) +
      L("3 · mathematics", m.status === "value" ? true : m.status === "syntax-error" ? null : false, m.status === "value" ? `exact value in ${esc(m.domain)}: <b>${esc(m.display)}</b>` : m.status === "syntax-error" ? "—" : `<b>${esc(m.status)}</b> in ${esc(m.domain)}: ${esc(m.reason)}${m.equation ? ` &nbsp;·&nbsp; defining equation <code>${esc(m.equation)}</code>${m.solutions ? `, solutions ${esc(m.solutions)}` : ""}` : ""}`) +
      (o.domain === m.domain ? L("4 · execution", null, `${esc(o.domain)} is an exact mathematical domain: there is no separate machine layer, and the outcome is the mathematical one`) :
      L("4 · execution", o.status === "value" ? true : o.status === "special" ? null : state("execution") === null && stop !== "execution" ? null : false,
        o.status === "value" || o.status === "special" ? `<b>${esc(o.domain)}</b> produces <b class="st-${STATUS_CLASS(o.status)}">${esc(o.display)}</b>${o.flags.length ? ` &nbsp;flags: ${o.flags.map((f) => `<code>${f}</code>`).join(" ")}` : ""}` : `<b>${esc(o.status)}</b> (${esc(o.layer)}): ${esc(o.reason)}`)) +
      L("5 · comparison", r.kind === "agrees" ? true : r.kind === "not-applicable" ? null : false, `the selected domain ${esc(REL_TEXT[r.kind] || r.kind)}${o.notes.length ? `<br><span class="lab-note">${o.notes.map(esc).join("<br>")}</span>` : ""}`);
    $(host, "tree").innerHTML = o.tree ? treeSvg(o.tree) : "<p class='lab-note'>no tree: the string is not an expression</p>";
    $(host, "rep").textContent = Object.keys(o.representation || {}).length ? Object.entries(o.representation).map(([k, v]) => `${k}: ${v}`).join("\n") : "—";
    $(host, "steps").textContent = o.steps.length ? o.steps.map((s, i) => `${i + 1}. ${s.op} (${s.operands.join(", ")}) → ${s.result}${s.rule ? "   [" + s.rule + "]" : ""}${s.equation ? "   " + s.equation : ""}`).join("\n") : "(no operation executed)";
  };
  $(host, "go").addEventListener("click", run);
  $(host, "e").addEventListener("keydown", (ev) => { if (ev.key === "Enter") run(); });
  $(host, "d").addEventListener("change", run);
  host.querySelectorAll(".chip").forEach((b) => b.addEventListener("click", () => { $(host, "e").value = b.dataset.x; if (b.dataset.x === "2 / 4") $(host, "d").value = "Z/6"; run(); }));
  run();
};

// ===================================================================== one expression, every machine
WIDGETS["machines"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>expression <input data-k="e" value="1 / 0" size="22" spellcheck="false"></label><button data-k="go">Compare</button></div><div class="table-wrap"><table class="lab-table"><thead><tr><th>domain</th><th>outcome</th><th>layer</th><th>value / reason</th><th>relation to exact mathematics</th></tr></thead><tbody data-k="rows"></tbody></table></div>`;
  const run = () => {
    const e = $(host, "e").value;
    $(host, "rows").innerHTML = DOMAIN_OPTIONS.map((d) => { const r = G.relation(e, d), o = r.selected;
      return `<tr><td><code>${esc(d)}</code></td><td class="st-${STATUS_CLASS(o.status)}">${esc(o.status)}</td><td>${esc(o.layer || "—")}</td><td>${o.status === "value" || o.status === "special" ? `<b>${esc(o.display)}</b>${o.flags.length ? " " + o.flags.map((f) => `<code>${f}</code>`).join(" ") : ""}` : esc(o.reason).slice(0, 110)}</td><td>${esc(r.kind)}</td></tr>`; }).join("");
  };
  $(host, "go").addEventListener("click", run);
  $(host, "e").addEventListener("keydown", (ev) => { if (ev.key === "Enter") run(); });
  run();
};

// ===================================================================== binary addition and the carry monoid
WIDGETS["carry"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>a <input data-k="a" value="11" size="8"></label><label>b <input data-k="b" value="1" size="8"></label><label>width <input data-k="w" type="number" min="2" max="32" value="8" style="width:4rem"></label><button data-k="go">Add in binary</button></div><div class="lab-out" data-k="out" aria-live="polite"></div>`;
  const run = () => {
    let a = BigInt($(host, "a").value || 0), b = BigInt($(host, "b").value || 0); const w = Math.max(2, Math.min(32, Number($(host, "w").value)));
    const M = (1n << BigInt(w)) - 1n; a &= M; b &= M;
    const bit = (x, i) => Number((x >> BigInt(i)) & 1n);
    const cls = [], carries = [0]; let c = 0, chain = 0, longest = 0;
    for (let i = 0; i < w; i++) {
      const k = bit(a, i) + bit(b, i) === 2 ? "G" : bit(a, i) + bit(b, i) === 1 ? "P" : "K"; cls.push(k);
      c = k === "G" ? 1 : k === "K" ? 0 : c; carries.push(c);
      chain = k === "G" ? 1 : k === "P" && chain ? chain + 1 : 0; longest = Math.max(longest, chain);
    }
    const s = (a + b) & M, cout = (a + b) >> BigInt(w);
    const row = (label, f) => label.padEnd(11) + Array.from({ length: w }, (_, j) => f(w - 1 - j)).join(" ");
    $(host, "out").textContent = [
      row("position", (i) => String(i % 10)),
      row("a", (i) => bit(a, i)), row("b", (i) => bit(b, i)),
      row("class", (i) => cls[i]),
      row("carry in", (i) => carries[i]),
      row("sum", (i) => bit(s, i)),
      "",
      `${a} + ${b} = ${a + b}${cout ? `  (carry out of the top position: in ${w} bits the result wraps to ${s})` : ""}`,
      `K = kill (carry becomes 0), P = propagate (carry passes), G = generate (carry becomes 1).`,
      `Longest carry chain: ${longest} position(s). Composite of all positions: ${cls.reduceRight((acc, k) => acc === "P" ? k : acc, "P")} (the carry monoid {K, P, G}).`,
    ].join("\n");
  };
  $(host, "go").addEventListener("click", run); host.querySelectorAll("input").forEach((i) => i.addEventListener("change", run)); run();
};

// ===================================================================== floating-point fields
WIDGETS["float"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>decimal <input data-k="x" value="0.1" size="16" spellcheck="false"></label><button data-k="go">Encode</button></div><div class="lab-out" data-k="out" aria-live="polite"></div>`;
  const run = () => {
    const txt = $(host, "x").value.trim();
    let q; try { const o = G.evaluate(txt, "Q"); if (o.status !== "value") throw new Error(o.reason); q = o.value; } catch (e) { $(host, "out").textContent = "Not an exact rational expression: " + e.message; return; }
    const lines = [`exact value: ${q.toString()}`, ""];
    for (const f of ["binary16", "binary32", "binary64"]) {
      const F = G.FORMATS[f]; const [v, fl] = G.roundExact(F, q, 0); const fd = G.fpFields(v);
      const exact = v.cls === "finite" ? (v.sign ? v.mag.neg() : v.mag) : null;
      lines.push(`${f.padEnd(9)} ${G.showFP(v).padEnd(24)} sign ${fd.sign} | exponent ${fd.exponent} | fraction ${fd.fraction}`);
      lines.push(`          ${[...fl].length ? "flags: " + [...fl].join(", ") : "exact: no rounding"}${exact && !exact.eq(q) ? `   stored value = ${exact.toString().length < 80 ? exact.toString() : "(a dyadic rational with " + exact.d.toString(2).length + "-bit denominator)"}` : ""}`);
    }
    $(host, "out").textContent = lines.join("\n");
  };
  $(host, "go").addEventListener("click", run); $(host, "x").addEventListener("keydown", (ev) => { if (ev.key === "Enter") run(); }); run();
};

// ===================================================================== division in Z/n: the image/kernel grid
WIDGETS["zmod"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>n <input data-k="n" type="number" min="2" max="24" value="6" style="width:4rem"></label><button data-k="go">Draw</button></div>
  <p class="lab-note">Row b, column a: is a / b admissible in ℤ/n? <span class="cell ok">c</span> unique quotient c · <span class="cell bad">∅</span> no solution (image failure) · <span class="cell bad2">k</span> k solutions (kernel failure).</p><div data-k="grid" class="zgrid"></div><p class="lab-note" data-k="sum"></p>`;
  const run = () => {
    const n = Math.max(2, Math.min(24, Number($(host, "n").value))); const D = `Z/${n}`;
    let uniq = 0, none = 0, many = 0;
    let html = `<table class="lab-table zt"><thead><tr><th>b \\ a</th>${Array.from({ length: n }, (_, a) => `<th>${a}</th>`).join("")}</tr></thead><tbody>`;
    for (let b = 0; b < n; b++) {
      html += `<tr><th>${b}</th>`;
      for (let a = 0; a < n; a++) {
        const o = G.evaluate(`${a} / ${b}`, D);
        if (o.status === "value") { uniq++; html += `<td class="cell ok" title="${a}/${b} = ${o.display}">${o.display}</td>`; }
        else if (o.status === "no-solution") { none++; html += `<td class="cell bad" title="${esc(o.reason)}">∅</td>`; }
        else { many++; const k = (o.solutions.match(/\d+/g) || []).length - 0; html += `<td class="cell bad2" title="${esc(o.solutions)}">${Math.max(2, k - 1)}</td>`; }
      }
      html += "</tr>";
    }
    $(host, "grid").innerHTML = html + "</tbody></table>";
    $(host, "sum").textContent = `${uniq} of ${n * n} pairs have a unique quotient (n·φ(n) = ${uniq}); ${none} have none; ${many} have several. A row has a unique quotient everywhere exactly when gcd(b, n) = 1 (Theorem GIN-THM-002).`;
  };
  $(host, "go").addEventListener("click", run); $(host, "n").addEventListener("change", run); run();
};

// ===================================================================== numerals of n
WIDGETS["numerals"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>n <input data-k="n" type="number" min="0" max="100000" value="4" style="width:7rem"></label><button data-k="go">Write n</button></div><div class="lab-out" data-k="out" aria-live="polite"></div>`;
  const bij = (n, b) => { let s = ""; while (n > 0) { const d = ((n - 1) % b) + 1; s = String(d) + s; n = (n - d) / b; } return s || "ε"; };
  const bal3 = (n) => { let s = ""; while (n !== 0) { let d = ((n % 3) + 3) % 3; if (d === 2) d = -1; s = (d === -1 ? "T" : String(d)) + s; n = (n - d) / 3; } return s || "ε"; };
  const run = () => {
    const n = Math.max(0, Math.min(100000, Math.floor(Number($(host, "n").value))));
    const rows = [["unary (successor term)", n <= 40 ? (n ? "S".repeat(n) + "0" : "0") : `S^${n}(0)`], ["bijective base 2 (digits 1, 2)", bij(n, 2)], ["binary", n.toString(2)],
      ["ternary", n.toString(3)], ["balanced ternary (T = −1)", bal3(n)], ["decimal", String(n)], ["hexadecimal", n.toString(16).toUpperCase()]];
    const heap = (n + 1).toString(2).slice(1).replace(/0/g, "L").replace(/1/g, "R") || "ε";
    $(host, "out").textContent = rows.map(([k, v]) => `${k.padEnd(32)} ${v}`).join("\n") +
      `\n\nThe value ${n} is the invariant; each line is a different word denoting it.\nCanonical address of ${n} in the CGT heap grammar of node ${n + 1}: ${heap} (bijective binary with 1→L, 2→R; GIN-PROP-006).` +
      `\nZero's canonical numeral is the empty word ε; the written "0" is a convention (GIN-PROP-002).`;
  };
  $(host, "go").addEventListener("click", run); $(host, "n").addEventListener("change", run); run();
};

// ===================================================================== Euclid with invariants
WIDGETS["euclid"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>a <input data-k="a" value="1071" size="10"></label><label>b <input data-k="b" value="462" size="10"></label><button data-k="go">Run Euclid</button></div><div class="lab-out" data-k="out" aria-live="polite"></div>`;
  const run = () => {
    const a0 = BigInt($(host, "a").value || 0), b0 = BigInt($(host, "b").value || 0);
    let [r0, r1] = [a0 < 0n ? -a0 : a0, b0 < 0n ? -b0 : b0], [s0, s1] = [1n, 0n], [t0, t1] = [0n, 1n];
    const lines = ["   r            s            t            invariant r = s·a + t·b"];
    const fmt = (x) => String(x).padStart(10);
    lines.push(`${fmt(r0)}   ${fmt(s0)}   ${fmt(t0)}   ${r0 === s0 * r0 + t0 * r1 - t0 * r1 ? "✓" : ""}`);
    let steps = 0;
    while (r1 !== 0n) {
      lines.push(`${fmt(r1)}   ${fmt(s1)}   ${fmt(t1)}   ${r1 === s1 * (a0 < 0n ? -a0 : a0) + t1 * (b0 < 0n ? -b0 : b0) ? "✓" : "✗"}`);
      const q = r0 / r1; [r0, r1] = [r1, r0 - q * r1]; [s0, s1] = [s1, s0 - q * s1]; [t0, t1] = [t1, t0 - q * t1]; steps++;
    }
    lines.push(`         0`, "", `gcd = ${r0} = (${s0})·${a0 < 0n ? -a0 : a0} + (${t0})·${b0 < 0n ? -b0 : b0}   after ${steps} division step(s).`,
      `Each move (a, b) → (b, a mod b) is admissible only when b ≠ 0; the terminal state (g, 0) has no admissible move.`);
    $(host, "out").textContent = lines.join("\n");
  };
  $(host, "go").addEventListener("click", run); run();
};

// ===================================================================== measured cost (stored experiment data)
WIDGETS["cost"] = (host, rel) => {
  host.innerHTML = `<p class="lab-note">Stored data: <code>experiments/results/exp008.json</code> (GIN-EXP-008), counted 32-bit limb operations of <code>ginsdk.bigint</code> on random operands. Axes are logarithmic.</p><div data-k="plot"></div><div class="lab-out" data-k="tab"></div>`;
  fetch(rel + "assets/experiments.json").then((r) => r.json()).then((x) => {
    const rows = x.exp008.data.rows;
    const keys = ["add", "mul_schoolbook", "mul_karatsuba", "divmod_2L_by_L", "gcd_euclid", "powmod_L_bit_exponent"];
    const e = { bits: rows.map((r) => r.bits) };
    const series = keys.map((k) => [k, rows.map((r) => r[k] ?? 0)]);
    const xs = e.bits, W = 560, H = 300, P = 44;
    const all = series.flatMap(([, v]) => v).filter((v) => v > 0);
    const lx = (v) => P + (Math.log2(v) - Math.log2(xs[0])) / (Math.log2(xs[xs.length - 1]) - Math.log2(xs[0])) * (W - 2 * P);
    const ymin = Math.log10(Math.min(...all)), ymax = Math.log10(Math.max(...all));
    const ly = (v) => H - P - (Math.log10(v) - ymin) / (ymax - ymin) * (H - 2 * P);
    const colors = ["var(--emerald)", "var(--brass)", "var(--claret)", "var(--slate)", "var(--ink-3)", "var(--ink)"];
    const paths = series.map(([k, v], i) => `<polyline fill="none" stroke="${colors[i % 6]}" stroke-width="2" points="${v.map((y, j) => y > 0 ? `${lx(xs[j])},${ly(y)}` : "").join(" ")}"/><text x="${W - P + 4}" y="${ly(v.filter((y) => y > 0).slice(-1)[0] || 1)}" style="fill:${colors[i % 6]}">${esc(k)}</text>`).join("");
    const ticks = xs.map((b) => `<text x="${lx(b)}" y="${H - P + 16}" text-anchor="middle" class="lbl">${b}</text>`).join("");
    $(host, "plot").innerHTML = `<svg class="lab-svg" viewBox="0 0 ${W + 90} ${H}" role="img" aria-label="Counted limb operations against operand bits, log-log"><line class="edge" x1="${P}" y1="${H - P}" x2="${W - P}" y2="${H - P}"/><line class="edge" x1="${P}" y1="${P / 2}" x2="${P}" y2="${H - P}"/>${ticks}<text x="${W / 2}" y="${H - 6}" text-anchor="middle" class="lbl">operand length (bits)</text>${paths}</svg>`;
    $(host, "tab").textContent = ["bits".padStart(7) + series.map(([k]) => k.padStart(16)).join(""), ...xs.map((b, j) => String(b).padStart(7) + series.map(([, v]) => String(v[j] ?? "").padStart(16)).join(""))].join("\n");
  }).catch((err) => { $(host, "tab").textContent = "Could not load the stored data: " + err.message; });
};

// ===================================================================== research lane THE NUMBER (NUM-*; not claims of the edition)
// zero, empty, absent: the census probes run in the reader's own JavaScript engine, next to stored results
WIDGETS["num-zero"] = (host, rel) => {
  host.innerHTML = `<p class="lab-note">Live column: computed now by <em>your</em> browser's JavaScript engine. Stored columns: <code>research/the-number/results/num_exp001.json</code> (NUM-EXP-001; Node 22, Python 3.13, SQLite 3.45.1). A difference in the live column is a finding about your engine, not an error of the page.</p><div data-k="js"></div><div data-k="py"></div>`;
  const live = N.zeroProbes();
  fetch(rel + "assets/num_results.json").then((r) => r.json()).then((x) => {
    const e1 = x.num_exp001, node = (e1.js_census.results || {});
    const rows = Object.keys(live).map((k) => `<tr><td><code>${esc(k)}</code></td><td>${esc(live[k])}</td><td>${esc(node[k] ?? "—")}</td><td>${live[k] === node[k] ? "" : "≠"}</td></tr>`).join("");
    $(host, "js").innerHTML = `<table class="lab-table"><thead><tr><th>JavaScript probe</th><th>your engine</th><th>stored (${esc(e1.js_census.node || "node")})</th><th></th></tr></thead><tbody>${rows}</tbody></table>`;
    const py = e1.python_census, sq = e1.sqlite_census;
    $(host, "py").innerHTML = `<div class="lab-out">Python (stored): ${py.equality_classes.length} equality classes under == among ${Object.keys(py.objects).length} zero-like objects; the numeric class is\n  ${esc(py.equality_classes[0].join(", "))}\ninserting 7 numeric zeros as dict keys leaves ${Object.keys(py.dict_after_inserting_7_zero_keys).length} key.\nSubstitutivity failures (x == y but f(x) ≠ f(y)):\n  ${py.substitutivity_failures.map(esc).join("\n  ")}\n\nSQLite ${esc(sq.sqlite_version)} (stored): SUM over an empty table = ${sq["SUM over empty table"]}, TOTAL = ${sq["TOTAL over empty table"]}, COUNT = ${sq["COUNT over empty table"]}; NULL = NULL is ${sq["NULL = NULL"]}; 1/0 = ${sq["1/0"]}.</div>`;
  }).catch((err) => { $(host, "js").textContent = "Could not load the stored data: " + err.message; });
};

// one value, many words: translation between numeration systems
WIDGETS["num-translate"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>n <input data-k="n" type="number" value="1994" min="-1000000" max="1000000000" style="width:9rem"></label><button data-k="go">Translate</button></div><table class="lab-table" data-k="out" aria-live="polite"></table><p class="lab-note" data-k="note"></p>`;
  const run = () => {
    const n = Math.max(-1e6, Math.min(1e9, Math.trunc(Number($(host, "n").value) || 0)));
    const rows = Object.entries(N.SYSTEMS).map(([k, label]) => { const w = N.encode(k, n); return `<tr><td>${esc(label)}</td><td><code>${w === null ? "— (no word: outside this system's language)" : esc(w)}</code></td><td>${w === null ? "O1 fails" : w.length}</td></tr>`; }).join("");
    $(host, "out").innerHTML = `<thead><tr><th>system</th><th>canonical word for ${n}</th><th>length</th></tr></thead><tbody>${rows}</tbody>`;
    $(host, "note").textContent = `Every row denotes the same value; a dash is a translation that fails obligation O1 (value preservation) — Roman has no zero and no negatives, unsigned systems have no negatives, 8-bit two's complement stops at 127. Uniqueness of each word is a property of the system's language: allow leading zeros, or two adjacent Fibonacci terms, and the same value gets many words (NUM-HYP-002).`;
  };
  $(host, "go").addEventListener("click", run); $(host, "n").addEventListener("change", run); run();
};

// spatial grammar canvas: two channels, a vertical place-value comparator, and the browser's own bidi rendering
WIDGETS["num-spatial"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>left glyph <select data-k="a">${[1, 2, 3, 4, 5, 6, 7, 8, 9].map((d) => `<option${d === 2 ? " selected" : ""}>${d}</option>`).join("")}</select></label>
  <label>right glyph <select data-k="b">${[1, 2, 3, 4, 5, 6, 7, 8, 9].map((d) => `<option${d === 3 ? " selected" : ""}>${d}</option>`).join("")}</select></label>
  <label>Maya-style n <input data-k="m" type="number" value="1000" min="0" max="3199999" style="width:8rem"></label><button data-k="go">Lay out</button></div>
  <div class="lab-cmp"><div class="lab-card"><h4>Horizontal × vertical channel</h4><div data-k="grid"></div></div><div class="lab-card"><h4>Vertical place value (bottom = units)</h4><div class="lab-out" data-k="maya"></div></div></div>
  <div class="lab-card"><h4>Digit order inside right-to-left text, rendered by your browser</h4><div data-k="bidi"></div></div>`;
  const run = () => {
    const a = $(host, "a").value, b = $(host, "b").value;
    const t = N.channelTable(a, b), rels = [["base", "on the baseline"], ["sup", "raised (exponent)"], ["sub", "lowered (base of the left run)"]];
    const cell = (k) => { const v = t[k]; return v === null || v === undefined ? "<td class='cell bad'>undefined</td>" : `<td class="cell ok">${v}</td>`; };
    $(host, "grid").innerHTML = `<table class="lab-table"><thead><tr><th>right glyph is …</th><th>order ${a}${b}</th><th>order ${b}${a}</th></tr></thead><tbody>${rels.map(([r, txt]) => `<tr><td>${txt}</td>${cell(`${a}${b}/${r}`)}${cell(`${b}${a}/${r}`)}</tr>`).join("")}</tbody></table><p class="lab-note">Columns change the horizontal order; rows change the vertical relation. When both change the value, the two channels are independent (NUM-DEF-031).</p>`;
    const n = Math.max(0, Math.min(3199999, Math.trunc(Number($(host, "m").value) || 0)));
    const lay = N.mayaLayout(n);
    $(host, "maya").textContent = lay.map((m) => `place ${m.place}  ${m.glyph.padEnd(8)}`).join("\n") + `\n\npure base 20:          ${N.mayaValue(lay)}\ncalendrical (1,20,360,…): ${N.mayaValue(lay, true)}\nSame marks, two semantics: the layout alone does not fix the value (NUM-NEG-005).`;
    const ai = "٠١٢٣٤٥٦٧٨٩", eai = "۰۱۲۳۴۵۶۷۸۹", n2 = String(n).slice(0, 6);
    const tr = (s, set) => [...s].map((c) => set[Number(c)]).join("");
    $(host, "bidi").innerHTML = `<table class="lab-table"><tbody>
      <tr><td>Arabic text, Arabic-Indic digits (bidi class AN)</td><td dir="rtl" lang="ar" style="font-size:1.3em">العدد ${tr(n2, ai)} هنا</td></tr>
      <tr><td>Arabic text, Extended Arabic-Indic digits (EN)</td><td dir="rtl" lang="fa" style="font-size:1.3em">العدد ${tr(n2, eai)} هنا</td></tr>
      <tr><td>Hebrew text, European digits (EN) — comparator</td><td dir="rtl" lang="he" style="font-size:1.3em">המספר ${n2} כאן</td></tr>
      <tr><td>Latin text, European digits — comparator</td><td dir="ltr" style="font-size:1.3em">the number ${n2} here</td></tr></tbody></table>
      <p class="lab-note">In every right-to-left row the digits keep their most-significant-first order and read left to right, while the words read right to left. The behaviour is the same for Hebrew with European digits: it is a property of the Unicode Bidirectional Algorithm (UAX #9), not of one script (NUM-HYP-003u, refuted). Rendering is your browser's.</p>`;
  };
  $(host, "go").addEventListener("click", run); ["a", "b", "m"].forEach((k) => $(host, k).addEventListener("change", run)); run();
};

// converse fiber explorer: profiles of b·c = a in Z/m and how classes move along Z/m → Z/k
WIDGETS["num-fibers"] = (host) => {
  host.innerHTML = `<div class="lab-row"><label>m <input data-k="m" type="number" value="12" min="1" max="40" style="width:5rem"></label><label>k (divides m) <input data-k="k" type="number" value="4" min="1" max="40" style="width:5rem"></label><button data-k="go">Reduce</button></div><div class="lab-out" data-k="out" aria-live="polite"></div>`;
  const run = () => {
    const m = Math.max(1, Math.min(40, Math.trunc(Number($(host, "m").value) || 1))), k = Math.max(1, Math.min(m, Math.trunc(Number($(host, "k").value) || 1)));
    if (m % k) { $(host, "out").textContent = `${k} does not divide ${m}: x ↦ x mod ${k} is not a ring homomorphism Z/${m} → Z/${k}.`; return; }
    const pm = N.profile(m), pk = N.profile(k), T = N.transfer(m, k), K = ["none", "unique", "many"];
    const lines = [`profile of b·c = a over all (a, b):   Z/${m}: none ${pm.none}, unique ${pm.unique}, many ${pm.many}    Z/${k}: none ${pk.none}, unique ${pk.unique}, many ${pk.many}`, "",
      `class in Z/${m} → class in Z/${k} (counts of pairs (a, b) of Z/${m}):`, "            " + K.map((t) => t.padStart(8)).join(""),
      ...K.map((s) => s.padEnd(12) + K.map((t) => String(T[s][t]).padStart(8)).join("")), "",
      `forbidden by the classical preservation theorem (NUM-HIST-001): unique → none = ${T.unique.none}, many → none = ${T.many.none}.`,
      `Other changes are allowed, and some occur here: a problem with no solution can gain one (3·c = 1 in Z/12 has none; in Z/4, c = 3), and many solutions can become one (3·c = 3).`];
    $(host, "out").textContent = lines.join("\n");
  };
  $(host, "go").addEventListener("click", run); ["m", "k"].forEach((x) => $(host, x).addEventListener("change", run)); run();
};
