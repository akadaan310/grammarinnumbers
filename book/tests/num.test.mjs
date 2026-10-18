// The research lane's browser port (num-core.js) must reproduce its Python library
// (research/the-number/numlab) on the fixtures exported by tools/export_data.py.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
await import("../site/assets/js/num-core.js");
const NUM = globalThis.NUM;
const fx = JSON.parse(fs.readFileSync(new URL("../data/num_fixtures.json", import.meta.url), "utf8"));

test("canonical words of every numeration system", () => {
  const bad = fx.encode.filter((f) => NUM.encode(f.s, f.n) !== f.w).map((f) => `${f.s} ${f.n}: ${NUM.encode(f.s, f.n)} vs ${f.w}`);
  assert.equal(bad.length, 0, bad.slice(0, 20).join("\n"));
});

test("converse profiles of multiplication in Z/n", () => {
  for (const [n, p] of Object.entries(fx.profiles)) assert.deepEqual(NUM.profile(Number(n)), p, `Z/${n}`);
});

test("class transfer along reductions Z/m -> Z/k", () => {
  for (const [key, mat] of Object.entries(fx.transfer)) {
    const [m, k] = key.split("->").map(Number);
    assert.deepEqual(NUM.transfer(m, k), mat, key);
  }
});

test("two-channel layout grammar", () => {
  for (const [ab, table] of Object.entries(fx.channels)) assert.deepEqual(NUM.channelTable(ab[0], ab[1]), table, ab);
});

test("Maya-style layouts and their two readings", () => {
  for (const f of fx.maya) {
    const lay = NUM.mayaLayout(f.n);
    assert.deepEqual(lay.map((m) => m.glyph), f.glyphs, String(f.n));
    assert.equal(NUM.mayaValue(lay), f.n);
    assert.equal(NUM.mayaValue(lay, true), f.cal, String(f.n));
  }
});
