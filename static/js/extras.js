// Cursor light, EmailJS contact form, chat assistant
(() => {
  const g = document.getElementById('glow');
  if (!g || !matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches, [soft, ring] = g.children;
  let x = innerWidth / 2, y = innerHeight / 2, sx = x, sy = y, rx = x, ry = y;
  
  g.hidden = false;
  
  addEventListener('pointermove', e => {
    x = e.clientX; y = e.clientY; g.classList.add('on');
    g.classList.toggle('dark', !!e.target.closest('.hero,.dark,.foot,.bar,.chat,.chat-open'));
    g.classList.toggle('hot', !!e.target.closest('a,button,summary,input,textarea,label'));
  }, { passive: true });
  
  document.documentElement.addEventListener('pointerleave', () => g.classList.remove('on'));
  
  (function tick() {
    sx += (x - sx) * (calm ? 1 : .12); sy += (y - sy) * (calm ? 1 : .12);
    rx += (x - rx) * (calm ? 1 : .3); ry += (y - ry) * (calm ? 1 : .3);
    
    // The ultimate fix: translate(-50%, -50%) keeps it perfectly centered always
    soft.style.transform = `translate3d(${sx}px, ${sy}px, 0) translate(-50%, -50%)`;
    ring.style.transform = `translate3d(${rx}px, ${ry}px, 0) translate(-50%, -50%)`;
    
    requestAnimationFrame(tick);
  })();
})();
(() => {
  const f = document.getElementById('contact-form');
  if (!f) return;
  const st = f.querySelector('.status'), btn = f.querySelector('button[type=submit]'), d = f.dataset;
  const say = (t, c) => { st.textContent = t; st.className = 'status ' + (c || ''); };
  f.addEventListener('submit', async e => {
    e.preventDefault();
    const v = Object.fromEntries(new FormData(f));
    if (v.website) return; // honeypot
    if (!v.from_name.trim() || !/^\S+@\S+\.\S+$/.test(v.from_email) || v.message.trim().length < 10)
      return say('Please add your name, a valid email and a message of at least 10 characters.', 'err');
    if (!d.service || !d.template || !d.key) return say('The form is not connected yet. Please use the email link below.', 'err');
    btn.disabled = true; say('Sending...');
    try {
      const r = await fetch('https://api.emailjs.com/api/v1.0/email/send', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ service_id: d.service, template_id: d.template, user_id: d.key,
          template_params: { from_name: v.from_name, from_email: v.from_email, reply_to: v.from_email, message: v.message } })
      });
      if (!r.ok) throw new Error(await r.text());
      f.reset(); say('Message sent. Thank you, Asad will reply by email soon.', 'ok');
    } catch (err) { say('Sorry, that did not send. Please try again or use the email link below.', 'err'); }
    btn.disabled = false;
  });
})();

(() => {
  const $ = id => document.getElementById(id);
  const box = $('chat'), log = $('chat-log'), input = $('chat-input'), open = $('chat-open'), tips = $('chat-tips');
  if (!box) return;
  const hist = [];
  let busy = false;

  function toggle(on) {
    box.hidden = !on; open.hidden = on; open.setAttribute('aria-expanded', on);
    if (on) { if (!log.children.length) hello(); input.focus(); } else open.focus();
  }
  function goContact() {
    toggle(false);
    const c = $('contact');
    if (!c) { location.href = '/#contact'; return; }
    c.scrollIntoView({ behavior: 'smooth' });
    setTimeout(() => $('contact-form').elements.from_name.focus({ preventScroll: true }), 700);
  }
  function add(role, text, d = {}) {
    const m = document.createElement('div'), p = document.createElement('p');
    m.className = 'msg ' + role; p.textContent = text; m.append(p);
    if (d.sources && d.sources.length) {
      const s = document.createElement('div'); s.className = 'src';
      d.sources.forEach(x => { const a = document.createElement('a'); a.href = x.url; a.textContent = x.title; if (/^https?:/.test(x.url)) { a.target = '_blank'; a.rel = 'noopener'; } s.append(a); });
      m.append(s);
    }
    if (d.action === 'contact') {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'go'; b.textContent = 'Open the contact form'; b.onclick = goContact; m.append(b);
    }
    log.append(m); log.scrollTop = log.scrollHeight; return m;
  }
  function hello() {
    add('bot', "Hi, I'm the assistant on Asad's portfolio. Ask me about his projects, skills and experience, or how to get in touch.");
    ['What has Asad built?', 'Tell me about his AI agent work', 'Which tools does he use?', 'How can I contact him?'].forEach(t => {
      const b = document.createElement('button'); b.type = 'button'; b.textContent = t; b.onclick = () => send(t); tips.append(b);
    });
  }
  async function send(text) {
    text = text.trim();
    if (!text || busy) return;
    busy = true; tips.hidden = true; input.value = '';
    add('user', text); const wait = add('bot typing', 'Thinking...');
    try {
      const r = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text, history: hist.slice(-6) }) });
      const d = await r.json(); wait.remove();
      add('bot', d.reply || 'Something went wrong. Please try again.', d);
      hist.push({ role: 'user', content: text }, { role: 'assistant', content: d.reply || '' });
    } catch (e) { wait.remove(); add('bot', 'I could not reach the server. Please try again, or use the contact form.', { action: 'contact' }); }
    busy = false; input.focus();
  }
  open.onclick = () => toggle(true);
  $('chat-close').onclick = () => toggle(false);
  $('chat-form').onsubmit = e => { e.preventDefault(); send(input.value); };
  addEventListener('keydown', e => { if (e.key === 'Escape' && !box.hidden) toggle(false); });
})();
