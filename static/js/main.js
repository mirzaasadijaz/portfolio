/* ══════════════════════════════════════
   NEURAL NETWORK CANVAS
══════════════════════════════════════ */
class NeuralNet {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext('2d');
    this.nodes  = [];
    this.pkts   = [];           // data packets flying along edges
    this.mouse  = { x: null, y: null };
    this.COUNT  = 70;
    this.DIST   = 160;
    this.raf    = null;

    this.resize();
    this.build();
    this.run();

    window.addEventListener('resize', () => this.resize());
    canvas.addEventListener('mousemove', e => {
      const r = canvas.getBoundingClientRect();
      this.mouse.x = e.clientX - r.left;
      this.mouse.y = e.clientY - r.top;
    });
    canvas.addEventListener('mouseleave', () => {
      this.mouse.x = null;
      this.mouse.y = null;
    });
  }

  resize() {
    this.canvas.width  = this.canvas.offsetWidth;
    this.canvas.height = this.canvas.offsetHeight;
  }

  build() {
    this.nodes = [];
    for (let i = 0; i < this.COUNT; i++) {
      this.nodes.push({
        x:  Math.random() * this.canvas.width,
        y:  Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        r:  Math.random() * 1.8 + 1.2,
        phase: Math.random() * Math.PI * 2,
        speed: 0.018 + Math.random() * 0.016,
        color: Math.random() > 0.65 ? 1 : 0  // 0=cyan 1=violet
      });
    }
  }

  spawnPkt(a, b) {
    this.pkts.push({
      x: a.x, y: a.y,
      tx: b.x, ty: b.y,
      p: 0,
      sp: 0.008 + Math.random() * 0.014,
      c: a.color
    });
  }

  drawNode(n) {
    const ctx = this.ctx;
    n.phase += n.speed;
    const g = (Math.sin(n.phase) + 1) / 2;

    const color = n.color === 0
      ? `rgba(0,212,255,${0.5 + g * 0.4})`
      : `rgba(124,58,237,${0.5 + g * 0.4})`;

    // Glow halo
    const grad = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 5);
    grad.addColorStop(0, n.color === 0
      ? `rgba(0,212,255,${0.18 + g * 0.12})`
      : `rgba(124,58,237,${0.18 + g * 0.12})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.beginPath();
    ctx.arc(n.x, n.y, n.r * 5, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();

    // Core
    ctx.beginPath();
    ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }

  drawEdge(a, b, dist) {
    const ctx  = this.ctx;
    const opac = (1 - dist / this.DIST) * 0.35;
    const grad = ctx.createLinearGradient(a.x, a.y, b.x, b.y);
    grad.addColorStop(0, `rgba(0,212,255,${opac})`);
    grad.addColorStop(0.5, `rgba(124,58,237,${opac * 0.7})`);
    grad.addColorStop(1, `rgba(0,212,255,${opac})`);
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.strokeStyle = grad;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  run() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Move + draw nodes
    for (let i = 0; i < this.nodes.length; i++) {
      const n = this.nodes[i];
      n.x += n.vx;
      n.y += n.vy;

      // Mouse attraction
      if (this.mouse.x !== null) {
        const dx = this.mouse.x - n.x;
        const dy = this.mouse.y - n.y;
        const d  = Math.hypot(dx, dy);
        if (d < 180) { n.x += dx * 0.012; n.y += dy * 0.012; }
      }

      // Walls
      if (n.x < 0 || n.x > this.canvas.width)  n.vx *= -1;
      if (n.y < 0 || n.y > this.canvas.height)  n.vy *= -1;
      n.x = Math.max(0, Math.min(this.canvas.width,  n.x));
      n.y = Math.max(0, Math.min(this.canvas.height, n.y));

      // Edges to neighbors
      for (let j = i + 1; j < this.nodes.length; j++) {
        const m  = this.nodes[j];
        const dx = m.x - n.x;
        const dy = m.y - n.y;
        const d  = Math.hypot(dx, dy);
        if (d < this.DIST) {
          this.drawEdge(n, m, d);
          if (Math.random() < 0.0006) this.spawnPkt(n, m);
        }
      }

      this.drawNode(n);
    }

    // Data packets
    this.pkts = this.pkts.filter(pk => pk.p < 1);
    this.pkts.forEach(pk => {
      pk.p += pk.sp;
      const x  = pk.x + (pk.tx - pk.x) * pk.p;
      const y  = pk.y + (pk.ty - pk.y) * pk.p;
      const al = 1 - pk.p;
      ctx.beginPath();
      ctx.arc(x, y, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = pk.c === 0
        ? `rgba(0,212,255,${al})`
        : `rgba(167,139,250,${al})`;
      ctx.fill();
    });

    this.raf = requestAnimationFrame(() => this.run());
  }

  destroy() {
    cancelAnimationFrame(this.raf);
    window.removeEventListener('resize', this.resize);
  }
}


/* ══════════════════════════════════════
   TYPEWRITER EFFECT
══════════════════════════════════════ */
function initTypewriter() {
  const el    = document.getElementById('typewriter');
  if (!el) return;
  const roles = [
    'Data Scientist',
    'ML Engineer',
    'Python Developer',
    'Automation Specialist',
    'Analytics Engineer'
  ];
  let ri = 0, ci = 0, deleting = false;

  function tick() {
    const word = roles[ri];
    if (!deleting) {
      el.textContent = word.slice(0, ++ci);
      if (ci === word.length) {
        deleting = true;
        setTimeout(tick, 1800);
        return;
      }
      setTimeout(tick, 70);
    } else {
      el.textContent = word.slice(0, --ci);
      if (ci === 0) {
        deleting = false;
        ri = (ri + 1) % roles.length;
        setTimeout(tick, 400);
        return;
      }
      setTimeout(tick, 38);
    }
  }
  setTimeout(tick, 800);
}


/* ══════════════════════════════════════
   NAVIGATION
══════════════════════════════════════ */
function initNav() {
  const nav   = document.getElementById('nav');
  const burger= document.getElementById('hamburger');
  const links = document.getElementById('nav-links');
  const allNL = document.querySelectorAll('.nl');

  // Scroll effect
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 40);
    // Active link spy
    const sections = ['home','about','skills','projects','experience','education','contact'];
    let active = 'home';
    sections.forEach(id => {
      const el = document.getElementById(id);
      if (el && window.scrollY >= el.offsetTop - 120) active = id;
    });
    allNL.forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === `#${active}`);
    });
  }, { passive: true });

  // Mobile toggle
  burger.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    burger.classList.toggle('open', open);
  });

  // Close on nav link click
  links.addEventListener('click', e => {
    if (e.target.classList.contains('nl')) {
      links.classList.remove('open');
      burger.classList.remove('open');
    }
  });

  // Smooth scroll for all anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}


