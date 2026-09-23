(() => {
  const header = document.querySelector('[data-header]');
  const menuButton = document.querySelector('[data-menu-button]');
  const menu = document.querySelector('[data-menu]');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const closeMenu = (returnFocus = false) => {
    if (!menuButton || !menu) return;
    menuButton.setAttribute('aria-expanded', 'false');
    menu.classList.remove('is-open');
    if (returnFocus) menuButton.focus();
  };

  menuButton?.addEventListener('click', () => {
    const willOpen = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(willOpen));
    menu?.classList.toggle('is-open', willOpen);
  });

  menu?.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton?.getAttribute('aria-expanded') === 'true') {
      closeMenu(true);
    }
  });

  document.addEventListener('click', (event) => {
    if (!menu?.classList.contains('is-open')) return;
    if (!menu.contains(event.target) && !menuButton?.contains(event.target)) closeMenu();
  });

  const updateHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 24);
  updateHeader();
  addEventListener('scroll', updateHeader, { passive: true });

  const capabilityTabs = [...document.querySelectorAll('[data-capability]')];
  const capabilityMedia = document.querySelector('.capability-media');
  const capabilityAvif = document.querySelector('[data-capability-avif]');
  const capabilityWebp = document.querySelector('[data-capability-webp]');
  const capabilityImage = document.querySelector('[data-capability-image]');
  const capabilityKicker = document.querySelector('[data-capability-kicker]');
  const capabilityTitle = document.querySelector('[data-capability-title]');
  const capabilityCopy = document.querySelector('[data-capability-copy]');
  let capabilityTimer;

  const setCapability = (tab, focus = false) => {
    if (!tab || tab.getAttribute('aria-selected') === 'true') {
      if (focus) tab?.focus();
      return;
    }

    capabilityTabs.forEach((candidate) => {
      const active = candidate === tab;
      candidate.setAttribute('aria-selected', String(active));
      candidate.tabIndex = active ? 0 : -1;
    });

    capabilityMedia?.classList.add('is-changing');
    clearTimeout(capabilityTimer);
    capabilityTimer = setTimeout(() => {
      const base = tab.dataset.base;
      const directImage = tab.dataset.image || '';
      const [width, height] = (tab.dataset.ratio || '1536 1024').split(' ');
      if (capabilityAvif) capabilityAvif.srcset = directImage || `assets/${base}-960.avif 960w, assets/${base}-1536.avif 1536w`;
      if (capabilityWebp) capabilityWebp.srcset = directImage || `assets/${base}-960.webp 960w, assets/${base}-1536.webp 1536w`;
      if (capabilityImage) {
        capabilityImage.src = directImage || `assets/${base}-1536.webp`;
        capabilityImage.alt = tab.dataset.alt || '';
        capabilityImage.width = Number(width);
        capabilityImage.height = Number(height);
      }
      if (capabilityKicker) capabilityKicker.textContent = tab.dataset.kicker || '';
      if (capabilityTitle) capabilityTitle.textContent = tab.dataset.title || '';
      if (capabilityCopy) capabilityCopy.textContent = tab.dataset.copy || '';
      capabilityMedia?.setAttribute('aria-labelledby', tab.id);
      requestAnimationFrame(() => capabilityMedia?.classList.remove('is-changing'));
    }, reducedMotion ? 0 : 135);

    if (focus) tab.focus();
  };

  capabilityTabs.forEach((tab, index) => {
    tab.addEventListener('click', () => setCapability(tab));
    tab.addEventListener('focus', () => setCapability(tab));
    tab.addEventListener('pointerenter', (event) => {
      if (event.pointerType === 'mouse') setCapability(tab);
    });
    tab.addEventListener('keydown', (event) => {
      const keys = ['ArrowDown', 'ArrowRight', 'ArrowUp', 'ArrowLeft', 'Home', 'End'];
      if (!keys.includes(event.key)) return;
      event.preventDefault();
      let nextIndex = index;
      if (event.key === 'ArrowDown' || event.key === 'ArrowRight') nextIndex = (index + 1) % capabilityTabs.length;
      if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') nextIndex = (index - 1 + capabilityTabs.length) % capabilityTabs.length;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = capabilityTabs.length - 1;
      setCapability(capabilityTabs[nextIndex], true);
    });
  });

  if (reducedMotion || !window.gsap || !window.ScrollTrigger) return;

  const { gsap } = window;
  gsap.registerPlugin(window.ScrollTrigger);
  document.documentElement.classList.add('motion-ready');

  const processScroll = document.querySelector('[data-process-scroll]');
  const processPin = document.querySelector('[data-process-pin]');
  const scenes = gsap.utils.toArray('[data-process-scene]');
  const captions = gsap.utils.toArray('[data-process-caption]');
  const steps = [...document.querySelectorAll('[data-process-step]')];
  const progressFill = document.querySelector('[data-process-fill]');
  const progressCursor = document.querySelector('[data-process-cursor]');
  const stageLive = document.querySelector('[data-stage-live]');
  const stageReadout = document.querySelector('[data-stage-readout]');
  const aperture = document.querySelector('[data-process-aperture]');
  const partCarrier = document.querySelector('[data-part-carrier]');
  const partStates = gsap.utils.toArray('[data-part-state]');
  const partScan = document.querySelector('[data-part-scan]');
  const measureLines = gsap.utils.toArray('[data-measure-line]');
  const stageNames = [
    'Enquiry received',
    'Technical review',
    'Quotation',
    'Approval and optional design',
    'Raw material',
    'Cut to size',
    'CNC and VMC machining',
    'In-process check',
    'Quality inspection',
    'Packing',
    'Supply'
  ];

  if (processScroll && processPin && scenes.length === 11 && captions.length === 11 && partStates.length === 6) {
    gsap.set(scenes, { autoAlpha: 0, scale: 1.035, clipPath: 'inset(0% 0% 0% 0%)' });
    gsap.set(scenes[0], { autoAlpha: 1, scale: 1.015 });
    gsap.set(captions, { autoAlpha: 0, y: 30 });
    gsap.set(captions[0], { autoAlpha: 1, y: 0 });
    gsap.set(partStates, { autoAlpha: 0, scale: 0.92, rotate: -1.5 });
    gsap.set(partStates[0], { autoAlpha: 1, scale: 1, rotate: 0 });
    gsap.set(partScan, { yPercent: -120, autoAlpha: 0 });
    gsap.set(measureLines, { scaleX: 0 });

    let activeStage = 0;
    const updateStage = (nextStage) => {
      if (nextStage === activeStage) return;
      activeStage = nextStage;
      const padded = String(nextStage).padStart(2, '0');
      if (stageLive) stageLive.textContent = `Stage ${padded} of 10: ${stageNames[nextStage]}.`;
      if (stageReadout) stageReadout.textContent = `Stage ${padded} / 10`;
      steps.forEach((step, index) => {
        step.classList.toggle('is-active', index === nextStage);
        step.classList.toggle('is-complete', index < nextStage);
      });
    };

    const masks = [
      'inset(0% 0% 0% 100%)',
      'inset(0% 100% 0% 0%)',
      'inset(0% 0% 100% 0%)',
      'inset(0% 0% 0% 100%)',
      'inset(100% 0% 0% 0%)',
      'inset(0% 100% 0% 0%)',
      'inset(0% 0% 100% 0%)',
      'inset(100% 0% 0% 0%)',
      'inset(0% 100% 0% 0%)',
      'inset(0% 0% 0% 100%)'
    ];

    const isCompact = matchMedia('(max-width: 780px)').matches;
    const journey = gsap.timeline({
      defaults: { ease: 'none' },
      scrollTrigger: {
        trigger: processScroll,
        start: 'top top',
        end: () => `+=${Math.max(innerHeight * (isCompact ? 5.1 : 6.8), isCompact ? 3300 : 4700)}`,
        pin: processPin,
        pinSpacing: true,
        scrub: isCompact ? 0.36 : 0.7,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onUpdate: (self) => updateStage(Math.min(10, Math.floor(self.progress * 11)))
      }
    });

    journey.to(scenes[0], { scale: 1.065, duration: 0.72 }, 0);
    journey.to(progressFill, { scaleX: 1, duration: 10.72 }, 0);
    journey.to(progressCursor, { left: '100%', duration: 10.72 }, 0);

    for (let index = 1; index < scenes.length; index += 1) {
      const at = index;
      journey
        .to(captions[index - 1], { autoAlpha: 0, y: -24, duration: 0.3 }, at - 0.38)
        .to(scenes[index - 1], { autoAlpha: 0.13, scale: 0.985, duration: 0.66 }, at - 0.46)
        .fromTo(
          scenes[index],
          { autoAlpha: 0, scale: index === 8 ? 1.025 : 1.07, clipPath: masks[index - 1] },
          { autoAlpha: 1, scale: index === 8 ? 1.008 : 1.018, clipPath: 'inset(0% 0% 0% 0%)', duration: index === 8 ? 0.92 : 0.74 },
          at - 0.42
        )
        .fromTo(
          captions[index],
          { autoAlpha: 0, y: 30 },
          { autoAlpha: 1, y: 0, duration: index === 8 ? 0.52 : 0.36, ease: 'power2.out' },
          at - 0.34
        )
        .set(scenes[index - 1], { autoAlpha: 0 }, at + 0.22)
        .fromTo(aperture, { scaleY: 0, left: index % 2 ? '34%' : '66%' }, { scaleY: 1, duration: 0.12 }, at - 0.43)
        .to(aperture, { scaleY: 0, duration: 0.16 }, at - 0.05);
    }

    const partChanges = [
      { at: 3.62, from: 0, to: 1 },
      { at: 4.62, from: 1, to: 2 },
      { at: 5.62, from: 2, to: 3 },
      { at: 6.62, from: 3, to: 4 },
      { at: 8.62, from: 4, to: 5 }
    ];

    partChanges.forEach(({ at, from, to }) => {
      journey
        .to(partStates[from], { autoAlpha: 0, scale: 0.88, rotate: 1.2, duration: 0.34 }, at)
        .fromTo(partStates[to], { autoAlpha: 0, scale: 1.1, rotate: -1.2 }, { autoAlpha: 1, scale: 1, rotate: 0, duration: 0.52, ease: 'power2.out' }, at + 0.08);
    });

    journey
      .fromTo(partCarrier, { xPercent: 4 }, { xPercent: -4, duration: 10.72 }, 0)
      .to(partScan, { autoAlpha: 0.78, duration: 0.08 }, 0.4)
      .to(partScan, { yPercent: 120, duration: 2.1 }, 0.45)
      .to(partScan, { autoAlpha: 0, duration: 0.14 }, 2.48)
      .to(measureLines[0], { scaleX: 1, duration: 0.4, ease: 'power1.inOut' }, 6.82)
      .to(measureLines[1], { scaleX: 1, duration: 0.36, ease: 'power1.inOut' }, 7.02)
      .to(measureLines, { autoAlpha: 0, duration: 0.28 }, 8.46)
      .to(scenes[10], { scale: 1, duration: 0.54 }, 10.18);

    const heroMotion = gsap.timeline({
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 0.7 }
    });
    heroMotion
      .to('[data-hero-image]', { yPercent: 5, scale: 1.045, ease: 'none' }, 0)
      .to('[data-hero-copy]', { y: -42, autoAlpha: 0.62, ease: 'none' }, 0);

    gsap.from('.process-intro > *', {
      autoAlpha: 0,
      y: 34,
      duration: 0.82,
      stagger: 0.12,
      ease: 'power2.out',
      scrollTrigger: { trigger: '.process-intro', start: 'top 76%', once: true }
    });

    window.ScrollTrigger.batch('.reveal-item', {
      start: 'top 89%',
      once: true,
      onEnter: (items) => gsap.from(items, {
        y: 24,
        duration: 0.68,
        stagger: 0.075,
        ease: 'power2.out',
        overwrite: true
      })
    });

    addEventListener('load', () => window.ScrollTrigger.refresh(), { once: true });
  }
})();
