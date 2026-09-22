import { chromium } from "file:///C:/Users/PRASAD/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";

const browser = await chromium.launch({ headless: true, executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto("http://127.0.0.1:4173/", { waitUntil: "networkidle" });
await page.locator("#systems").scrollIntoViewIfNeeded();
await page.waitForTimeout(1800);
const result = await page.evaluate(() => {
  const image = document.querySelector(".component-visual img");
  const figure = document.querySelector(".component-visual");
  const grid = document.querySelector(".component-scope-grid");
  const section = document.querySelector("#components");
  const pick = (element) => {
    const r = element.getBoundingClientRect();
    const c = getComputedStyle(element);
    return { width: r.width, height: r.height, minHeight: c.minHeight, aspectRatio: c.aspectRatio, position: c.position, paddingTop: c.paddingTop, paddingBottom: c.paddingBottom };
  };
  const systems = [...document.querySelectorAll(".system-visual img")].map((item) => ({
    src: item.currentSrc,
    complete: item.complete,
    naturalWidth: item.naturalWidth,
    naturalHeight: item.naturalHeight,
    opacity: getComputedStyle(item.closest("figure")).opacity,
    imageOpacity: getComputedStyle(item).opacity,
  }));
  return { image: pick(image), figure: pick(figure), grid: pick(grid), section: pick(section), systems };
});
console.log(JSON.stringify(result, null, 2));
await browser.close();
