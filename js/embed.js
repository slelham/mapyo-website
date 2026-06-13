(function () {
  var params = new URLSearchParams(window.location.search);
  var isEmbed = params.has('embed') || window.self !== window.top;
  if (!isEmbed) return;

  document.documentElement.classList.add('is-embed');
  window.MAPYO_EMBED = true;

  var style = document.createElement('style');
  style.textContent =
    'html.is-embed,html.is-embed body{overflow-y:auto!important}' +
    'html.is-embed .fade-up{opacity:1!important;transform:none!important}';
  document.head.appendChild(style);

  function revealContent() {
    document.querySelectorAll('.fade-up').forEach(function (el) {
      el.classList.add('visible');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', revealContent);
  } else {
    revealContent();
  }

  window.addEventListener('load', revealContent);
})();