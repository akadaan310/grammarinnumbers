// Screenshot pages of dist/ for visual inspection:  node tools/screenshot.mjs out-dir page.html[#sel] ...
import { chromium } from "playwright-core";
import { serve } from "./serve.mjs";
const [out, ...pages] = process.argv.slice(2);
const srv = await serve(0);
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
for (const [i, p] of pages.entries()) {
  const [url, w] = p.split("@");
  const page = await browser.newPage({ viewport: { width: Number(w || 1280), height: 900 } });
  const errs = []; page.on("pageerror", (e) => errs.push(e.message)); page.on("console", (m) => m.type() === "error" && errs.push(m.text()));
  await page.goto(`http://127.0.0.1:${srv.address().port}/${url}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${out}/shot-${i}.png`, fullPage: false });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  console.log(url, w || 1280, errs.length ? "ERRORS: " + errs.join(" | ") : "no console errors", overflow ? "HORIZONTAL OVERFLOW" : "");
  await page.close();
}
await browser.close(); srv.close();
