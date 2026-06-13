(function () {
  var stored = localStorage.getItem('mapyo-theme');
  var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  var theme = stored === 'dark' || stored === 'light' ? stored : (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
})();