document.addEventListener('DOMContentLoaded', () => {
  const nav = document.getElementById('nav');
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  const sections = document.querySelectorAll('section, header');
  const navAnchors = document.querySelectorAll('.nav__links a');

  initThemeToggle();

  // Sticky nav background on scroll
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  }, { passive: true });

  // Mobile menu toggle
  navToggle.addEventListener('click', () => {
    navToggle.classList.toggle('open');
    navLinks.classList.toggle('open');
  });

  // Close mobile menu on link click
  navAnchors.forEach(link => {
    link.addEventListener('click', () => {
      navToggle.classList.remove('open');
      navLinks.classList.remove('open');
    });
  });

  // Active nav link highlighting
  const observerOptions = { rootMargin: '-30% 0px -60% 0px' };
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        navAnchors.forEach(a => {
          a.classList.toggle('active', a.getAttribute('href') === `#${id}`);
        });
      }
    });
  }, observerOptions);

  sections.forEach(s => {
    if (s.id) sectionObserver.observe(s);
  });

  // Fade-up scroll animations
  const fadeEls = document.querySelectorAll('.fade-up');
  const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 80);
        fadeObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  fadeEls.forEach(el => fadeObserver.observe(el));

  // Study group accordions
  document.querySelectorAll('.study-group__header').forEach(header => {
    header.addEventListener('click', () => {
      const expanded = header.getAttribute('aria-expanded') === 'true';
      header.setAttribute('aria-expanded', !expanded);
    });
  });

  // Worksheet tabs
  const tabs = document.querySelectorAll('.worksheet-tab');
  const panels = document.querySelectorAll('.worksheet-panel');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;

      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById(`tab-${target}`).classList.add('active');
    });
  });
});

function initThemeToggle() {
  const navInner = document.querySelector('.nav__inner');
  if (!navInner || document.getElementById('themeToggle')) return;

  const navToggle = document.getElementById('navToggle');
  const actions = document.createElement('div');
  actions.className = 'nav__actions';

  const btn = document.createElement('button');
  btn.className = 'theme-toggle';
  btn.id = 'themeToggle';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Toggle dark mode');
  btn.title = 'Toggle dark mode';
  btn.innerHTML = `
    <svg class="theme-toggle__sun" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 17.5a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11Zm0-14.5a1 1 0 0 1 1 1v1.1a1 1 0 1 1-2 0V4a1 1 0 0 1 1-1Zm0 17.4a1 1 0 0 1 1 1V21a1 1 0 1 1-2 0v-1.1a1 1 0 0 1 1-1ZM4 12a1 1 0 0 1 1-1h1.1a1 1 0 1 1 0 2H5a1 1 0 0 1-1-1Zm14.9 0a1 1 0 0 1 1-1H21a1 1 0 1 1 0 2h-1.1a1 1 0 0 1-1-1ZM6.05 6.05a1 1 0 0 1 1.41 0l.78.78a1 1 0 1 1-1.41 1.41l-.78-.78a1 1 0 0 1 0-1.41Zm11.31 11.31a1 1 0 0 1 1.41 0l.78.78a1 1 0 0 1-1.41 1.41l-.78-.78a1 1 0 0 1 0-1.41ZM6.05 17.95a1 1 0 0 1 0-1.41l.78-.78a1 1 0 1 1 1.41 1.41l-.78.78a1 1 0 0 1-1.41 0Zm11.31-11.31a1 1 0 0 1 0-1.41l.78-.78a1 1 0 1 1 1.41 1.41l-.78.78a1 1 0 0 1-1.41 0Z"/></svg>
    <svg class="theme-toggle__moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 14.5A7.5 7.5 0 0 1 9.5 3.2a6 6 0 1 0 11.5 11.3Z"/></svg>
  `;

  actions.appendChild(btn);
  if (navToggle) {
    navInner.insertBefore(actions, navToggle);
    actions.appendChild(navToggle);
  } else {
    navInner.appendChild(actions);
  }

  btn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('mapyo-theme', next);
  });
}