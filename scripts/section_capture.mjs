import { chromium } from "file:///C:/Users/PRASAD/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const browser = await chromium.launch({
  headless: true,
  executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
});
const output = path.resolve("qa-output");
await mkdir(output, { recursive: true });

for (const [label, width, height, selectors] of [
  ["desktop", 1440, 900, ["#components", "#systems", "#quality", "#why", "#rfq", "#contact"]],
  ["mobile", 390, 844, ["#capabilities", "#components", "#systems", "#why", "#rfq", "#contact"]],
]) {
  const context = await browser.newContext({ viewport: { width, height } });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });
  await page.waitForTimeout(400);
  for (const selector of selectors) {
    await page.evaluate((target) => {
      const element = document.querySelector(target);
      scrollTo(0, element.getBoundingClientRect().top + scrollY - 76);
    }, selector);
    await page.waitForTimeout(1600);
    await page.screenshot({ path: path.join(output, `${label}-${selector.slice(1)}.png`) });
  }
  await context.close();
}

await browser.close();
