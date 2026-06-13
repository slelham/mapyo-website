document.addEventListener('DOMContentLoaded', () => {
  const nav = document.getElementById('nav');
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  const sections = document.querySelectorAll('section, header');
  const navAnchors = document.querySelectorAll('.nav__links a');

  if (window.MapyoTheme) window.MapyoTheme.setupToggle();

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