import { chromium } from "playwright";
import { createServer } from "node:http";
import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";

const repositoryRoot = process.cwd();
const output = path.resolve(process.env.QA_OUTPUT || "qa-output");
const viewportFilter = process.env.QA_VIEWPORT;
const mimeTypes = new Map([
  [".avif", "image/avif"],
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".ico", "image/x-icon"],
  [".jpg", "image/jpeg"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".png", "image/png"],
  [".svg", "image/svg+xml"],
  [".webp", "image/webp"],
]);

const viewports = [
  ["desktop-1920", 1920, 1080],
  ["desktop-1440", 1440, 900],
  ["desktop-1024", 1024, 768],
  ["boundary-780", 780, 900],
  ["tablet-768", 768, 1024],
  ["mobile-430", 430, 932],
  ["mobile-390", 390, 844],
  ["mobile-375", 375, 812],
].filter(([name]) => !viewportFilter || name === viewportFilter);

const report = [];
const assertions = [];
const failures = [];

function check(condition, name, detail = "") {
  const result = { name, passed: Boolean(condition), detail };
  assertions.push(result);
  if (!result.passed) failures.push(result);
}

function observePage(page) {
  const events = { consoleErrors: [], pageErrors: [], failedRequests: [] };
  page.on("console", (message) => {
    if (message.type() === "error") events.consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => events.pageErrors.push(error.message));
  page.on("requestfailed", (request) => {
    events.failedRequests.push(`${request.url()} :: ${request.failure()?.errorText || "unknown failure"}`);
  });
  return events;
}

async function startStaticServer() {
  const rootWithSeparator = `${path.resolve(repositoryRoot)}${path.sep}`.toLowerCase();
  const server = createServer(async (request, response) => {
    try {
      const requestUrl = new URL(request.url || "/", "http://127.0.0.1");
      const pathname = decodeURIComponent(requestUrl.pathname);
      const relativePath = pathname === "/" ? "index.html" : pathname.replace(/^\/+/, "");
      const filePath = path.resolve(repositoryRoot, relativePath);
      const normalizedPath = filePath.toLowerCase();

      if (normalizedPath !== path.resolve(repositoryRoot).toLowerCase() && !normalizedPath.startsWith(rootWithSeparator)) {
        response.writeHead(403).end("Forbidden");
        return;
      }

      const fileStat = await stat(filePath);
      if (!fileStat.isFile()) {
        response.writeHead(404).end("Not found");
        return;
      }

      const body = await readFile(filePath);
      response.writeHead(200, {
        "Content-Type": mimeTypes.get(path.extname(filePath).toLowerCase()) || "application/octet-stream",
        "Cache-Control": "no-store",
      });
      response.end(body);
    } catch (error) {
      response.writeHead(error?.code === "ENOENT" ? 404 : 500).end(error?.code === "ENOENT" ? "Not found" : "Server error");
    }
  });

  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });

  const address = server.address();
  return { server, url: `http://127.0.0.1:${address.port}/` };
}

async function waitForAllImages(page, { pollForCompletion = true } = {}) {
  await page.evaluate(() => {
    document.querySelectorAll('img[loading="lazy"]').forEach((image) => { image.loading = "eager"; });
  });
  const dimensions = await page.evaluate(() => ({
    height: document.documentElement.scrollHeight,
    step: Math.max(320, Math.floor(innerHeight * 0.75)),
  }));
  for (let top = 0; top < dimensions.height; top += dimensions.step) {
    await page.evaluate((position) => scrollTo(0, position), top);
    await page.waitForTimeout(24);
  }
  await page.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
  await page.waitForTimeout(120);
  if (pollForCompletion) {
    await page.waitForFunction(
      () => [...document.images].every((image) => image.complete),
      undefined,
      { timeout: 5000 },
    ).catch(() => {});
  } else {
    await page.waitForTimeout(750);
  }
  await page.evaluate(() => scrollTo(0, 0));
  await page.waitForTimeout(150);
}

async function verifyDeclaredImageAssets(page) {
  const imageUrls = await page.evaluate(() => {
    const urls = [...document.querySelectorAll("img[src]")].map((image) => image.src);
    document.querySelectorAll("source[srcset]").forEach((source) => {
      source.srcset.split(",").forEach((candidate) => {
        const asset = candidate.trim().split(/\s+/)[0];
        if (asset) urls.push(new URL(asset, document.baseURI).href);
      });
    });
    return [...new Set(urls)];
  });
  const failures = [];
  for (const imageUrl of imageUrls) {
    try {
      const response = await page.request.get(imageUrl);
      const contentType = response.headers()["content-type"] || "";
      if (!response.ok() || !contentType.startsWith("image/")) {
        failures.push(`${imageUrl} (${response.status()} ${contentType || "no content type"})`);
      }
    } catch (error) {
      failures.push(`${imageUrl} (${error.message})`);
    }
  }
  return failures;
}