/* ══════════════════════════════════════
   SCROLL REVEAL
══════════════════════════════════════ */
function initReveal() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        en.target.classList.add('visible');
        obs.unobserve(en.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
}


/* ══════════════════════════════════════
   COUNTER ANIMATION
══════════════════════════════════════ */
function animateCounter(el) {
  const target = parseInt(el.dataset.target, 10);
  const dur    = 1600;
  const start  = performance.now();

  function step(now) {
    const pct = Math.min((now - start) / dur, 1);
    const ease = 1 - Math.pow(1 - pct, 3); // ease-out cubic
    el.textContent = Math.floor(ease * target);
    if (pct < 1) requestAnimationFrame(step);
    else el.textContent = target;
  }
  requestAnimationFrame(step);
}

function initCounters() {
  const counters = document.querySelectorAll('.hstat-n, .acnt-n');
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        animateCounter(en.target);
        obs.unobserve(en.target);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(el => obs.observe(el));
}


/* ══════════════════════════════════════
   SKILL RINGS
══════════════════════════════════════ */
function initSkillRings() {
  const C = 2 * Math.PI * 52; // circumference for r=52

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const container = en.target.closest('.sr-item') || en.target;
      const prog = container.querySelector('.sr-prog');
      const pctEl= container.querySelector('.sr-pct');
      if (!prog || !pctEl) return;

      const pct = parseInt(prog.dataset.pct, 10);
      prog.style.strokeDasharray  = C;
      prog.style.strokeDashoffset = C;

      // Trigger animation
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          prog.style.strokeDashoffset = C * (1 - pct / 100);
        });
      });

      // Number count-up
      const dur   = 1500;
      const start = performance.now();
      (function countUp(now) {
        const p = Math.min((now - start) / dur, 1);
        const e = 1 - Math.pow(1 - p, 3);
        pctEl.textContent = Math.round(e * pct) + '%';
        if (p < 1) requestAnimationFrame(countUp);
      })(start);

      obs.unobserve(container);
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.sr-prog').forEach(el => {
    el.style.strokeDasharray  = C;
    el.style.strokeDashoffset = C;
    obs.observe(el);
  });
}


