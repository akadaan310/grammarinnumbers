// GIN-EXP-013 oracle: JavaScript BigInt and Number arithmetic (node).
import { createInterface } from "node:readline";
const mode = process.argv[2];
for await (const line of createInterface({ input: process.stdin })) {
  const [a, op, b] = line.trim().split(" ");
  try {
    const x = mode === "bigint" ? BigInt(a) : Number(a), y = mode === "bigint" ? BigInt(b) : Number(b);
    const r = op === "+" ? x + y : op === "-" ? x - y : op === "*" ? x * y : op === "/" ? x / y : x % y;
    console.log("value " + String(r));
  } catch (e) { console.log("exception " + e.name); }
}
