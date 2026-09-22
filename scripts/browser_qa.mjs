import { chromium } from "file:///C:/Users/PRASAD/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const url = process.env.QA_URL || "http://127.0.0.1:4173/";
const output = path.resolve(process.env.QA_OUTPUT || "qa-output");
await mkdir(output, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
});
const viewports = [
  ["desktop-1920", 1920, 1080],
  ["desktop-1440", 1440, 900],
  ["tablet-1024", 1024, 768],
  ["mobile-430", 430, 932],
  ["mobile-390", 390, 844],
  ["mobile-375", 375, 812],
];

const report = [];

for (const [name, width, height] of viewports) {
  const context = await browser.newContext({ viewport: { width, height } });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("requestfailed", (request) => failedRequests.push(`${request.url()} :: ${request.failure()?.errorText}`));
  await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(500);

  const state = await page.evaluate(() => {
    const anchors = [...document.querySelectorAll('a[href^="#"]')]
      .map((link) => link.getAttribute("href"))
      .filter((href) => href && href.length > 1);
    const missingAnchors = [...new Set(anchors)].filter((href) => !document.querySelector(href));
    const images = [...document.images];
    const h1 = document.querySelector("h1")?.getBoundingClientRect();
    return {
      title: document.title,
      h1Visible: Boolean(h1 && h1.width > 0 && h1.height > 0),
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      missingAnchors,
      brokenImages: images.filter((image) => image.complete && image.naturalWidth === 0).map((image) => image.currentSrc || image.src),
      motionReady: document.documentElement.classList.contains("motion-ready"),
      processPinDisplay: getComputedStyle(document.querySelector("[data-process-pin]")).display,
      fallbackDisplay: getComputedStyle(document.querySelector(".process-fallback")).display,
      mainHeading: document.querySelector("h1")?.innerText.trim(),
    };
  });

  if (width <= 1080) {
    await page.click("[data-menu-button]");
    const opened = await page.getAttribute("[data-menu-button]", "aria-expanded");
    await page.keyboard.press("Escape");
    const closed = await page.getAttribute("[data-menu-button]", "aria-expanded");
    state.mobileMenu = { opened, closed };
  }

  if (name === "desktop-1440") {
    await page.locator("[data-process-scroll]").scrollIntoViewIfNeeded();
    const processTop = await page.evaluate(() => document.querySelector("[data-process-scroll]").getBoundingClientRect().top + scrollY);
    await page.evaluate(({ processTop, height }) => scrollTo(0, processTop + height * 3.1), { processTop, height });
    await page.waitForTimeout(900);
    state.processSample = await page.evaluate(() => ({
      readout: document.querySelector("[data-stage-readout]")?.textContent,
      activeStep: document.querySelector("[data-process-step].is-active")?.textContent.trim(),
      visibleScenes: [...document.querySelectorAll("[data-process-scene]")].filter((scene) => Number(getComputedStyle(scene).opacity) > 0.2).length,
      pinnedTop: Math.round(document.querySelector("[data-process-pin]").getBoundingClientRect().top),
    }));
    await page.screenshot({ path: path.join(output, "desktop-1440-process.png"), fullPage: false });

    await page.locator("#capabilities").scrollIntoViewIfNeeded();
    await page.focus("#capability-tab-0");
    await page.keyboard.press("ArrowDown");
    await page.waitForTimeout(250);
    state.capabilityKeyboard = await page.evaluate(() => ({
      selected: document.querySelector('[data-capability][aria-selected="true"]')?.id,
      title: document.querySelector("[data-capability-title]")?.textContent,
      image: document.querySelector("[data-capability-image]")?.getAttribute("src"),
    }));
    await page.screenshot({ path: path.join(output, "desktop-1440-capabilities.png"), fullPage: false });
  }

  if (name === "mobile-390") {
    const processTop = await page.evaluate(() => document.querySelector("[data-process-scroll]").getBoundingClientRect().top + scrollY);
    await page.evaluate(({ processTop, height }) => scrollTo(0, processTop + height * 2.6), { processTop, height });
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(output, "mobile-390-process.png"), fullPage: false });
    await page.locator("#quality").scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    state.mobileQuality = await page.evaluate(() => ({
      scrollY: Math.round(scrollY),
      qualityTop: Math.round(document.querySelector("#quality").getBoundingClientRect().top),
      visual: (() => { const r = document.querySelector(".quality-visual").getBoundingClientRect(); return { top: Math.round(r.top), bottom: Math.round(r.bottom) }; })(),
      copy: (() => { const r = document.querySelector(".quality-copy").getBoundingClientRect(); return { top: Math.round(r.top), bottom: Math.round(r.bottom) }; })(),
      steps: [...document.querySelectorAll(".quality-steps li")].map((item) => { const r = item.getBoundingClientRect(); const s = getComputedStyle(item); return { top: Math.round(r.top), bottom: Math.round(r.bottom), opacity: s.opacity, transform: s.transform }; }),
    }));
    await page.screenshot({ path: path.join(output, "mobile-390-quality.png"), fullPage: false });
  }

  const screenshotPath = path.join(output, `${name}-hero.png`);
  await page.evaluate(() => scrollTo(0, 0));
  await page.waitForTimeout(200);
  await page.screenshot({ path: screenshotPath, fullPage: false });
  report.push({ name, width, height, ...state, consoleErrors, pageErrors, failedRequests, screenshotPath });
  await context.close();
}

const reducedContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
const reducedPage = await reducedContext.newPage();
const reducedErrors = [];
reducedPage.on("pageerror", (error) => reducedErrors.push(error.message));
await reducedPage.goto(url, { waitUntil: "networkidle", timeout: 30000 });
await reducedPage.waitForTimeout(300);
const reduced = await reducedPage.evaluate(() => ({
  motionReady: document.documentElement.classList.contains("motion-ready"),
  processPinDisplay: getComputedStyle(document.querySelector("[data-process-pin]")).display,
  fallbackDisplay: getComputedStyle(document.querySelector(".process-fallback")).display,
  fallbackItems: document.querySelectorAll(".process-fallback > li").length,
  pageErrors: [],
}));
reduced.pageErrors = reducedErrors;
report.push({ name: "reduced-motion", ...reduced });
await reducedContext.close();

console.log(JSON.stringify(report, null, 2));
await browser.close();