/* ══════════════════════════════════════
   PROJECT FILTER
══════════════════════════════════════ */
function initFilter() {
  const btns  = document.querySelectorAll('.fb');
  const cards = document.querySelectorAll('.proj-card');

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const f = btn.dataset.filter;

      cards.forEach(card => {
        const match = f === 'all' || card.dataset.cat === f;
        if (match) {
          card.style.display = '';
          card.style.animation = 'fadeUp 0.4s ease both';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}


/* ══════════════════════════════════════
   CONTACT FORM
══════════════════════════════════════ */
function initContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  // EmailJS Initialize (Apni Public Key yahan daalein)
  emailjs.init("PqacPdPtvsuetRqmJ"); 

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = document.getElementById('submit-btn');
    const txt = btn.querySelector('.btn-txt');
    const load = btn.querySelector('.btn-load');
    const msg = document.getElementById('form-msg');

    txt.style.display = 'none';
    load.style.display = 'inline-flex';
    btn.disabled = true;
    msg.className = 'form-msg';

    // EmailJS Send
    try {
      await emailjs.send("service_kh5ncfh", "template_u4ax3ee", {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        subject: document.getElementById('subject').value,
        message: document.getElementById('message').value
      });

      msg.textContent = "Message sent successfully! 🚀";
      msg.className = 'form-msg success';
      form.reset();
    } catch (error) {
      console.error("EmailJS Error:", error);
      msg.textContent = 'Failed to send — please try again later.';
      msg.className = 'form-msg error';
    } finally {
      txt.style.display = 'inline-flex';
      load.style.display = 'none';
      btn.disabled = false;
    }
  });
}
/* ══════════════════════════════════════
   PROJECT CARD TILT
══════════════════════════════════════ */
function initTilt() {
  document.querySelectorAll('.proj-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width  - 0.5;
      const y = (e.clientY - rect.top)  / rect.height - 0.5;
      card.style.transform = `translateY(-6px) rotateX(${-y * 6}deg) rotateY(${x * 6}deg)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });
}


/* ══════════════════════════════════════
   HERO PARALLAX (subtle)
══════════════════════════════════════ */
function initParallax() {
  const hero = document.querySelector('.hero-body');
  if (!hero) return;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y < window.innerHeight) {
      hero.style.transform = `translateY(${y * 0.18}px)`;
      hero.style.opacity   = 1 - (y / window.innerHeight) * 1.2;
    }
  }, { passive: true });
}


/* ══════════════════════════════════════
   CURSOR GLOW (desktop only)
══════════════════════════════════════ */
function initCursorGlow() {
  if (window.matchMedia('(pointer: coarse)').matches) return;
  const glow = document.createElement('div');
  glow.style.cssText = `
    position:fixed; pointer-events:none; z-index:9999;
    width:400px; height:400px;
    border-radius:50%;
    background:radial-gradient(circle, rgba(0,212,255,0.06) 0%, transparent 70%);
    transform:translate(-50%,-50%);
    transition: left 0.08s, top 0.08s;
  `;
  document.body.appendChild(glow);
  document.addEventListener('mousemove', e => {
    glow.style.left = e.clientX + 'px';
    glow.style.top  = e.clientY + 'px';
  });
}


/* ══════════════════════════════════════
   ENTRY POINT
══════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  // Neural network canvas
  const canvas = document.getElementById('neural-canvas');
  if (canvas) new NeuralNet(canvas);

  // Features
  initTypewriter();
  initNav();
  initReveal();
  initCounters();
  initSkillRings();
  initFilter();
  initContactForm();
  initTilt();
  initParallax();
  initCursorGlow();

  // Subtle entrance: hero stats
  setTimeout(() => {
    document.querySelectorAll('.hstat-n[data-target]').forEach(el => {
      animateCounter(el);
    });
  }, 600);
});

window.addEventListener('scroll', () => {
  const scrollCue = document.querySelector('.hero-scroll');
  // 500 represents the number of pixels scrolled down before it hides. 
  // You can adjust this to match the height of your hero section!
  if (window.scrollY > 500) {
    scrollCue.classList.add('hidden');
  } else {
    scrollCue.classList.remove('hidden');
  }
});