async function inspectPage(page, options) {
  await waitForAllImages(page, options);
  return page.evaluate(() => {
    const visible = (element) => {
      if (!element) return false;
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
    };
    const anchors = [...document.querySelectorAll('a[href^="#"]')]
      .map((link) => link.getAttribute("href"))
      .filter((href) => href && href.length > 1);
    const missingAnchors = [...new Set(anchors)].filter((href) => {
      try {
        return !document.getElementById(decodeURIComponent(href.slice(1)));
      } catch {
        return true;
      }
    });
    const interactiveSelector = [
      "a[href]",
      "area[href]",
      "button",
      "input:not([type=hidden])",
      "select",
      "textarea",
      "iframe",
      "audio[controls]",
      "video[controls]",
      "summary",
      "[contenteditable]:not([contenteditable=false])",
      "[tabindex]",
    ].join(",");
    const hiddenInteractive = [...document.querySelectorAll('[aria-hidden="true"]')]
      .flatMap((container) => [...container.querySelectorAll(interactiveSelector)])
      .filter((element, index, all) => all.indexOf(element) === index)
      .map((element) => `${element.tagName.toLowerCase()}${element.id ? `#${element.id}` : ""}${element.getAttribute("href") ? `[href="${element.getAttribute("href")}"]` : ""}`);
    const images = [...document.images];
    const fallback = document.querySelector(".process-fallback");
    const fallbackItems = [...document.querySelectorAll(".process-fallback > li")];
    const h1 = document.querySelector("h1");
    const primaryCta = document.querySelector(".hero .button-primary");
    const resources = performance.getEntriesByType("resource");

    return {
      title: document.title,
      h1Visible: visible(h1),
      primaryCtaVisible: visible(primaryCta) && primaryCta.getBoundingClientRect().width >= 44 && primaryCta.getBoundingClientRect().height >= 44,
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      missingAnchors,
      brokenImages: images.filter((image) => visible(image) && (!image.complete || image.naturalWidth === 0)).map((image) => image.currentSrc || image.src),
      hiddenInteractive,
      gsapAvailable: Boolean(window.gsap),
      scrollTriggerAvailable: Boolean(window.ScrollTrigger),
      motionReady: document.documentElement.classList.contains("motion-ready"),
      cinematicReady: document.documentElement.classList.contains("process-cinematic-ready"),
      processPinDisplay: getComputedStyle(document.querySelector("[data-process-pin]")).display,
      fallbackDisplay: getComputedStyle(fallback).display,
      fallbackVisible: visible(fallback),
      fallbackItems: fallbackItems.length,
      visibleFallbackItems: fallbackItems.filter(visible).length,
      bodyFontFamily: getComputedStyle(document.body).fontFamily,
      displayFontFamily: getComputedStyle(document.querySelector(".brand")).fontFamily,
      loadedResources: resources.length,
      encodedResourceBytes: Math.round(resources.reduce((sum, item) => sum + (item.encodedBodySize || 0), 0)),
    };
  });
}

function assertSharedState(name, state, events) {
  check(state.h1Visible, `${name}: main heading is visible`);
  check(state.primaryCtaVisible, `${name}: primary CTA meets the visible 44px target`);
  check(!state.horizontalOverflow, `${name}: no horizontal overflow`, `${state.scrollWidth}/${state.clientWidth}`);
  check(state.missingAnchors.length === 0, `${name}: all internal anchors resolve`, state.missingAnchors.join(", "));
  const imageFailures = [...state.brokenImages, ...state.imageAssetFailures];
  check(imageFailures.length === 0, `${name}: all visible and declared images load`, imageFailures.join(", "));
  check(state.hiddenInteractive.length === 0, `${name}: aria-hidden subtrees contain no interactive descendants`, state.hiddenInteractive.join(", "));
  check(events.consoleErrors.length === 0, `${name}: no console errors`, events.consoleErrors.join(" | "));
  check(events.pageErrors.length === 0, `${name}: no page errors`, events.pageErrors.join(" | "));
  check(events.failedRequests.length === 0, `${name}: no failed requests`, events.failedRequests.join(" | "));
}

await mkdir(output, { recursive: true });
const stylesSource = await readFile(path.join(repositoryRoot, "styles.css"), "utf8");
check(!/\b(?:Archivo|Inter)\b/i.test(stylesSource), "typography: no legacy Archivo or Inter declarations remain");
check(stylesSource.includes("--font-display:") && stylesSource.includes("--font-body:"), "typography: display and body tokens are defined");

let localServer;
let browser;

try {
  const target = process.env.QA_URL ? { url: process.env.QA_URL } : await startStaticServer();
  localServer = target.server;
  browser = await chromium.launch({ headless: true });

  for (const [name, width, height] of viewports) {
    console.log(`Running ${name} (${width}x${height})...`);
    const context = await browser.newContext({ viewport: { width, height } });
    const page = await context.newPage();
    const events = observePage(page);
    await page.goto(target.url, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(250);
    const state = await inspectPage(page);
    state.imageAssetFailures = await verifyDeclaredImageAssets(page);

    check(state.gsapAvailable && state.scrollTriggerAvailable, `${name}: local GSAP and ScrollTrigger are available`);
    if (width > 780) {
      check(state.cinematicReady, `${name}: manufacturing cinematic is active`);
      check(state.processPinDisplay !== "none", `${name}: cinematic pin is displayed`);
      check(!state.fallbackVisible, `${name}: stacked fallback is hidden while the cinematic is active`);
    } else {
      check(!state.cinematicReady, `${name}: manufacturing cinematic is disabled at 780px and below`);
      check(state.processPinDisplay === "none", `${name}: cinematic pin is hidden at 780px and below`);
      check(state.fallbackVisible && state.fallbackItems === 8 && state.visibleFallbackItems === 8, `${name}: complete stacked route is visible`, `${state.visibleFallbackItems}/${state.fallbackItems}`);
    }

    if (width <= 1080) {
      await page.focus("[data-menu-button]");
      await page.keyboard.press("Enter");
      const opened = await page.getAttribute("[data-menu-button]", "aria-expanded");
      await page.keyboard.press("Tab");
      const focusMovedIntoMenu = await page.evaluate(() => Boolean(document.activeElement?.closest("[data-menu]")));
      await page.keyboard.press("Escape");
      const closed = await page.getAttribute("[data-menu-button]", "aria-expanded");
      const focusReturned = await page.evaluate(() => document.activeElement?.hasAttribute("data-menu-button"));
      state.mobileMenuKeyboard = { opened, focusMovedIntoMenu, closed, focusReturned };
      check(opened === "true" && focusMovedIntoMenu && closed === "false" && focusReturned, `${name}: mobile menu works with keyboard only`, JSON.stringify(state.mobileMenuKeyboard));
    }

    if (name === "desktop-1440") {
      await page.evaluate(() => document.activeElement?.blur());
      await page.keyboard.press("Tab");
      state.keyboardFocus = await page.evaluate(() => {
        const element = document.activeElement;
        const style = getComputedStyle(element);
        return { text: element?.textContent?.trim(), outlineWidth: style.outlineWidth, outlineStyle: style.outlineStyle };
      });
      check(state.keyboardFocus.outlineStyle !== "none" && state.keyboardFocus.outlineWidth !== "0px", `${name}: keyboard focus is visibly styled`, JSON.stringify(state.keyboardFocus));
      await page.evaluate(() => document.activeElement?.blur());

      const processTop = await page.evaluate(() => document.querySelector("[data-process-scroll]").getBoundingClientRect().top + scrollY);
      await page.evaluate(({ top, viewportHeight }) => scrollTo(0, top + viewportHeight * 3.1), { top: processTop, viewportHeight: height });
      await page.waitForTimeout(500);
      state.processSample = await page.evaluate(() => ({
        readout: document.querySelector("[data-stage-readout]")?.textContent,
        activeStep: document.querySelector("[data-process-step].is-active")?.textContent.trim(),
        visibleScenes: [...document.querySelectorAll("[data-process-scene]")].filter((scene) => Number(getComputedStyle(scene).opacity) > 0.2).length,
        pinnedTop: Math.round(document.querySelector("[data-process-pin]").getBoundingClientRect().top),
      }));
      check(Boolean(state.processSample.readout && state.processSample.activeStep) && state.processSample.visibleScenes >= 1, `${name}: cinematic stage status advances`, JSON.stringify(state.processSample));
      await page.screenshot({ path: path.join(output, "desktop-1440-process.png"), fullPage: false });

      await page.locator("#capabilities").scrollIntoViewIfNeeded();
      await page.focus("#capability-tab-0");
      await page.keyboard.press("ArrowDown");
      await page.waitForTimeout(180);
      state.capabilityKeyboard = await page.evaluate(() => ({
        selected: document.querySelector('[data-capability][aria-selected="true"]')?.id,
        title: document.querySelector("[data-capability-title]")?.textContent,
        image: document.querySelector("[data-capability-image]")?.getAttribute("src"),
      }));
      check(state.capabilityKeyboard.selected === "capability-tab-1", `${name}: capability tabs respond to keyboard navigation`, JSON.stringify(state.capabilityKeyboard));
      await page.screenshot({ path: path.join(output, "desktop-1440-capabilities.png"), fullPage: false });
    }

    if (name === "mobile-390") {
      const stageTop = await page.evaluate(() => {
        const stage = document.querySelectorAll(".process-fallback > li")[3];
        return stage.getBoundingClientRect().top + scrollY;
      });
      await page.evaluate((top) => scrollTo(0, top - 68), stageTop);
      await page.waitForTimeout(250);
      await page.screenshot({ path: path.join(output, "mobile-390-process.png"), fullPage: false });
    }

    await page.evaluate(() => scrollTo(0, 0));
    await page.waitForTimeout(100);
    const screenshotPath = path.join(output, `${name}-hero.png`);
    await page.screenshot({ path: screenshotPath, fullPage: false });

    assertSharedState(name, state, events);
    report.push({ name, width, height, ...state, ...events, screenshotPath });
    await context.close();
    console.log(`Completed ${name}.`);
  }

  console.log("Running reduced-motion...");
  const reducedContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
  const reducedPage = await reducedContext.newPage();
  const reducedEvents = observePage(reducedPage);
  await reducedPage.goto(target.url, { waitUntil: "networkidle", timeout: 30000 });
  const reduced = await inspectPage(reducedPage);
  reduced.imageAssetFailures = await verifyDeclaredImageAssets(reducedPage);
  check(!reduced.motionReady && !reduced.cinematicReady, "reduced-motion: cinematic enhancement is disabled");
  check(reduced.processPinDisplay === "none", "reduced-motion: cinematic pin is hidden");
  check(reduced.fallbackVisible && reduced.fallbackItems === 8 && reduced.visibleFallbackItems === 8, "reduced-motion: complete stacked route is visible", `${reduced.visibleFallbackItems}/${reduced.fallbackItems}`);
  assertSharedState("reduced-motion", reduced, reducedEvents);
  report.push({ name: "reduced-motion", ...reduced, ...reducedEvents });
  await reducedContext.close();
  console.log("Completed reduced-motion.");

  console.log("Running no-javascript...");
  const noJsContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, javaScriptEnabled: false });
  const noJsPage = await noJsContext.newPage();
  const noJsEvents = observePage(noJsPage);
  await noJsPage.goto(target.url, { waitUntil: "networkidle", timeout: 30000 });
  const noJs = await inspectPage(noJsPage, { pollForCompletion: false });
  noJs.imageAssetFailures = await verifyDeclaredImageAssets(noJsPage);
  check(!noJs.cinematicReady, "no-javascript: cinematic enhancement is inactive");
  check(noJs.processPinDisplay === "none", "no-javascript: cinematic pin is hidden");
  check(noJs.fallbackVisible && noJs.fallbackItems === 8 && noJs.visibleFallbackItems === 8, "no-javascript: complete eight-stage route is visible", `${noJs.visibleFallbackItems}/${noJs.fallbackItems}`);
  assertSharedState("no-javascript", noJs, noJsEvents);
  report.push({ name: "no-javascript", ...noJs, ...noJsEvents });
  await noJsContext.close();
  console.log("Completed no-javascript.");

  const result = {
    generatedAt: new Date().toISOString(),
    target: target.url,
    scenarios: report,
    assertions,
    passed: failures.length === 0,
  };
  await writeFile(path.join(output, "report.json"), `${JSON.stringify(result, null, 2)}\n`, "utf8");

  console.log(`Browser QA ${result.passed ? "passed" : "failed"}: ${assertions.length - failures.length}/${assertions.length} assertions passed across ${report.length} scenarios.`);
  console.log(`Detailed report: ${path.join(output, "report.json")}`);
  if (failures.length) {
    failures.forEach((failure) => console.error(`FAIL: ${failure.name}${failure.detail ? ` — ${failure.detail}` : ""}`));
    process.exitCode = 1;
  }
} finally {
  await browser?.close();
  if (localServer) await new Promise((resolve, reject) => localServer.close((error) => error ? reject(error) : resolve()));
}
