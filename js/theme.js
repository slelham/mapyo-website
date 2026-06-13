(function () {
  var STORAGE_KEY = 'mapyo-theme';
  var MODES = ['auto', 'light', 'dark'];

  function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function getPreference() {
    var stored = localStorage.getItem(STORAGE_KEY);
    return MODES.indexOf(stored) !== -1 ? stored : 'auto';
  }

  function resolveTheme(preference) {
    return preference === 'auto' ? getSystemTheme() : preference;
  }

  function apply() {
    var preference = getPreference();
    var resolved = resolveTheme(preference);
    document.documentElement.setAttribute('data-theme', resolved);
    document.documentElement.setAttribute('data-theme-mode', preference);
  }

  function setPreference(preference) {
    localStorage.setItem(STORAGE_KEY, preference);
    apply();
    updateToggleUi();
  }

  function cyclePreference() {
    var current = getPreference();
    var next = MODES[(MODES.indexOf(current) + 1) % MODES.length];
    setPreference(next);
  }

  function watchSystem() {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    var handler = function () {
      if (getPreference() === 'auto') apply();
    };
    if (mq.addEventListener) mq.addEventListener('change', handler);
    else if (mq.addListener) mq.addListener(handler);
  }

  function modeLabel(mode) {
    if (mode === 'light') return 'Light mode';
    if (mode === 'dark') return 'Dark mode';
    return 'Auto mode (follows system)';
  }

  function updateToggleUi() {
    var btn = document.getElementById('themeToggle');
    if (!btn) return;
    var mode = getPreference();
    btn.setAttribute('aria-label', 'Theme: ' + modeLabel(mode));
    btn.title = modeLabel(mode) + ' — click to change';
  }

  function setupToggle() {
    var navInner = document.querySelector('.nav__inner');
    if (!navInner || document.getElementById('themeToggle')) {
      updateToggleUi();
      return;
    }

    var navToggle = document.getElementById('navToggle');
    var actions = document.createElement('div');
    actions.className = 'nav__actions';

    var btn = document.createElement('button');
    btn.className = 'theme-toggle';
    btn.id = 'themeToggle';
    btn.type = 'button';
    btn.innerHTML = `
      <svg class="theme-toggle__auto" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16v12H4V6Zm2 2v8h12V8H6Zm10 10h2v2h-2v-2ZM4 18H2v2h2v-2Zm16 0h2v2h-2v-2ZM4 2H2v2h2V2Zm16 0h2v2h-2V2Z"/></svg>
      <svg class="theme-toggle__sun" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 17.5a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11Zm0-14.5a1 1 0 0 1 1 1v1.1a1 1 0 1 1-2 0V4a1 1 0 0 1 1-1Zm0 17.4a1 1 0 0 1 1 1V21a1 1 0 1 1-2 0v-1.1a1 1 0 0 1 1-1ZM4 12a1 1 0 0 1 1-1h1.1a1 1 0 1 1 0 2H5a1 1 0 0 1-1-1Zm14.9 0a1 1 0 0 1 1-1H21a1 1 0 1 1 0 2h-1.1a1 1 0 0 1-1-1ZM6.05 6.05a1 1 0 0 1 1.41 0l.78.78a1 1 0 1 1-1.41 1.41l-.78-.78a1 1 0 0 1 0-1.41Zm11.31 11.31a1 1 0 0 1 1.41 0l.78.78a1 1 0 0 1-1.41 1.41l-.78-.78a1 1 0 0 1 0-1.41ZM6.05 17.95a1 1 0 0 1 0-1.41l.78-.78a1 1 0 1 1 1.41 1.41l-.78.78a1 1 0 0 1-1.41 0Zm11.31-11.31a1 1 0 0 1 0-1.41l.78-.78a1 1 0 1 1 1.41 1.41l-.78.78a1 1 0 0 1-1.41 0Z"/></svg>
      <svg class="theme-toggle__moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 14.5A7.5 7.5 0 0 1 9.5 3.2a6 6 0 1 0 11.5 11.3Z"/></svg>
    `;

    btn.addEventListener('click', cyclePreference);

    actions.appendChild(btn);
    if (navToggle) {
      navInner.insertBefore(actions, navToggle);
      actions.appendChild(navToggle);
    } else {
      navInner.appendChild(actions);
    }

    updateToggleUi();
  }

  apply();
  watchSystem();

  window.MapyoTheme = {
    apply: apply,
    cyclePreference: cyclePreference,
    setupToggle: setupToggle,
    getPreference: getPreference,
  };
})();