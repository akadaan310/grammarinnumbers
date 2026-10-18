// The laboratory's reference core must reproduce the Python SDK exactly on the
// fixture set exported by tools/export_data.py (GIN-D-015).
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
await import("../site/assets/js/gin-core.js");   // a classic browser script: it defines globalThis.GIN
const GIN = globalThis.GIN;
const fx = JSON.parse(fs.readFileSync(new URL("../data/lab_fixtures.json", import.meta.url), "utf8"));

test("every fixture outcome: status, layer, displayed value, IEEE flags", () => {
  const bad = [];
  for (const f of fx.outcomes) {
    const o = GIN.evaluate(f.e, f.d);
    const got = { status: o.status, layer: o.layer, display: ["value", "special"].includes(o.status) ? o.display : "", flags: o.flags };
    const exp = { status: f.status, layer: f.layer, display: f.display, flags: f.flags };
    if (JSON.stringify(got) !== JSON.stringify(exp)) bad.push(`${f.e} in ${f.d}: expected ${JSON.stringify(exp)} got ${JSON.stringify(got)}`);
  }
  assert.equal(bad.length, 0, `${bad.length}/${fx.outcomes.length} mismatches:\n${bad.slice(0, 40).join("\n")}`);
});

test("machine-versus-mathematics relations agree with ginsdk.contracts.inspect", () => {
  const bad = [];
  for (const f of fx.relations) {
    const r = GIN.relation(f.e, f.d);
    if (r.kind !== f.relation || r.math !== f.math) bad.push(`${f.e} in ${f.d}: expected ${f.relation}/${f.math} got ${r.kind}/${r.math}`);
  }
  assert.equal(bad.length, 0, bad.join("\n"));
});

test("exact rounding: binary64 agrees with the host's IEEE arithmetic on random operands", () => {
  let seed = 754;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  const F = GIN.FORMATS.binary64;
  const toQ = (x) => { const [v] = GIN.roundExact(F, decimalQ(x)); return v; };
  function decimalQ(x) { // exact rational of a JS number
    const buf = new DataView(new ArrayBuffer(8)); buf.setFloat64(0, x);
    const hi = buf.getUint32(0), lo = buf.getUint32(4);
    const sign = hi >>> 31, e = (hi >>> 20) & 0x7ff, m = (BigInt(hi & 0xfffff) << 32n) | BigInt(lo);
    const mant = e ? m | (1n << 52n) : m, ex = (e ? e : 1) - 1075;
    let q = ex >= 0 ? new GIN.Q(mant << BigInt(ex)) : new GIN.Q(mant, 1n << BigInt(-ex));
    return sign ? q.neg() : q;
  }
  let n = 0;
  for (let i = 0; i < 2000; i++) {
    const a = (rnd() - 0.5) * 10 ** Math.floor(rnd() * 40 - 20), b = (rnd() - 0.5) * 10 ** Math.floor(rnd() * 40 - 20);
    for (const op of ["+", "-", "*", "/"]) {
      const host = op === "+" ? a + b : op === "-" ? a - b : op === "*" ? a * b : a / b;
      const exact = op === "+" ? decimalQ(a).add(decimalQ(b)) : op === "-" ? decimalQ(a).sub(decimalQ(b)) : op === "*" ? decimalQ(a).mul(decimalQ(b)) : decimalQ(a).div(decimalQ(b));
      const [v] = GIN.roundExact(F, exact);
      assert.ok(v.cls === "finite" && decimalQ(host).eq(v.sign ? v.mag.neg() : v.mag), `${a} ${op} ${b}`);
      n++;
    }
  }
  assert.ok(n === 8000 && toQ(0.1));
});

test("Python repr and IEEE display formats", () => {
  assert.equal(GIN.evaluate("0.1 + 0.2", "binary64").display, "0.30000000000000004");
  assert.equal(GIN.evaluate("1 / 3", "Python").display, "0.3333333333333333");
  assert.equal(GIN.evaluate("9007199254740992 + 1", "binary64").display, "9007199254740992");
  assert.equal(GIN.evaluate("1 / 0", "binary64").display, "Infinity");
  assert.equal(GIN.evaluate("2 ^ 60 * 2 ^ 60", "binary64").status, "unsupported");
  assert.equal(GIN.evaluate("1152921504606846976 * 1152921504606846976", "binary64").display, "1.329227995784916e36");
  assert.equal(GIN.evaluate("0 / 0", "binary64").status, "special");
});
