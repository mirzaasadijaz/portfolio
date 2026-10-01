(() => {
  // --- NEW: Dark/Light Mode Toggle ---
  const themeToggle = document.getElementById('theme-toggle');
  const htmlElement = document.documentElement;

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      // Check current theme
      const currentTheme = htmlElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      // Apply new theme
      htmlElement.setAttribute('data-theme', newTheme);
      
      // Save user preference to localStorage so it remembers their choice
      localStorage.setItem('theme', newTheme);
    });
  }

  // --- EXISTING: Project filter ---
  const chips = document.querySelectorAll('.chips button');
  chips.forEach(b => b.addEventListener('click', () => {
    chips.forEach(o => o.setAttribute('aria-pressed', o === b));
    document.querySelectorAll('#pinned .item').forEach(i => {
      i.hidden = b.dataset.filter !== 'all' && !i.dataset.areas.split(' ').includes(b.dataset.filter);
    });
  }));

  // --- EXISTING: Current section in the nav ---
  const links = [...document.querySelectorAll('.bar nav a')];
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) links.forEach(a => a.toggleAttribute('aria-current', a.hash === '#' + e.target.id));
  }), { rootMargin: '-45% 0px -50% 0px' });
  links.forEach(a => { const s = document.querySelector(a.hash); if (s) io.observe(s); });

  // --- EXISTING: Hero canvas animation ---
  const cv = document.getElementById('field');
  if (!cv) return;
  const ctx = cv.getContext('2d'), still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const seeds = [[.14, .30], [.40, .18], [.30, .62], [.52, .46], [.66, .16]];
  let W, H, pts = [], mouse = null, live = true;
  const rnd = (a, b) => a + Math.random() * (b - a);

  function size() {
    const r = cv.getBoundingClientRect(), d = devicePixelRatio || 1;
    W = r.width; H = r.height; cv.width = W * d; cv.height = H * d; ctx.setTransform(d, 0, 0, d, 0, 0);
    pts = [];
    seeds.forEach((s, k) => { for (let i = 0; i < 26; i++) {
      const a = rnd(0, 6.283), rad = Math.abs(rnd(-1, 1) * rnd(20, 90));
      pts.push({ k, cx: s[0] * W, cy: s[1] * H, a, rad, sp: rnd(.0004, .0012), x: 0, y: 0 });
    } });
  }
  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    for (const p of pts) {
      const ang = p.a + t * p.sp;
      let x = p.cx + Math.cos(ang) * p.rad, y = p.cy + Math.sin(ang * 1.3) * p.rad * .7, hot = 0;
      if (mouse) {
        const dx = mouse.x - x, dy = mouse.y - y, d = Math.hypot(dx, dy);
        if (d < 170) { hot = 1 - d / 170; x += dx * hot * .35; y += dy * hot * .35; }
      }
      p.x = x; p.y = y;
      ctx.fillStyle = hot ? `rgba(143,155,255,${.45 + hot * .55})` : 'rgba(255,255,255,.28)';
      ctx.beginPath(); ctx.arc(x, y, hot ? 2.6 : 1.9, 0, 6.283); ctx.fill();
      if (hot > .25) { ctx.strokeStyle = `rgba(143,155,255,${hot * .5})`; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke(); }
    }
    ctx.strokeStyle = '#8f9bff'; ctx.lineWidth = 1.5;
    for (const s of seeds) { const x = s[0] * W, y = s[1] * H; ctx.beginPath(); ctx.moveTo(x - 6, y); ctx.lineTo(x + 6, y); ctx.moveTo(x, y - 6); ctx.lineTo(x, y + 6); ctx.stroke(); }
    ctx.lineWidth = 1;
  }
  function loop(t) { if (live && !document.hidden) draw(t); if (!still) requestAnimationFrame(loop); }

  size();
  addEventListener('resize', () => { size(); if (still) draw(0); });
  const hero = cv.parentElement;
  hero.addEventListener('pointermove', e => { const r = cv.getBoundingClientRect(); mouse = { x: e.clientX - r.left, y: e.clientY - r.top }; });
  hero.addEventListener('pointerleave', () => { mouse = null; });
  new IntersectionObserver(([e]) => { live = e.isIntersecting; }).observe(hero);
  still ? draw(0) : requestAnimationFrame(loop);
})();